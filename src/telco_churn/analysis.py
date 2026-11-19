from __future__ import annotations

import pandas as pd


def segment_churn(frame: pd.DataFrame) -> pd.DataFrame:
    """Return churn counts, population, and rate across business segments."""
    dimensions = [
        "Contract", "PaymentMethod", "InternetService", "tenure_band",
        "OnlineSecurity", "TechSupport", "PaperlessBilling",
    ]
    data = frame.copy()
    data["tenure_band"] = pd.cut(
        data["tenure"], bins=[-1, 12, 24, 48, 60, 72],
        labels=["0-12 months", "13-24 months", "25-48 months", "49-60 months", "61-72 months"],
    ).astype("string")
    outputs = []
    for dimension in dimensions:
        grouped = data.groupby(dimension, dropna=False, observed=False)["Churn"].agg(
            customers="size", churned=lambda values: values.eq("Yes").sum()
        ).reset_index().rename(columns={dimension: "segment"})
        grouped.insert(0, "dimension", dimension)
        grouped["churn_rate"] = grouped["churned"] / grouped["customers"]
        outputs.append(grouped)
    return pd.concat(outputs, ignore_index=True)


def profile_metrics(frame: pd.DataFrame) -> dict[str, float | int]:
    churn_rate = frame["Churn"].eq("Yes").mean()
    return {
        "customers": int(len(frame)),
        "churned_customers": int(frame["Churn"].eq("Yes").sum()),
        "churn_rate": float(churn_rate),
        "monthly_charges": float(frame["MonthlyCharges"].sum()),
    }

