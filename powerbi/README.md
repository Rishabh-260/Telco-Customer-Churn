# Power BI report setup

Power BI Desktop was not found in the common installation paths in this environment. [`TelcoChurn.pbip`](TelcoChurn.pbip) is a source project starter with a TMDL import model and the core measures. The PBIP/PBIR/TMDL text formats are documented Power BI project formats. The visuals still need to be laid out in Desktop using the dashboard design below; save the finished report as PBIP and, if desired, as PBIX.

## Import data

1. Run the Python project to produce `reports/generated/customer_predictions.csv` and `reports/generated/segment_churn.csv`.
2. Open `TelcoChurn.pbip` in Power BI Desktop. If Desktop rejects the source starter, create a blank report and import the same CSV; use the TMDL file and measures as the model reference.
3. In `TelcoChurn.SemanticModel/definition/tables/customer_predictions.tmdl`, replace `PATH_TO_CUSTOMER_PREDICTIONS.csv` with the full path to the generated CSV, then refresh the model.
4. Keep `customerID` as text, `Churn` as text, `churn_probability` as decimal number, `predicted_churn` as whole number, and charge columns as decimal/currency.
5. Import [`theme.json`](theme.json) and use the measures in the model (also listed in [`measures.dax`](measures.dax)).

## Report pages

### Executive overview

- KPI cards: customers, observed churn rate, flagged customers, estimated monthly charges at risk.
- Clustered bar: churn rate and customer count by `Contract`.
- Bar: churn rate by `PaymentMethod`.
- Bar: estimated monthly charges at risk by contract.
- Slicers: `Contract`, `InternetService`, `PaymentMethod`, and `tenure`.

### Retention segments

- Matrix: contract × payment method with customer count, churn rate, and charge exposure.
- Bar charts: churn rates for `OnlineSecurity`, `TechSupport`, and `InternetService` categories.
- Scatter: `MonthlyCharges` by `tenure`, colored by actual churn; use prediction probability for the forward-looking view.
- Customer table: ID, contract, tenure, monthly charges, actual churn, probability, and predicted risk flag.

Use `churn_probability` for ranking and `predicted_churn` for the baseline 0.5 cutoff. The estimated charge measure is a prioritization proxy, not realized revenue loss.

