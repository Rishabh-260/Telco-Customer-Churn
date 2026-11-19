CREATE SCHEMA IF NOT EXISTS telco;

-- The Python loader refreshes these tables from cleaned source data and full-roster scores.
CREATE TABLE IF NOT EXISTS telco.customers (
    "customerID" TEXT PRIMARY KEY,
    gender TEXT,
    "SeniorCitizen" SMALLINT,
    "Partner" TEXT,
    "Dependents" TEXT,
    tenure INTEGER,
    "PhoneService" TEXT,
    "MultipleLines" TEXT,
    "InternetService" TEXT,
    "OnlineSecurity" TEXT,
    "OnlineBackup" TEXT,
    "DeviceProtection" TEXT,
    "TechSupport" TEXT,
    "StreamingTV" TEXT,
    "StreamingMovies" TEXT,
    "Contract" TEXT,
    "PaperlessBilling" TEXT,
    "PaymentMethod" TEXT,
    "MonthlyCharges" NUMERIC(10,2),
    "TotalCharges" NUMERIC(12,2),
    "Churn" TEXT CHECK ("Churn" IN ('Yes', 'No'))
);

CREATE TABLE IF NOT EXISTS telco.customer_predictions (
    "customerID" TEXT PRIMARY KEY,
    "Churn" TEXT CHECK ("Churn" IN ('Yes', 'No')),
    "Contract" TEXT,
    "PaymentMethod" TEXT,
    tenure INTEGER,
    "MonthlyCharges" NUMERIC(10,2),
    churn_probability NUMERIC(8,7) CHECK (churn_probability BETWEEN 0 AND 1),
    predicted_churn SMALLINT CHECK (predicted_churn IN (0, 1)),
    estimated_monthly_charges_at_risk NUMERIC(10,2),
    model_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_telco_customers_contract ON telco.customers ("Contract");
CREATE INDEX IF NOT EXISTS idx_telco_predictions_risk ON telco.customer_predictions (predicted_churn, churn_probability);

