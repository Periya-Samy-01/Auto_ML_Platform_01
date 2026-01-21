# Sample Data Folder

This folder contains CSV files for sample datasets that cannot be loaded from sklearn at runtime.

## Files to Add

Please add the following CSV files to this folder:

| Filename | Description | Rows | Columns |
|----------|-------------|------|---------|
| `titanic.csv` | Titanic passenger survival data | 891 | 12 |
| `boston_housing.csv` | Boston house prices (deprecated in sklearn) | 506 | 14 |
| `air_passengers.csv` | Monthly airline passengers 1949-1960 | 144 | 3 |
| `sms_spam.csv` | SMS spam/ham text messages | 5,572 | 2 |
| `imdb_reviews.csv` | Movie reviews with sentiment | 1,000 | 2 |
| `credit_fraud.csv` | Credit card fraud transactions (downsampled) | 10,000 | 31 |
| `synthetic_imbalanced.csv` | Synthetic imbalanced classification | 10,000 | 21 |
| `transactions_categorical.csv` | High-cardinality categorical data | 10,000 | 10 |

## CSV Format Requirements

### titanic.csv
Columns: PassengerId, Survived, Pclass, Name, Sex, Age, SibSp, Parch, Ticket, Fare, Cabin, Embarked

### boston_housing.csv
Columns: CRIM, ZN, INDUS, CHAS, NOX, RM, AGE, DIS, RAD, TAX, PTRATIO, B, LSTAT, MEDV

### air_passengers.csv
Columns: Month (YYYY-MM format), Year, Passengers

### sms_spam.csv
Columns: label (spam/ham), message

### imdb_reviews.csv
Columns: review, sentiment (positive/negative)

### credit_fraud.csv
Columns: Time, V1-V28, Amount, Class

### synthetic_imbalanced.csv
Columns: feature_0 through feature_19, target (0/1 with 95:5 ratio)

### transactions_categorical.csv
Columns: transaction_id, merchant_id, category, city, state, amount, hour, day_of_week, is_weekend, is_fraud
