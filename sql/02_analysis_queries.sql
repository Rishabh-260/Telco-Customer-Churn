-- Overall churn rate
SELECT COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE "Churn" = 'Yes') AS churned,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Churn" = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct
FROM telco.customers;

-- Contract churn rates
SELECT "Contract", COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE "Churn" = 'Yes') AS churned,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Churn" = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct
FROM telco.customers
GROUP BY "Contract"
ORDER BY churn_rate_pct DESC;

-- Payment method churn rates
SELECT "PaymentMethod", COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE "Churn" = 'Yes') AS churned,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Churn" = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct
FROM telco.customers
GROUP BY "PaymentMethod"
ORDER BY churn_rate_pct DESC;

-- Subscription churn rates
SELECT "InternetService", "OnlineSecurity", "TechSupport", COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE "Churn" = 'Yes') / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct
FROM telco.customers
GROUP BY "InternetService", "OnlineSecurity", "TechSupport"
ORDER BY churn_rate_pct DESC;

-- Prioritization proxy: monthly recurring charges of customers flagged by the LR model
SELECT COUNT(*) AS flagged_customers,
       ROUND(SUM("MonthlyCharges"), 2) AS estimated_monthly_charges_at_risk
FROM telco.customer_predictions
WHERE predicted_churn = 1;

-- At-risk charge exposure by contract
SELECT "Contract", COUNT(*) AS flagged_customers,
       ROUND(SUM("MonthlyCharges"), 2) AS estimated_monthly_charges_at_risk
FROM telco.customer_predictions
WHERE predicted_churn = 1
GROUP BY "Contract"
ORDER BY estimated_monthly_charges_at_risk DESC;

