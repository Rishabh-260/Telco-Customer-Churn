from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "Churn"
IDENTIFIER = "customerID"
RANDOM_STATE = 42
TEST_SIZE = 0.20
THRESHOLD = 0.50


@dataclass
class ModelResults:
    metrics: pd.DataFrame
    predictions: pd.DataFrame
    fitted_models: dict[str, Pipeline]
    scoring_model: Pipeline
    feature_importance: pd.DataFrame
    selected_model: str


def _preprocessor(frame: pd.DataFrame, scale_numeric: bool) -> ColumnTransformer:
    features = frame.drop(columns=[IDENTIFIER, TARGET], errors="ignore")
    numeric = features.select_dtypes(include=["number"]).columns.tolist()
    categorical = [column for column in features.columns if column not in numeric]
    numeric_steps: list[tuple[str, Any]] = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline(numeric_steps), numeric),
            ("categorical", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
            ]), categorical),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def _models(frame: pd.DataFrame) -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline([
            ("preprocessor", _preprocessor(frame, scale_numeric=True)),
            ("classifier", LogisticRegression(max_iter=2000, solver="liblinear", random_state=RANDOM_STATE)),
        ]),
        "random_forest": Pipeline([
            ("preprocessor", _preprocessor(frame, scale_numeric=False)),
            ("classifier", RandomForestClassifier(
                n_estimators=400, min_samples_leaf=2, class_weight="balanced_subsample",
                random_state=RANDOM_STATE, n_jobs=-1,
            )),
        ]),
    }


def train_compare_score(frame: pd.DataFrame) -> ModelResults:
    """Evaluate two models on one stratified split, then refit LR for roster scoring."""
    X = frame.drop(columns=[TARGET, IDENTIFIER])
    y = frame[TARGET].eq("Yes").astype("int8")
    indices = np.arange(len(frame))
    train_idx, test_idx = train_test_split(
        indices, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    models = _models(frame)
    metric_rows = []
    scored = frame.iloc[test_idx][[IDENTIFIER, "Churn", "MonthlyCharges"]].copy()
    scored["actual_churn"] = y_test.to_numpy()
    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        probabilities = pipeline.predict_proba(X_test)[:, 1]
        predictions = (probabilities >= THRESHOLD).astype("int8")
        tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
        metric_rows.append({
            "model": name,
            "roc_auc": roc_auc_score(y_test, probabilities),
            "recall": recall_score(y_test, predictions, zero_division=0),
            "precision": precision_score(y_test, predictions, zero_division=0),
            "f1": f1_score(y_test, predictions, zero_division=0),
            "accuracy": accuracy_score(y_test, predictions),
            "threshold": THRESHOLD,
            "true_negative": int(tn), "false_positive": int(fp),
            "false_negative": int(fn), "true_positive": int(tp),
            "test_rows": int(len(test_idx)),
        })
        if name == "logistic_regression":
            scored["churn_probability"] = probabilities
            scored["predicted_churn"] = predictions

    # Generate honest full-roster risk scores: each customer's score comes from a
    # fold model that did not train on that customer.
    selected = _models(frame)["logistic_regression"]
    oof_probabilities = cross_val_predict(
        _models(frame)["logistic_regression"], X, y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        method="predict_proba", n_jobs=1,
    )[:, 1]
    # Keep a full-data estimator as the reusable model artifact for future scoring.
    selected.fit(X, y)
    roster = frame[[IDENTIFIER, "Churn", "Contract", "PaymentMethod", "tenure", "MonthlyCharges"]].copy()
    roster["churn_probability"] = oof_probabilities
    roster["predicted_churn"] = (oof_probabilities >= THRESHOLD).astype("int8")
    roster["estimated_monthly_charges_at_risk"] = roster["MonthlyCharges"] * roster["predicted_churn"]
    roster["model_name"] = "logistic_regression_5fold_oof"

    classifier = selected.named_steps["classifier"]
    feature_names = selected.named_steps["preprocessor"].get_feature_names_out()
    importance = pd.DataFrame({
        "feature": feature_names,
        "importance": np.abs(classifier.coef_[0]),
        "direction": np.where(classifier.coef_[0] >= 0, "higher_churn_odds", "lower_churn_odds"),
    }).sort_values("importance", ascending=False, ignore_index=True)
    return ModelResults(
        metrics=pd.DataFrame(metric_rows), predictions=roster,
        fitted_models=models, scoring_model=selected, feature_importance=importance,
        selected_model="logistic_regression",
    )

