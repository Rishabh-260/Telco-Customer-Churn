from __future__ import annotations

from pathlib import Path

def log_experiments(results, metrics_path: Path, tracking_uri: str) -> None:
    import mlflow
    import mlflow.sklearn

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("telco-customer-churn")
    for row in results.metrics.to_dict(orient="records"):
        name = row["model"]
        with mlflow.start_run(run_name=name):
            mlflow.log_params({
                "model": name, "random_state": 42, "test_size": 0.2,
                "threshold": row["threshold"], "features_excluded": "customerID",
            })
            mlflow.log_metrics({key: float(value) for key, value in row.items() if key not in {"model", "threshold", "test_rows"}})
            mlflow.log_param("test_rows", int(row["test_rows"]))
            mlflow.log_artifact(str(metrics_path))
            mlflow.sklearn.log_model(results.fitted_models[name], artifact_path="model")

    with mlflow.start_run(run_name="logistic_regression_full_roster_scoring"):
        mlflow.log_params({"model": results.selected_model, "training_scope": "full_dataset", "threshold": 0.5})
        mlflow.sklearn.log_model(results.scoring_model, artifact_path="model")

