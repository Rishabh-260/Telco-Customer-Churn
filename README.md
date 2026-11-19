# Telecom Customer Churn and Retention Intelligence

An end-to-end analytics project for exploring customer churn, comparing churn classifiers, tracking experiments, and preparing customer risk data for PostgreSQL and Power BI.

## Project highlights

- Analyze customer churn by contract, payment method, tenure, and subscribed services.
- Train logistic regression and random forest classifiers on a stratified holdout split.
- Track model parameters, metrics, and artifacts with MLflow.
- Score the full customer base and estimate monthly charges associated with flagged customers.
- Load cleaned customers and churn scores into PostgreSQL and query retention segments.
- Use Power BI source assets and dashboard instructions in [`powerbi/`](powerbi/).

## Dataset

Download the **Telco Customer Churn** CSV from [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) and place it at:

```text
data/raw/Telco-Customer-Churn.csv
```

Kaggle may require sign-in. The same sample is available in IBM's [public repository](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv). The CSV is excluded from Git. See [`data/README.md`](data/README.md) for the expected columns and data handling notes.

## Quick start

Requires Python 3.10+ and PostgreSQL 14+ if database loading is needed.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

Run the Python analysis, model comparison, scoring, and local MLflow tracking:

```powershell
telco-churn --input data/raw/Telco-Customer-Churn.csv --output-dir reports/generated --tracking-uri file:./mlruns
```

The pipeline writes `cleaned_customers.csv`, `segment_churn.csv`, `model_metrics.csv`, `customer_predictions.csv`, and `feature_importance.csv` under the output directory. `customer_predictions.csv` is the Power BI import table.

To include PostgreSQL loading, set a connection string first. The loader creates and refreshes the project tables:

```powershell
$env:TELCO_DATABASE_URL = 'postgresql+psycopg://postgres:postgres@localhost:5432/telco_churn'
telco-churn --input data/raw/Telco-Customer-Churn.csv --output-dir reports/generated --tracking-uri file:./mlruns --load-postgres
```

Start the MLflow UI in a second terminal to inspect logged runs:

```powershell
mlflow ui --backend-store-uri ./mlruns
```

SQL schema and reusable analysis queries are in [`sql/`](sql/). Power BI setup is documented in [`powerbi/README.md`](powerbi/README.md).

## Evaluation design

- Target: `Churn` (`Yes` / `No`).
- Identifier `customerID` is retained for customer-level outputs and excluded from model features.
- One stratified 80/20 train/test split with random seed `42` gives 1,409 held-out records.
- Categorical inputs are one-hot encoded; numeric inputs are median-imputed and standardized for logistic regression. Both models use the same split and a 0.5 classification threshold.
- ROC-AUC and churn-class recall are reported alongside precision, F1, accuracy, and confusion-matrix counts. The figures from the project brief are comparison targets; the pipeline records actual measured results.
- For the complete roster exposure table, each customer's probability is generated out of fold so that customer's own churn label did not train its scoring model. A separate logistic regression pipeline is fit on the full dataset and logged for future scoring. Holdout metrics remain from the untouched test partition.
- “Monthly charges at risk” is a prioritization estimate: the sum of `MonthlyCharges` for customers whose predicted churn probability is at least 0.5. It is not a forecast of realized revenue loss.

## Repository map

```text
data/       dataset instructions and ignored local CSVs
powerbi/    dashboard model notes, measures, theme, and PBIP starter
reports/    generated exports (ignored by Git)
sql/        PostgreSQL DDL and segment queries
src/        data validation, analytics, modeling, persistence, CLI
```

