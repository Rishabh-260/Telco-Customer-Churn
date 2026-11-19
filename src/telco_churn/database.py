from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


def load_to_postgres(customers: pd.DataFrame, predictions: pd.DataFrame, url: str | None = None) -> None:
    """Replace project-owned customer and scoring tables in PostgreSQL."""
    connection_url = url or os.getenv("TELCO_DATABASE_URL")
    if not connection_url:
        raise ValueError("Set TELCO_DATABASE_URL or pass a database URL to load PostgreSQL tables")
    engine = create_engine(connection_url)
    schema_file = Path(__file__).resolve().parents[2] / "sql" / "01_schema.sql"
    statements = [part.strip() for part in schema_file.read_text(encoding="utf-8").split(";") if part.strip()]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
        connection.execute(text("TRUNCATE TABLE telco.customer_predictions, telco.customers"))
    customers.to_sql("customers", engine, schema="telco", if_exists="append", index=False, chunksize=1000)
    predictions.to_sql("customer_predictions", engine, schema="telco", if_exists="append", index=False, chunksize=1000)

