from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .analysis import profile_metrics, segment_churn
from .data import load_and_clean
from .database import load_to_postgres
from .mlflow_tracking import log_experiments
from .modeling import train_compare_score

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze, model, and score telecom customer churn.")
    parser.add_argument("--input", default="data/raw/Telco-Customer-Churn.csv", help="Path to source CSV")
    parser.add_argument("--output-dir", default="reports/generated", help="Directory for CSV outputs")
    parser.add_argument("--tracking-uri", default="file:./mlruns", help="MLflow tracking URI")
    parser.add_argument("--database-url", default=None, help="Optional SQLAlchemy PostgreSQL URL")
    parser.add_argument("--load-postgres", action="store_true", help="Load customer and prediction tables")
    parser.add_argument("--skip-mlflow", action="store_true", help="Skip MLflow logging")
    return parser


def run(input_path: str, output_dir: str, tracking_uri: str, load_postgres: bool = False,
        database_url: str | None = None, skip_mlflow: bool = False) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    customers = load_and_clean(input_path)
    customers.to_csv(output / "cleaned_customers.csv", index=False)
    profile = profile_metrics(customers)
    (output / "profile_metrics.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")

    segments = segment_churn(customers)
    segments.to_csv(output / "segment_churn.csv", index=False)

    results = train_compare_score(customers)
    metrics_path = output / "model_metrics.csv"
    results.metrics.to_csv(metrics_path, index=False)
    results.predictions.to_csv(output / "customer_predictions.csv", index=False)
    results.feature_importance.to_csv(output / "feature_importance.csv", index=False)

    if not skip_mlflow:
        log_experiments(results, metrics_path, tracking_uri)
    if load_postgres:
        load_to_postgres(customers, results.predictions, database_url)

    logging.info("Loaded %s customers; observed churn rate %.2f%%", profile["customers"], profile["churn_rate"] * 100)
    logging.info("Selected scoring model: %s", results.selected_model)
    logging.info("Wrote analysis and scores to %s", output.resolve())
    return {"profile": profile, "metrics": results.metrics, "output_dir": output}


def main() -> None:
    args = build_parser().parse_args()
    run(args.input, args.output_dir, args.tracking_uri, args.load_postgres, args.database_url, args.skip_mlflow)


if __name__ == "__main__":
    main()

