"""
Model Evaluation Topic Content
Lesson content for the Model Evaluation topic
"""

MODEL_EVALUATION_CONTENT = {
    "why-evaluation": {
        "content": """
## What is it?

**Model evaluation** is the process of measuring how well your model performs on unseen data. It's essential because a model that memorizes training data (overfitting) will fail in production. Proper evaluation ensures your model generalizes to new, real-world data.

Without evaluation, you're flying blind.

## How it Works

**The Core Problem:**
```
Training Performance ≠ Real-World Performance

Overfitting Example:
├── Training accuracy: 99%
├── Test accuracy: 65%
└── Model memorized training data, doesn't generalize!

Good Generalization:
├── Training accuracy: 88%
├── Test accuracy: 85%
└── Similar performance = model learned real patterns
```

**Evaluation Goals:**
```
├── Estimate real-world performance
├── Compare different models fairly
├── Detect overfitting early
├── Guide hyperparameter tuning
└── Build confidence before deployment
```

**Key Concepts:**
```
Bias-Variance Tradeoff:
├── High Bias (Underfitting):
│   └── Model too simple, misses patterns
├── High Variance (Overfitting):
│   └── Model too complex, memorizes noise
└── Goal: Balance between the two
```

## Example

**Fraud Detection Model Evaluation:**

```
Scenario: Detecting credit card fraud

Without Proper Evaluation:
├── Train on all data
├── Test on same data
├── "99% accuracy!" (meaningless)
└── Model memorized fraud patterns, fails on new fraud

With Proper Evaluation:
├── Split: 70% train, 15% validation, 15% test
├── Train on training set
├── Tune on validation set
├── Final evaluation on test set
├── Test accuracy: 94%
└── Confidence: Model will work in production

Reality Check:
├── 1% of transactions are fraud
├── Model that predicts "not fraud" always = 99% accurate
├── But catches 0% of fraud!
└── Need better metrics than accuracy
```

## When to Use

**Always Evaluate When:**
```
├── Deploying a model to production
├── Comparing multiple models
├── Tuning hyperparameters
├── Presenting results to stakeholders
└── Making business decisions based on predictions
```

**Evaluation Strategy:**
```
1. Hold out test set from the start
2. Never look at test set during development
3. Use validation set for:
   ├── Model selection
   ├── Hyperparameter tuning
   └── Feature engineering decisions
4. Final test set evaluation only once
5. Report honest, unbiased performance
```

## Key Takeaways

- **Training metrics lie**: High training score doesn't mean good model
- **Generalization matters**: How model performs on **new data**
- **Overfitting is the enemy**: Model memorizes instead of learns
- **Hold out test data**: Never train on test set
- **Choose right metrics**: Accuracy isn't always enough
- Evaluation should guide **all modeling decisions**
""",
        "key_points": [
            "Training performance doesn't equal real-world performance",
            "Overfitting means the model memorizes rather than generalizes",
            "Always evaluate on unseen data (test set)",
            "Choose metrics appropriate for your problem",
            "Evaluation should guide all modeling decisions"
        ]
    },
    
    "train-test-split": {
        "content": """
## What is it?

**Train/test/validation split** divides your data into separate sets for different purposes: training the model, tuning hyperparameters, and final evaluation. This prevents data leakage and gives an honest estimate of how the model will perform on new data.

The most fundamental practice in ML evaluation.

## How it Works

**Three-Way Split:**
```
Full Dataset (100%)
├── Training Set (60-70%)
│   └── Used to train the model
├── Validation Set (15-20%)
│   └── Used to tune hyperparameters
└── Test Set (15-20%)
    └── Final evaluation only (touch once!)
```

**Why Three Sets?**
```
Problem with just train/test:
├── You tune hyperparameters on test set
├── Test set performance guides your choices
├── Test set is no longer "unseen"
└── Performance estimate is biased (optimistic)

With validation set:
├── Tune on validation set
├── Test set remains truly unseen
└── Honest final performance estimate
```

**Splitting Strategies:**
```
Random Split:
├── Shuffle data, split by ratio
├── Good for most cases
└── May cause issues with time series

Stratified Split:
├── Maintain class proportions in each set
├── Essential for imbalanced data
└── Same 5% positive rate in train, val, test

Time-Based Split:
├── Train on past, test on future
├── Required for time series
└── Simulates real deployment scenario
```

## Example

**Customer Churn Prediction:**

```
Dataset: 100,000 customers
Churn Rate: 15%

Random Split (BAD for imbalanced):
├── Training: 70,000 (maybe 14% churn)
├── Validation: 15,000 (maybe 16% churn)
├── Test: 15,000 (maybe 15% churn)
└── Different proportions = unfair evaluation

Stratified Split (GOOD):
├── Training: 70,000 (exactly 15% churn)
├── Validation: 15,000 (exactly 15% churn)
├── Test: 15,000 (exactly 15% churn)
└── Same proportions = fair evaluation

Code Concept:
train, temp = stratified_split(data, test_size=0.3)
val, test = stratified_split(temp, test_size=0.5)

Result:
├── 70% training
├── 15% validation
└── 15% test
All with 15% churn rate
```

## When to Use

**Split Ratios:**

| Dataset Size | Suggested Split |
|--------------|-----------------|
| < 1,000 | Use cross-validation instead |
| 1,000-10,000 | 70/15/15 or 60/20/20 |
| 10,000-100,000 | 80/10/10 |
| > 100,000 | 90/5/5 or even 98/1/1 |

**When to Use Stratified:**
```
├── Classification problems
├── Imbalanced classes
├── Multi-class problems
└── When class proportions matter
```

**Time Series Data:**
```
NEVER shuffle time series data!
├── Train: 2020-2022 data
├── Validation: 2023 Q1-Q2
└── Test: 2023 Q3-Q4
├── Simulates predicting the future
```

## Key Takeaways

- **Three sets**: Train, Validation, Test (each has a purpose)
- **Never train on test data**: Keep it sacred
- **Stratified split**: Maintains class proportions
- **Time series**: Split by time, not random
- Larger datasets can use **smaller test percentages**
- Validation set for **tuning**, test set for **final evaluation**
""",
        "key_points": [
            "Three sets: Train (learn), Validation (tune), Test (evaluate)",
            "Never train or tune on test data—keep it unseen",
            "Use stratified split for imbalanced classification",
            "Time series data must be split by time, not randomly",
            "Larger datasets can use smaller test percentages"
        ]
    },
    
    "classification-metrics": {
        "content": """
## What is it?

**Classification metrics** measure how well your model predicts categories. Accuracy alone is often misleading, especially for imbalanced data. Common metrics include precision, recall, F1 score, and AUC-ROC, each capturing different aspects of performance.

Choose metrics that match your business goals.

## How it Works

**Core Metrics:**
```
Accuracy = (TP + TN) / Total
├── Percent of correct predictions
├── Misleading for imbalanced data
└── "99% accurate" can be useless

Precision = TP / (TP + FP)
├── Of predicted positives, how many correct?
├── High precision = few false alarms
└── Important when false positives are costly

Recall (Sensitivity) = TP / (TP + FN)
├── Of actual positives, how many found?
├── High recall = few missed positives
└── Important when missing positives is costly

F1 Score = 2 × (Precision × Recall) / (Precision + Recall)
├── Harmonic mean of precision and recall
├── Balances both metrics
└── Single number for comparison
```

**Where:**
```
TP = True Positives (correctly predicted positive)
TN = True Negatives (correctly predicted negative)
FP = False Positives (incorrectly predicted positive)
FN = False Negatives (incorrectly predicted negative)
```

## Example

**Disease Screening Model:**

```
Results:
├── 1000 patients tested
├── 50 actually have disease
├── Model predictions:
    ├── TP: 45 (caught 45 sick patients)
    ├── FP: 30 (30 healthy flagged as sick)
    ├── TN: 920 (920 healthy correctly cleared)
    └── FN: 5 (missed 5 sick patients!)

Metrics:
├── Accuracy = (45 + 920) / 1000 = 96.5%
├── Precision = 45 / (45 + 30) = 60%
├── Recall = 45 / (45 + 5) = 90%
└── F1 = 2 × (0.60 × 0.90) / (0.60 + 0.90) = 72%

Business Interpretation:
├── Recall 90%: Catches 90% of sick patients (good!)
├── Precision 60%: 40% of flagged patients aren't sick
├── Missing 10% of sick patients = 5 people
└── Is that acceptable? Depends on disease severity!
```

**Precision-Recall Tradeoff:**
```
Cannot maximize both simultaneously:
├── Higher threshold: ↑ Precision, ↓ Recall
├── Lower threshold: ↓ Precision, ↑ Recall
└── Choose based on business cost

Spam Filter: High precision (don't lose good emails)
Cancer Screening: High recall (don't miss cancer)
```

## When to Use

**Metric Selection Guide:**

| Scenario | Preferred Metric |
|----------|------------------|
| Balanced classes | Accuracy is okay |
| Imbalanced classes | F1, Precision, Recall |
| False positives costly | Precision |
| False negatives costly | Recall |
| Need single number | F1 Score |
| Compare across thresholds | AUC-ROC |

**AUC-ROC:**
```
Area Under ROC Curve:
├── Plots True Positive Rate vs False Positive Rate
├── Range 0 to 1 (0.5 = random guessing)
├── Threshold-independent
└── Good for comparing models overall
```

## Key Takeaways

- **Accuracy misleads** on imbalanced data
- **Precision**: How many predicted positives are correct?
- **Recall**: How many actual positives were found?
- **F1 Score**: Balance between precision and recall
- **AUC-ROC**: Overall performance across thresholds
- Choose metrics based on **business costs** of errors
""",
        "key_points": [
            "Accuracy is misleading for imbalanced data",
            "Precision measures false alarm rate",
            "Recall measures missed detection rate",
            "F1 Score balances precision and recall",
            "Choose metrics based on business costs of errors"
        ]
    },
    
    "regression-metrics": {
        "content": """
## What is it?

**Regression metrics** measure how close your predicted values are to actual values. Unlike classification, errors are continuous—predicting $500k when the house costs $450k is better than predicting $300k. Common metrics include MSE, RMSE, MAE, and R².

Different metrics penalize errors differently.

## How it Works

**Core Metrics:**
```
MAE (Mean Absolute Error):
MAE = (1/n) × Σ|y_actual - y_predicted|
├── Average of absolute errors
├── Easy to interpret (same units as target)
├── Treats all errors equally
└── Less sensitive to outliers

MSE (Mean Squared Error):
MSE = (1/n) × Σ(y_actual - y_predicted)²
├── Average of squared errors
├── Penalizes large errors more heavily
├── Units are squared (harder to interpret)
└── Sensitive to outliers

RMSE (Root Mean Squared Error):
RMSE = √MSE
├── Square root of MSE
├── Same units as target (interpretable)
├── Penalizes large errors more than MAE
└── Most common regression metric

R² (R-squared / Coefficient of Determination):
R² = 1 - (SS_residual / SS_total)
├── Proportion of variance explained
├── Range: -∞ to 1 (1 is perfect)
├── 0.8 means 80% of variance explained
└── Negative means worse than mean prediction
```

## Example

**House Price Prediction:**

```
Actual Prices: [300K, 400K, 350K, 500K, 280K]
Predictions:   [320K, 380K, 360K, 450K, 300K]
Errors:        [+20K, -20K, +10K, -50K, +20K]

Calculations:
MAE = (20 + 20 + 10 + 50 + 20) / 5 = $24,000
├── On average, off by $24K

MSE = (20² + 20² + 10² + 50² + 20²) / 5 = 660 (in K²)
├── Hard to interpret (units squared)

RMSE = √660 = $25,690
├── Weighted average error ~$26K
├── Higher than MAE due to $50K outlier

R² = 0.89
├── Model explains 89% of price variance
├── 11% unexplained (noise, missing features)
```

**MAE vs RMSE:**
```
Same errors: [10, 10, 10, 10, 10]
├── MAE = 10, RMSE = 10

Mixed errors: [2, 2, 2, 2, 42]
├── MAE = 10
├── RMSE = 18.8
└── RMSE penalizes the one big error more

Choose RMSE when large errors are worse
Choose MAE when all errors matter equally
```

## When to Use

**Metric Selection:**

| Metric | Use When |
|--------|----------|
| MAE | All errors equally important, outliers present |
| RMSE | Large errors are especially bad |
| R² | Want to explain variance, compare models |
| MAPE | Need percentage error (varying scales) |

**Interpreting R²:**
```
R² Values:
├── > 0.90: Excellent fit
├── 0.70 - 0.90: Good fit
├── 0.50 - 0.70: Moderate fit
├── < 0.50: Poor fit
└── < 0: Worse than predicting mean

Context matters:
├── R² = 0.60 for stock prices = impressive
├── R² = 0.60 for physics = poor
└── Compare to domain baselines
```

**Best Practices:**
```
├── Report multiple metrics
├── Include baseline comparison
├── Consider business context
├── Check residual distribution
└── RMSE and R² most common in practice
```

## Key Takeaways

- **MAE**: Average absolute error, robust to outliers
- **RMSE**: Penalizes large errors more heavily
- **R²**: Proportion of variance explained (0-1 scale)
- Choose based on **how much large errors matter**
- Always **compare to baseline** (mean prediction)
- Report **multiple metrics** for complete picture
""",
        "key_points": [
            "MAE: Average absolute error, treats all errors equally",
            "RMSE: Penalizes large errors more heavily",
            "R²: Proportion of variance explained (0 to 1)",
            "Choose based on how costly large errors are",
            "Report multiple metrics for complete picture"
        ]
    },
    
    "confusion-matrix": {
        "content": """
## What is it?

A **confusion matrix** is a table showing the counts of correct and incorrect predictions for each class. It reveals not just overall accuracy, but exactly where and how your model makes mistakes. Essential for understanding classification performance.

The foundation of all classification metrics.

## How it Works

**Binary Classification Matrix:**
```
                    Predicted
                 Negative  Positive
Actual  Negative    TN        FP
        Positive    FN        TP

Where:
├── TN: True Negative (correct rejection)
├── FP: False Positive (false alarm)
├── FN: False Negative (missed detection)
└── TP: True Positive (correct detection)
```

**Reading the Matrix:**
```
                Predicted
              No Fraud | Fraud
Actual  No Fraud  9850  |   50   → FP rate
        Fraud       30  |   70   → TP rate (Recall)
                    ↑
              FN rate

Diagonals = Correct predictions
Off-diagonals = Errors
```

**Metrics from Confusion Matrix:**
```
From the matrix above:
├── Accuracy = (9850 + 70) / 10000 = 99.2%
├── Precision = 70 / (70 + 50) = 58.3%
├── Recall = 70 / (70 + 30) = 70%
├── Specificity = 9850 / (9850 + 50) = 99.5%
└── F1 = 2 × (0.583 × 0.70) / (0.583 + 0.70) = 63.6%
```

## Example

**Email Spam Classifier:**

```
Confusion Matrix:
                 Predicted
              Not Spam | Spam
Actual Not Spam   850  |   20   
       Spam        30  |  100   

Total: 1000 emails

Analysis:
├── TN = 850: Legitimate emails correctly delivered
├── FP = 20: Legitimate emails wrongly sent to spam
├── FN = 30: Spam emails that reached inbox
├── TP = 100: Spam correctly filtered

Metrics:
├── Accuracy = (850 + 100) / 1000 = 95%
├── Precision = 100 / 120 = 83% (of spam folder, 83% is actually spam)
├── Recall = 100 / 130 = 77% (catches 77% of spam)

Business Impact:
├── 20 important emails go to spam (bad!)
├── 30 spam emails reach inbox (annoying)
└── Which is worse? Depends on user preference
```

**Multi-class Matrix:**
```
                    Predicted
              Cat | Dog | Bird
Actual  Cat   45  |  3  |  2    
        Dog    5  | 40  |  5
        Bird   2  |  3  | 45

Reading:
├── Cat correctly classified 45 times
├── Cat misclassified as Dog 3 times
├── Cat misclassified as Bird 2 times
├── Dog misclassified as Cat 5 times
└── ...and so on

Insights:
├── Model confused Cat↔Dog more than Cat↔Bird
└── Consider: What features distinguish cats from dogs?
```

## When to Use

**Confusion Matrix Reveals:**
```
├── Which classes are confused with each other
├── Whether errors are symmetric
├── If model is biased toward certain classes
├── The actual counts (not just percentages)
└── Foundation for all other metrics
```

**When to Deep Dive:**
```
├── Model accuracy seems good but stakeholders unhappy
├── Imbalanced classes present
├── Different error types have different costs
├── Need to explain mistakes to non-technical audience
└── Debugging model behavior
```

**Visualization Tips:**
```
├── Normalize by row to see recall per class
├── Normalize by column to see precision per class
├── Use heatmap colors for quick scanning
└── Always include actual counts somewhere
```

## Key Takeaways

- **Shows exact error patterns**, not just overall accuracy
- **Diagonal = correct**, off-diagonal = errors
- **All classification metrics** derived from it
- Reveals **which classes are confused** with each other
- Essential for **imbalanced data** analysis
- Use **heatmaps** for visualization in multi-class
""",
        "key_points": [
            "Shows exact counts of correct and incorrect predictions",
            "Diagonal elements are correct predictions",
            "All classification metrics can be derived from it",
            "Reveals which classes are confused with each other",
            "Essential for understanding imbalanced data performance"
        ]
    },
    
    "cross-validation": {
        "content": """
## What is it?

**Cross-validation** is a technique that uses multiple train/test splits to get a more reliable estimate of model performance. Instead of evaluating once, you evaluate multiple times on different subsets and average the results. This reduces the variance of your performance estimate.

Essential when you have limited data.

## How it Works

**K-Fold Cross-Validation:**
```
Split data into K equal parts (folds)

Fold 1: [Test] [Train] [Train] [Train] [Train] → Score 1
Fold 2: [Train] [Test] [Train] [Train] [Train] → Score 2
Fold 3: [Train] [Train] [Test] [Train] [Train] → Score 3
Fold 4: [Train] [Train] [Train] [Test] [Train] → Score 4
Fold 5: [Train] [Train] [Train] [Train] [Test] → Score 5

Final Score = Average(Score 1, 2, 3, 4, 5)
Std Dev shows score stability
```

**Common Variations:**
```
K-Fold (standard):
├── K=5 or K=10 most common
├── Each sample tested exactly once
└── Good for most cases

Stratified K-Fold:
├── Maintains class proportions in each fold
├── Essential for imbalanced data
└── Default for classification

Leave-One-Out (LOO):
├── K = N (each sample is a fold)
├── Maximum use of data
└── Computationally expensive

Repeated K-Fold:
├── Run K-fold multiple times with different splits
├── Even more stable estimate
└── 5×2 CV or 10×10 CV common
```

## Example

**Model Comparison with Cross-Validation:**

```
Dataset: 1000 samples
Task: Compare Random Forest vs Logistic Regression

Single Split Results:
├── RF: 85% accuracy
├── LR: 82% accuracy
└── RF wins? Maybe just lucky split...

5-Fold Cross-Validation Results:
Random Forest:
├── Fold 1: 84%
├── Fold 2: 87%
├── Fold 3: 83%
├── Fold 4: 86%
├── Fold 5: 85%
├── Mean: 85.0% ± 1.6%

Logistic Regression:
├── Fold 1: 83%
├── Fold 2: 84%
├── Fold 3: 82%
├── Fold 4: 84%
├── Fold 5: 83%
├── Mean: 83.2% ± 0.8%

Analysis:
├── RF: Higher mean but more variable
├── LR: Lower mean but more stable
├── Difference (1.8%) may not be significant
└── Consider: Is RF complexity worth 1.8%?
```

**Using CV for Hyperparameter Tuning:**
```
Goal: Find best 'max_depth' for Decision Tree

For max_depth in [3, 5, 7, 10, 15]:
    scores = cross_val_score(model, X, y, cv=5)
    print(f"depth={max_depth}: {scores.mean():.3f} ± {scores.std():.3f}")

Results:
├── depth=3:  0.78 ± 0.02
├── depth=5:  0.82 ± 0.02
├── depth=7:  0.84 ± 0.03  ← Best
├── depth=10: 0.83 ± 0.04
└── depth=15: 0.79 ± 0.05 (overfitting)
```

## When to Use

**Cross-Validation Benefits:**
```
├── More reliable performance estimate
├── Uses all data for both training and testing
├── Detects overfitting more reliably
├── Shows performance variance
└── Essential for small datasets
```

**Choosing K:**

| Dataset Size | Recommended K |
|--------------|--------------|
| < 100 | Leave-One-Out or K=10 |
| 100 - 1000 | K=10 |
| 1000 - 10000 | K=5 |
| > 10000 | K=5 or simple split |

**When NOT to Use:**
```
├── Time series data (use time-based split)
├── Very large datasets (computationally expensive)
├── When you need final test set (use nested CV)
└── Grouped data (use GroupKFold)
```

## Key Takeaways

- **K-Fold**: Split into K parts, each serves as test once
- **More reliable** than single train/test split
- **K=5 or 10** is most common
- Use **Stratified** for classification
- Report **mean ± std** for honest assessment
- Essential for **small datasets** and **model comparison**
""",
        "key_points": [
            "Uses multiple train/test splits for reliable evaluation",
            "K-Fold: Each sample tested exactly once",
            "K=5 or K=10 is most common",
            "Stratified K-Fold maintains class proportions",
            "Report mean ± std for honest performance assessment"
        ]
    }
}
