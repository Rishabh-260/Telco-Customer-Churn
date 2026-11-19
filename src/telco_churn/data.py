from __future__ import annotations

from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges", "Churn",
]
NUMERIC_COLUMNS = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]


def load_and_clean(path: str | Path) -> pd.DataFrame:
    """Read the source CSV, validate its shape, and normalize numeric/target fields."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(
            f"Dataset not found at {source}. See data/README.md for download instructions."
        )

    frame = pd.read_csv(source, dtype={"customerID": "string", "TotalCharges": "string"})
    missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {', '.join(missing)}")
    if frame["customerID"].isna().any() or frame["customerID"].duplicated().any():
        raise ValueError("customerID must be present and unique for each row")

    frame = frame[EXPECTED_COLUMNS].copy()
    for col in NUMERIC_COLUMNS:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["TotalCharges"] = frame["TotalCharges"].fillna(0.0)
    if frame[NUMERIC_COLUMNS].isna().any().any():
        bad = frame[NUMERIC_COLUMNS].isna().sum()
        raise ValueError(f"Unexpected missing numeric data: {bad[bad > 0].to_dict()}")

    frame["Churn"] = frame["Churn"].astype("string").str.strip()
    if not set(frame["Churn"].dropna().unique()).issubset({"Yes", "No"}):
        raise ValueError("Churn must contain only 'Yes' and 'No'")
    if frame["Churn"].isna().any():
        raise ValueError("Churn contains missing values")
    return frame

