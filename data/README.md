# Dataset setup

Download `Telco-Customer-Churn.csv` from [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) or the [IBM public copy](https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv) and save it as `data/raw/Telco-Customer-Churn.csv`.

Expected shape: 7,043 customer rows and 21 columns, including `customerID` and `Churn`. The raw file is ignored by Git.

`TotalCharges` is published as text and can contain blank strings for customers whose tenure is zero. The cleaning step coerces it to numeric and fills those blanks with 0, preserving all 7,043 rows. Customer IDs are checked for uniqueness.

