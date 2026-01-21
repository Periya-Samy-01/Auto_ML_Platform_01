"""
Feature Engineering Topic Content
Lesson content for the Feature Engineering topic
"""

FEATURE_ENGINEERING_CONTENT = {
    "what-is-feature-engineering": {
        "content": """
## What is it?

**Feature Engineering** is the process of transforming raw data into features that better represent the underlying problem, leading to improved model performance. It's often said that "applied ML is mostly feature engineering"—it can make a bigger difference than choosing the right algorithm.

Features are the input variables your model uses to make predictions.

## How it Works

Feature engineering involves several activities:

```
Feature Engineering Pipeline:
├── Data Cleaning
│   ├── Handle missing values
│   ├── Fix data types
│   └── Remove duplicates
├── Feature Transformation
│   ├── Scaling/Normalization
│   ├── Encoding categories
│   └── Log/Power transforms
├── Feature Creation
│   ├── Combine existing features
│   ├── Extract from dates, text, etc.
│   └── Domain-specific features
└── Feature Selection
    ├── Remove irrelevant features
    ├── Reduce dimensionality
    └── Keep most informative
```

**Why It Matters:**
```
Same Algorithm, Different Features:
├── Raw data: 65% accuracy
├── Basic preprocessing: 75% accuracy
├── Good feature engineering: 90% accuracy
└── The features make the difference!
```

## Example

**Predicting Flight Delays:**

```
Raw Data:
├── departure_time: "2024-03-15 14:30:00"
├── origin: "JFK"
├── destination: "LAX"
├── carrier: "AA"
└── scheduled_duration: 330 minutes

Engineered Features:
├── hour_of_day: 14 (afternoon = busier)
├── day_of_week: 5 (Friday = busier)
├── is_weekend: False
├── is_holiday: False
├── month: 3 (March)
├── route_popularity: "high"
├── carrier_delay_history: 0.15 (15% historical delay rate)
├── origin_congestion: 0.72 (busy airport index)
├── distance_category: "long_haul"
└── connection_risk: Low

Model Performance:
├── Without engineering: 62% accuracy
└── With engineering: 84% accuracy
```

## When to Use

**Feature Engineering is Critical When:**
- Raw data isn't in ideal format for algorithms
- Domain knowledge can add valuable information
- Simple models need help finding patterns
- Improving performance beyond algorithm tuning

**Feature Engineering Steps:**
```
1. Understand the data (EDA)
2. Clean and preprocess
3. Create domain-specific features
4. Encode and transform
5. Select best features
6. Iterate based on model performance
```

## Key Takeaways

- Feature engineering often matters **more than algorithm choice**
- Transforms raw data into **model-ready inputs**
- Includes **cleaning, transformation, creation, selection**
- **Domain knowledge** is your biggest advantage
- **Iterative process**: Create, test, refine
- 60-80% of ML project time is often spent here
""",
        "key_points": [
            "Feature engineering often matters more than algorithm choice",
            "Transforms raw data into model-ready inputs",
            "Includes cleaning, transformation, creation, and selection",
            "Domain knowledge is your biggest advantage",
            "60-80% of ML project time is often spent on features"
        ]
    },
    
    "missing-data": {
        "content": """
## What is it?

**Missing data** (null values, NaN) is one of the most common data quality issues. Most ML algorithms can't handle missing values directly, so you need strategies to deal with them: remove them, fill them in (imputation), or use algorithms that handle them natively.

The right approach depends on why data is missing.

## How it Works

**Types of Missing Data:**
```
├── MCAR (Missing Completely at Random)
│   └── No pattern to what's missing
├── MAR (Missing at Random)
│   └── Missing depends on other observed variables
└── MNAR (Missing Not at Random)
    └── Missing depends on the missing value itself
    └── Most problematic!
```

**Common Strategies:**
```
1. Deletion:
   ├── Drop rows with missing values
   ├── Drop columns with too many missing
   └── Risk: Losing valuable data

2. Imputation:
   ├── Mean/Median: Replace with average
   ├── Mode: For categorical (most frequent)
   ├── Forward/Backward Fill: Time series
   └── Model-based: Predict missing values

3. Indicator Features:
   ├── Add "is_missing" column
   └── Preserves information that value was missing
```

## Example

**Customer Data with Missing Values:**

```
Original Data:
Customer  Age   Income    City
1         35    50000     NYC
2         NaN   65000     LA
3         42    NaN       Chicago
4         28    45000     NaN
5         NaN   NaN       Boston

Strategy 1: Drop rows with any missing
├── Only Customer 1 remains
└── Lost 80% of data! (Bad)

Strategy 2: Mean/Mode Imputation
├── Age: Fill with mean = 35
├── Income: Fill with mean = 53333
├── City: Fill with mode = NYC
└── All data retained

Strategy 3: Smarter Imputation
├── Age: Group by city, use group median
├── Income: Predict from age + city
├── City: Keep as "Unknown" category
└── Preserves more relationships

With Missing Indicators:
Customer  Age   Income   City     Age_Missing  Income_Missing
1         35    50000    NYC      0            0
2         35    65000    LA       1            0
3         42    53333    Chicago  0            1
```

## When to Use

**Strategy Selection:**

| Strategy | Use When |
|----------|----------|
| Drop rows | Few missing, MCAR, lots of data |
| Mean/Median | MCAR, quick baseline needed |
| Mode | Categorical variables |
| Model-based | MAR, feature relationships exist |
| Indicator | Missingness might be informative |

**Best Practices:**
```
Handling Missing Data:
├── Understand WHY data is missing first
├── Visualize missing patterns
├── Start simple (mean/median)
├── Add missing indicators
├── Try model-based imputation
├── Compare results across strategies
└── Document your choices!
```

## Key Takeaways

- Most algorithms **can't handle missing values** directly
- Understand **why** data is missing before choosing strategy
- **Simple imputation** (mean/median) works for MCAR
- **Model-based imputation** preserves relationships better
- **Missing indicators** can capture valuable information
- Always **compare** different strategies' impact on model
""",
        "key_points": [
            "Most algorithms can't handle missing values directly",
            "Understand why data is missing before choosing a strategy",
            "Mean/median imputation is simple but may lose information",
            "Model-based imputation preserves feature relationships",
            "Missing indicators can capture informative patterns"
        ]
    },
    
    "encoding-categorical": {
        "content": """
## What is it?

**Categorical encoding** converts non-numeric categories (like "red", "blue", "green") into numbers that ML algorithms can process. Different encoding methods have different properties and are suited for different situations.

Choosing the right encoding can significantly impact model performance.

## How it Works

**Common Encoding Methods:**

```
1. Label Encoding:
   └── Assign integer to each category
   └── red=0, blue=1, green=2
   └── ⚠️ Implies ordering that doesn't exist

2. One-Hot Encoding:
   └── Create binary column per category
   └── red=[1,0,0], blue=[0,1,0], green=[0,0,1]
   └── No false ordering, but many columns

3. Ordinal Encoding:
   └── For truly ordered categories
   └── low=0, medium=1, high=2
   └── Preserves natural order

4. Target Encoding:
   └── Replace with mean target value
   └── NYC=0.75, LA=0.55 (if target is price)
   └── ⚠️ Risk of leakage, needs regularization
```

**High Cardinality Problem:**
```
One-hot encoding "Country" with 200 countries:
├── Creates 200 new columns
├── Sparse data, slow training
└── May cause overfitting

Solutions:
├── Group rare categories into "Other"
├── Use target encoding
├── Use embedding (deep learning)
└── Use frequency encoding
```

## Example

**Encoding "City" Feature:**

```
Original Data:
ID   City      Price
1    NYC       500
2    LA        400
3    NYC       550
4    Chicago   300
5    LA        420

Label Encoding:
ID   City_Label   Price
1    2            500
2    1            400
3    2            550
4    0            300
5    1            420
⚠️ Implies Chicago < LA < NYC (not meaningful!)

One-Hot Encoding:
ID   Chicago  LA  NYC   Price
1    0        0   1     500
2    0        1   0     400
3    0        0   1     550
4    1        0   0     300
5    0        1   0     420
✓ No false ordering

Target Encoding (mean price):
ID   City_TargetEnc   Price
1    525              500    # NYC mean
2    410              400    # LA mean
3    525              550
4    300              300    # Chicago mean
5    410              420
✓ Encodes predictive information
```

## When to Use

**Encoding Selection Guide:**

| Method | Best For | Avoid When |
|--------|----------|------------|
| One-Hot | Low cardinality (< 15 categories) | High cardinality |
| Label | Tree-based models only | Linear models |
| Ordinal | Truly ordered categories | No natural order |
| Target | High cardinality, tabular | Small data (leakage risk) |

**Best Practices:**
```
├── One-hot is safest default
├── Tree models handle label encoding
├── Use target encoding with cross-validation
├── Drop one column in one-hot (avoid dummy trap)
└── Test different encodings and compare
```

## Key Takeaways

- **Categorical variables** must be converted to numbers
- **One-hot encoding**: Safe, no false ordering, but many columns
- **Label encoding**: Compact, but implies false order (okay for trees)
- **Target encoding**: Powerful for high cardinality, risk of leakage
- **Ordinal encoding**: Only for naturally ordered categories
- Choice depends on **algorithm** and **cardinality**
""",
        "key_points": [
            "Categorical variables must be converted to numbers for ML",
            "One-hot encoding is safe but creates many columns",
            "Label encoding implies ordering—only suitable for tree models",
            "Target encoding is powerful but risks data leakage",
            "Choose encoding based on algorithm and cardinality"
        ]
    },
    
    "scaling": {
        "content": """
## What is it?

**Feature scaling** transforms features to similar ranges so that no single feature dominates due to its magnitude. Many algorithms (like gradient-based methods, KNN, SVM) are sensitive to feature scales, while tree-based methods are not.

Common methods: StandardScaler, MinMaxScaler, RobustScaler.

## How it Works

**Scaling Methods:**

```
1. StandardScaler (Z-score normalization):
   x_scaled = (x - mean) / std_dev
   └── Mean = 0, Std = 1
   └── Most common choice

2. MinMaxScaler:
   x_scaled = (x - min) / (max - min)
   └── Range [0, 1]
   └── Preserves zero values

3. RobustScaler:
   x_scaled = (x - median) / IQR
   └── Uses median and interquartile range
   └── Robust to outliers

4. MaxAbsScaler:
   x_scaled = x / |max|
   └── Range [-1, 1]
   └── Preserves sparsity
```

**Why Scaling Matters:**
```
Without scaling:
├── Feature A: Income ($30,000 - $150,000)
├── Feature B: Age (18 - 65)
└── Gradient descent dominated by income!

With StandardScaler:
├── Feature A: -2 to +2 (approximately)
├── Feature B: -2 to +2 (approximately)
└── Both features contribute equally
```

## Example

**Scaling Customer Features:**

```
Original Data:
Customer  Age   Income    Purchases
1         25    30000     5
2         35    80000     20
3         60    150000    8
4         22    25000     3

StandardScaler:
Customer  Age     Income    Purchases
1         -0.87   -0.73     -0.41
2         -0.07   0.27      1.47
3         1.94    1.67      0.00
4         -1.00   -0.94     -1.06

MinMaxScaler:
Customer  Age    Income    Purchases
1         0.08   0.04      0.12
2         0.34   0.44      1.00
3         1.00   1.00      0.29
4         0.00   0.00      0.00

Impact on KNN (K=2):
├── Without scaling: Dominated by income
│   └── Nearest to C1: C4 (similar income)
├── With scaling: Balanced features
│   └── Nearest to C1: C4 (genuinely similar overall)
```

## When to Use

**Algorithm Sensitivity:**

| Algorithm | Needs Scaling? |
|-----------|---------------|
| Linear/Logistic Regression | Yes (gradient-based) |
| SVM | Yes (distance-based) |
| KNN | Yes (distance-based) |
| Neural Networks | Yes (gradient-based) |
| Decision Trees | No (split-based) |
| Random Forest | No |
| XGBoost/LightGBM | No |

**Choosing Scaler:**
```
├── StandardScaler: Default choice, normal-ish distributions
├── MinMaxScaler: Need bounded range, no outliers
├── RobustScaler: Many outliers present
└── None: Tree-based models
```

**Critical Rule:**
```
Fit on training data ONLY, transform both:
├── scaler.fit(X_train)        # Learn from train
├── X_train_scaled = scaler.transform(X_train)
└── X_test_scaled = scaler.transform(X_test)
Never fit on test data! (Data leakage)
```

## Key Takeaways

- Scaling puts features on **similar ranges**
- **Essential** for gradient-based and distance-based algorithms
- **Not needed** for tree-based algorithms
- **StandardScaler**: Default choice for most cases
- **RobustScaler**: When outliers are present
- **Fit on train only**, transform both train and test
""",
        "key_points": [
            "Scaling puts features on similar ranges to prevent dominance",
            "Essential for gradient-based and distance-based algorithms",
            "Not needed for tree-based models (Random Forest, XGBoost)",
            "StandardScaler is the default choice for most cases",
            "Always fit scaler on training data only—avoid leakage"
        ]
    },
    
    "feature-selection": {
        "content": """
## What is it?

**Feature selection** identifies and removes irrelevant or redundant features to improve model performance, reduce overfitting, speed up training, and improve interpretability. Not all features are useful—some add noise.

Different from feature extraction (PCA), which creates new features.

## How it Works

**Three Approaches:**

```
1. Filter Methods (before training):
   ├── Correlation with target
   ├── Variance threshold
   ├── Chi-squared test
   └── Mutual information
   └── Fast, algorithm-agnostic

2. Wrapper Methods (use model):
   ├── Forward selection: Add features one by one
   ├── Backward elimination: Remove features one by one
   ├── Recursive Feature Elimination (RFE)
   └── Slower, better results

3. Embedded Methods (during training):
   ├── Lasso (L1): Coefficients go to zero
   ├── Tree importance: Built-in ranking
   └── Efficient, algorithm-specific
```

**Filter Example:**
```
Correlation-based selection:
├── Feature A: corr with target = 0.85 (keep)
├── Feature B: corr with target = 0.72 (keep)
├── Feature C: corr with target = 0.05 (drop)
└── Feature D: corr with target = -0.68 (keep)
```

## Example

**Selecting Features for House Price Prediction:**

```
Original: 25 features
Goal: Find most important subset

Step 1: Remove low variance
├── "has_roof" = 1 for all houses
└── Removed: 1 feature (24 remaining)

Step 2: Correlation filtering
├── "sq_feet" vs "total_rooms": 0.92 correlation
├── Keep "sq_feet" (higher target correlation)
└── Removed: 3 redundant features (21 remaining)

Step 3: Model-based (Random Forest importance)
Feature          Importance
sq_feet          0.35
location_score   0.22
bedrooms         0.12
age              0.08
bathrooms        0.06
lot_size         0.05
...
paint_color      0.001  ← Drop

Final: 12 most important features

Model Comparison:
├── All 25 features: R² = 0.82, training time: 45s
├── Top 12 features: R² = 0.84, training time: 18s
└── Fewer features, better results!
```

## When to Use

**Benefits of Feature Selection:**
```
├── Improved accuracy (less noise)
├── Reduced overfitting
├── Faster training and inference
├── Better interpretability
└── Lower storage and memory
```

**Method Selection:**

| Method | Use When |
|--------|----------|
| Correlation | Quick initial filter |
| Variance | Remove constants |
| RFE | Have compute budget, want best subset |
| Lasso | Want automatic selection during training |
| Tree importance | Using tree-based model |

**Warning Signs of Too Many Features:**
```
├── Features > samples (high dimensional)
├── Many correlated features
├── Low model performance despite tuning
├── Slow training times
└── Difficulty interpreting model
```

## Key Takeaways

- Remove **irrelevant** and **redundant** features
- **Filter methods**: Fast, pre-training (correlation, variance)
- **Wrapper methods**: Use model to evaluate (RFE)
- **Embedded methods**: During training (Lasso, tree importance)
- Fewer features can mean **better performance**
- Always **validate** that removing features helps
""",
        "key_points": [
            "Removes irrelevant and redundant features for better models",
            "Filter methods are fast but algorithm-agnostic",
            "Wrapper methods (RFE) are slower but more accurate",
            "Embedded methods (Lasso) select during training",
            "Fewer features often means better, faster, more interpretable models"
        ]
    },
    
    "feature-creation": {
        "content": """
## What is it?

**Feature creation** (or feature construction) generates new features from existing ones to capture patterns that raw features miss. This is where domain knowledge becomes most valuable—you create features that make sense for your specific problem.

Often the difference between a good and great model.

## How it Works

**Common Techniques:**

```
1. Mathematical Combinations:
   ├── Ratios: price_per_sqft = price / sq_feet
   ├── Products: bmi = weight * height²
   ├── Sums: total_debt = mortgage + car_loan + credit
   └── Differences: age_gap = current_year - birth_year

2. Polynomial Features:
   ├── x² = x × x
   ├── x × y (interactions)
   └── Captures non-linear relationships

3. Datetime Extraction:
   ├── Hour, day, month, year
   ├── is_weekend, is_holiday
   ├── days_since_event
   └── Quarter, season

4. Text Features:
   ├── Word count, character count
   ├── Sentiment score
   ├── Contains specific words
   └── TF-IDF values

5. Aggregations:
   ├── Customer's average purchase
   ├── Rolling means
   └── Group statistics
```

## Example

**E-commerce Click Prediction:**

```
Raw Features:
├── timestamp: 2024-03-15 14:32:15
├── user_id: 12345
├── product_price: 49.99
├── product_category: "Electronics"
└── page_views: 3

Created Features:
├── From timestamp:
│   ├── hour: 14
│   ├── day_of_week: 5 (Friday)
│   ├── is_weekend: False
│   └── is_business_hours: True
├── From user history:
│   ├── user_avg_purchase: 65.00
│   ├── user_purchase_count: 12
│   ├── days_since_last_purchase: 14
│   └── user_category_affinity: 0.8 (electronics)
├── Ratios:
│   ├── price_vs_avg: 49.99 / 65.00 = 0.77
│   └── engagement_ratio: 3 / avg_views = 1.5
└── Interactions:
    └── is_weekend × is_sale = False

Model Improvement:
├── Raw features only: AUC = 0.72
└── With engineered features: AUC = 0.89
```

## When to Use

**When to Create Features:**
```
├── Domain knowledge suggests relationships
├── Model struggling with raw features
├── Non-linear patterns exist
├── Temporal data (dates, times)
├── User behavior data
└── Text or categorical data
```

**Domain-Specific Examples:**

| Domain | Feature Ideas |
|--------|--------------|
| Finance | Debt-to-income, transaction velocity |
| Healthcare | BMI, age × condition interactions |
| Retail | Recency, frequency, monetary (RFM) |
| Marketing | Days since last contact, campaign response rate |

**Best Practices:**
```
├── Let domain knowledge guide you
├── Create features, then select
├── Test each feature's importance
├── Watch for data leakage!
├── Document feature logic
└── Automate feature creation in pipeline
```

## Key Takeaways

- **Create** new features from existing ones
- **Domain knowledge** is your biggest advantage
- **Datetime features**: Hour, day, is_weekend, etc. are often valuable
- **Ratios and interactions** capture relationships
- **Aggregations** from historical data are powerful
- Always **validate** feature value with importance analysis
""",
        "key_points": [
            "Create new features from existing ones to capture patterns",
            "Domain knowledge is key for meaningful features",
            "Date/time features are often highly predictive",
            "Ratios, interactions, and aggregations add value",
            "Validate new features with importance analysis"
        ]
    },
    
    "dimensionality-reduction": {
        "content": """
## What is it?

**Dimensionality reduction** transforms high-dimensional data into lower dimensions while preserving important information. It helps with visualization, speeds up training, reduces overfitting, and handles the "curse of dimensionality." **PCA** (Principal Component Analysis) is the most common method.

Different from feature selection—this creates new features.

## How it Works

**PCA (Principal Component Analysis):**

```
Goal: Find directions of maximum variance

Process:
1. Center data (subtract mean)
2. Calculate covariance matrix
3. Find eigenvectors (principal components)
4. Project data onto top K components

Result:
├── PC1: Direction of most variance
├── PC2: Second most variance, orthogonal to PC1
├── PC3: Third most, orthogonal to PC1 and PC2
└── ...and so on

Dimensionality reduction:
├── Original: 100 features
├── Keep top 10 PCs (90% variance)
└── 10x fewer dimensions, most info retained
```

**Explained Variance:**
```
Component  Variance Explained  Cumulative
PC1        45%                 45%
PC2        25%                 70%
PC3        10%                 80%
PC4        8%                  88%
PC5        5%                  93%  ← Stop here?

Rule: Keep components for ~90-95% variance
```

[Diagram: PCA Projecting Data to Lower Dimensions]

## Example

**Image Compression with PCA:**

```
Original Image:
├── 64x64 pixels = 4096 dimensions
├── Each pixel is a feature
└── Too many for some algorithms

PCA Compression:
├── Analyze variance across images
├── Find principal components
├── Keep top 100 components
└── 4096 → 100 dimensions (97% reduction!)

Information retained:
├── 100 components: 95% variance (good reconstruction)
├── 50 components: 85% variance (acceptable)
└── 10 components: 50% variance (blurry but recognizable)

For ML Classification:
├── Original 4096 features: Accuracy = 92%, Time = 45s
├── PCA with 100 features: Accuracy = 91%, Time = 5s
└── Minimal accuracy loss, 9x faster!
```

**Customer Segmentation Example:**
```
Original: 50 behavioral features
├── page_views, clicks, purchases, time_spent...
└── Hard to visualize 50 dimensions

After PCA (2 components):
├── PC1 ≈ "engagement level"
├── PC2 ≈ "purchase intent"
└── Now visualizable in 2D scatter plot!

Clusters become visible for segmentation
```

## When to Use

**Benefits:**
```
├── Visualization: Reduce to 2-3D for plotting
├── Speed: Fewer features = faster training
├── Noise reduction: Drops low-variance noise
├── Multicollinearity: Components are uncorrelated
└── Storage: Compressed representations
```

**Limitations:**
```
├── Interpretability lost: PCs are combinations
├── Linear only: Can't capture non-linear patterns
├── Variance ≠ Importance: High variance may be noise
└── Scaling required: Features must be standardized
```

**When to Use:**

| Situation | Recommendation |
|-----------|----------------|
| Many correlated features | PCA helps |
| Visualization needed | Reduce to 2-3D |
| Speed/memory issues | Reduce dimensions |
| Need interpretable features | Don't use PCA |
| Non-linear relationships | Use t-SNE or UMAP |

## Key Takeaways

- **Reduces dimensions** while preserving variance
- **PCA** finds directions of maximum variance
- Keep components for **90-95% cumulative variance**
- Great for **visualization, speed, and noise reduction**
- **Loses interpretability**: Features become abstract combinations
- **Must scale data** before applying PCA
""",
        "key_points": [
            "Reduces dimensions while preserving important information",
            "PCA finds directions of maximum variance",
            "Keep components explaining 90-95% of variance",
            "Useful for visualization, speed, and reducing noise",
            "Must scale data before applying—loses interpretability"
        ]
    }
}
