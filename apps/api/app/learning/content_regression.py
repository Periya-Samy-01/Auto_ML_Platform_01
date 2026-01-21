"""
Regression Topic Content
Lesson content for the Regression topic
"""

# Each lesson follows the structure:
# - What is it?
# - How it works
# - Example
# - When to Use
# - Key Takeaways

REGRESSION_CONTENT = {
    "what-is-regression": {
        "content": """
## What is it?

**Regression** is a type of supervised machine learning where the goal is to predict a **continuous numerical value**. Unlike classification which predicts categories, regression predicts quantities like prices, temperatures, ages, or scores.

Think of it as answering "how much?" or "how many?" rather than "which category?"

## How it Works

Regression algorithms learn the relationship between input features (X) and a continuous output variable (y).

```
The Goal:
Find a function f(X) that maps features to predictions
y_predicted = f(X)

Minimize the error between predictions and actual values:
Error = Σ(y_actual - y_predicted)²
```

The algorithm adjusts its parameters to minimize the difference between predicted and actual values, typically using metrics like Mean Squared Error (MSE).

**Key Concepts:**
- **Dependent Variable (y)**: The value you're predicting
- **Independent Variables (X)**: Features used for prediction
- **Residuals**: Differences between actual and predicted values

## Example

**House Price Prediction:**

```
Features (X):
├── Square footage: 2000 sq ft
├── Bedrooms: 3
├── Bathrooms: 2
├── Age: 10 years
└── Location score: 8/10

Target (y):
└── Price: $350,000 (continuous value)

Model learns:
├── Each sq ft adds ~$150
├── Each bedroom adds ~$10,000
├── Location score multiplies value
└── Age decreases value by ~$2,000/year
```

**Prediction for new house:**
```
2500 sq ft, 4 bed, 2 bath, 5 years, location 9/10
Predicted price: $425,000
```

[Diagram: Scatter Plot with Regression Line]

## When to Use

Regression is appropriate when:
- **Output is continuous**: Price, temperature, score, count
- **Relationship exists**: Features correlate with output
- **Prediction is needed**: Not just understanding relationships
- **Historical data available**: Past examples with known outcomes

**Common Applications:**
- House price prediction
- Sales forecasting
- Weather prediction
- Stock price movement
- Customer lifetime value
- Demand estimation

**Not Appropriate When:**
- Output is categorical (use classification)
- Output is count-based with low values (use Poisson regression)
- Relationships are purely random

## Key Takeaways

- Regression predicts **continuous numerical values**
- Learns the **relationship** between features and target
- Minimizes **prediction error** (often squared error)
- Evaluated using **MSE, RMSE, MAE, R²** metrics
- Foundation for many ML applications like **forecasting**
- Different from classification which predicts **categories**
""",
        "key_points": [
            "Regression predicts continuous numerical values",
            "Learns relationships between features and target",
            "Minimizes prediction error (MSE, RMSE)",
            "Common in forecasting, pricing, and estimation",
            "Different from classification which predicts categories"
        ]
    },
    
    "linear-regression": {
        "content": """
## What is it?

**Linear Regression** is the simplest and most fundamental regression algorithm. It models the relationship between features and the target as a straight line (in 2D) or hyperplane (in higher dimensions). Despite its simplicity, it's powerful for many real-world problems.

The equation: `y = w₁x₁ + w₂x₂ + ... + wₙxₙ + b`

## How it Works

Linear Regression finds the best-fitting line through the data by minimizing the sum of squared residuals.

```
Model Equation:
y = w₁x₁ + w₂x₂ + ... + wₙxₙ + b

Where:
├── w₁, w₂, ... = weights (coefficients)
├── x₁, x₂, ... = features
├── b = bias (intercept)
└── y = prediction

Training Objective:
Minimize Σ(y_actual - y_predicted)²
└── Called "Ordinary Least Squares" (OLS)
```

**Finding the Best Line:**
```
Method 1: Closed-form Solution (Normal Equation)
├── Direct mathematical formula
├── Fast for small datasets
└── Memory-intensive for large data

Method 2: Gradient Descent
├── Iteratively adjust weights
├── Works for any size dataset
└── Used in most ML libraries
```

[Diagram: Best Fit Line Through Data Points]

## Example

**Predicting Test Scores from Study Hours:**

```
Data:
Hours Studied | Score
      1       |   50
      2       |   55
      3       |   65
      4       |   70
      5       |   75

Linear Regression finds:
y = 6.5x + 43

Interpretation:
├── Intercept (43): Base score with 0 hours
├── Slope (6.5): Each hour adds 6.5 points
└── Prediction: 6 hours → 6.5(6) + 43 = 82

Coefficients tell a story:
├── Positive coefficient = positive relationship
├── Negative coefficient = negative relationship
└── Magnitude = strength of effect
```

## When to Use

**Advantages:**
- **Highly interpretable**: Coefficients explain feature effects
- **Fast training**: Closed-form solution available
- **No hyperparameters**: Simple to use
- **Works well for linear relationships**
- **Good baseline model**

**Limitations:**
- **Assumes linearity**: Can't capture curves
- **Sensitive to outliers**: Squared error amplifies
- **Multicollinearity issues**: Correlated features cause problems
- **Homoscedasticity assumption**: Equal variance expected

**Best Practices:**
```
Checklist:
├── Check for linear relationship (scatter plots)
├── Remove or handle outliers
├── Check for multicollinearity (VIF)
├── Scale features if using gradient descent
└── Consider polynomial features for non-linearity
```

## Key Takeaways

- Linear Regression models y as a **linear combination** of features
- Coefficients are **interpretable**: show feature impact
- Uses **Ordinary Least Squares** to minimize squared error
- **Simple but powerful** baseline for regression problems
- Assumes **linear relationship** between features and target
- Sensitive to **outliers** and **multicollinearity**
""",
        "key_points": [
            "Models target as linear combination of features",
            "Coefficients are highly interpretable",
            "Uses Ordinary Least Squares minimization",
            "Simple, fast, and excellent as baseline",
            "Assumes linear relationships between features and target"
        ]
    },
    
    "polynomial-regression": {
        "content": """
## What is it?

**Polynomial Regression** extends linear regression to capture non-linear relationships by adding polynomial features (x², x³, etc.). It's still a linear model in terms of coefficients, but can fit curved relationships in the data.

Think of it as bending the straight line into a curve.

## How it Works

Polynomial regression transforms features into polynomial terms, then applies linear regression.

```
Original Feature: x

Polynomial Transformation (degree 2):
├── x → [x, x²]

Polynomial Transformation (degree 3):
├── x → [x, x², x³]

Model becomes:
y = w₀ + w₁x + w₂x² + w₃x³ + ...

Still linear in weights (w), curved in x
```

**Choosing Degree:**
```
Degree Effects:
├── Degree 1: Straight line (linear regression)
├── Degree 2: Parabola (quadratic)
├── Degree 3: S-curves possible (cubic)
├── Degree 4+: More flexibility, overfitting risk

Warning Signs of Overfitting:
├── High training accuracy, low test accuracy
├── Wild oscillations in predictions
└── Unrealistic predictions outside training range
```

[Diagram: Linear vs Polynomial Fits on Curved Data]

## Example

**Salary vs. Experience (Non-linear relationship):**

```
Experience | Salary
    1      | $40,000
    3      | $50,000
    5      | $70,000
    10     | $120,000
    15     | $160,000
    20     | $180,000

Linear fit: Poor (underestimates mid-career)
y = $7,500x + $35,000
R² = 0.89

Polynomial (degree 2): Better fit
y = -$200x² + $11,000x + $30,000
R² = 0.97

Interpretation:
├── Early career: Rapid salary growth
├── Mid-career: Peak growth rate
└── Late career: Growth slows (diminishing returns)
```

**Polynomial Feature Creation:**
```
Original: [experience]
Degree 2: [experience, experience²]

For experience = 10:
├── Original: [10]
└── Polynomial: [10, 100]
```

## When to Use

**When to Choose Polynomial:**
- Clear **curved patterns** in scatter plots
- Linear regression has **poor R²** despite clear relationship
- Domain knowledge suggests **non-linear effects**

**Degree Selection:**
```
Guidelines:
├── Start with degree 2 (quadratic)
├── Use cross-validation to compare degrees
├── Prefer lower degree if similar performance
├── Rarely go beyond degree 4-5
└── Watch for overfitting with high degrees
```

**Alternatives for Non-linearity:**
- Decision Tree Regression
- Random Forest Regression
- Spline Regression
- Neural Networks

## Key Takeaways

- Polynomial regression captures **non-linear relationships**
- Created by **transforming features** to polynomial terms
- Still a **linear model** in coefficients
- **Degree** controls flexibility (and overfitting risk)
- Use **cross-validation** to select appropriate degree
- Higher degrees risk **overfitting**—prefer simpler models
""",
        "key_points": [
            "Captures non-linear patterns by adding polynomial terms",
            "Transform features to x², x³, etc.",
            "Still linear in coefficients, curved in features",
            "Degree controls flexibility and overfitting risk",
            "Use cross-validation to select appropriate degree"
        ]
    },
    
    "ridge-lasso": {
        "content": """
## What is it?

**Ridge** and **Lasso** are regularized versions of linear regression that prevent overfitting by adding a penalty term to the loss function. Ridge uses L2 regularization (squared weights), while Lasso uses L1 regularization (absolute weights).

Regularization helps when you have many features or correlated features.

## How it Works

Both methods add a penalty to the standard linear regression loss:

```
Standard Linear Regression:
Loss = Σ(y - ŷ)²

Ridge Regression (L2):
Loss = Σ(y - ŷ)² + α × Σ(w²)
├── Adds sum of squared weights
└── Shrinks weights toward zero (but never exactly zero)

Lasso Regression (L1):
Loss = Σ(y - ŷ)² + α × Σ|w|
├── Adds sum of absolute weights
└── Can shrink weights to exactly zero (feature selection!)

Elastic Net (L1 + L2):
Loss = Σ(y - ŷ)² + α₁ × Σ|w| + α₂ × Σ(w²)
└── Combines both penalties
```

**Alpha (α) Parameter:**
```
α Controls Regularization Strength:
├── α = 0: No regularization (standard linear regression)
├── α small: Light penalty, weights mostly unrestricted
├── α large: Heavy penalty, weights forced small
└── α → ∞: All weights approach zero
```

[Diagram: Effect of Alpha on Weight Shrinkage]

## Example

**Housing Price with Many Features:**

```
Problem: 50 features, some correlated, some irrelevant
Standard Linear Regression: Overfits, unstable coefficients

Ridge (α=1.0) Results:
├── All 50 features kept (small but non-zero weights)
├── Correlated features share importance
├── More stable predictions
└── Test R² improved from 0.75 to 0.82

Lasso (α=0.5) Results:
├── Only 15 features have non-zero weights
├── 35 features eliminated (automatic feature selection!)
├── More interpretable model
└── Test R² = 0.80

Feature Selection Example:
├── "sq_feet": 150.2 (important)
├── "bedrooms": 8500.5 (important)
├── "paint_color": 0.0 (removed by Lasso)
├── "door_style": 0.0 (removed by Lasso)
└── "neighborhood_score": 12000.3 (important)
```

## When to Use

**Choose Ridge When:**
- Many features that may all be relevant
- Correlated features present
- You want to keep all features
- Primary goal is prediction accuracy

**Choose Lasso When:**
- Suspect many irrelevant features
- Want automatic feature selection
- Need interpretable, sparse model
- Fewer features is preferable

**Choose Elastic Net When:**
- Some feature selection desired
- But also want ridge's stability
- Many correlated feature groups

**Tuning Alpha:**
```
Finding Optimal Alpha:
├── Use cross-validation
├── Try range: [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
├── Plot validation score vs alpha
└── Choose alpha with best CV score
```

## Key Takeaways

- **Regularization** prevents overfitting in linear regression
- **Ridge (L2)**: Shrinks weights, keeps all features
- **Lasso (L1)**: Can eliminate features (weights = 0)
- **Alpha** controls regularization strength
- Use **cross-validation** to tune alpha
- Lasso provides **automatic feature selection**
""",
        "key_points": [
            "Regularization prevents overfitting by penalizing large weights",
            "Ridge (L2) shrinks weights but keeps all features",
            "Lasso (L1) can eliminate features entirely (sparse models)",
            "Alpha parameter controls penalty strength",
            "Use cross-validation to find optimal alpha value"
        ]
    },
    
    "decision-tree-regression": {
        "content": """
## What is it?

**Decision Tree Regression** applies the decision tree structure to predict continuous values instead of classes. Instead of predicting a category at each leaf, it predicts a numerical value—typically the average of training samples that reach that leaf.

It can capture complex non-linear patterns without explicit feature transformation.

## How it Works

The tree splits data to minimize prediction variance within each leaf.

```
Building the Tree:
1. Start with all data at root
2. Find best split to reduce variance
3. Split data into child nodes
4. Repeat until stopping criteria met
5. Leaf prediction = mean of samples in leaf

Splitting Criterion (Regression):
├── Minimize Mean Squared Error in children
├── Variance reduction = Parent MSE - Weighted Child MSE
└── Choose split that maximizes variance reduction
```

**Prediction Process:**
```
For new sample:
1. Start at root
2. Evaluate condition at each node
3. Follow appropriate branch
4. Reach leaf node
5. Predict leaf's mean value
```

[Diagram: Decision Tree for Regression with Numerical Predictions in Leaves]

## Example

**Predicting House Prices:**

```
Decision Tree Structure:
                    [All Houses]
                    Mean: $300K
                         │
              sq_feet > 2000?
                   /         \\
                Yes           No
                 │             │
           Mean: $450K    Mean: $200K
                 │             │
        bedrooms > 3?   location > 5?
           /      \\       /       \\
        Yes       No    Yes       No
         │         │      │         │
     $550K     $380K  $250K     $160K

Prediction for new house:
├── 2500 sq ft → Yes (right branch)
├── 4 bedrooms → Yes (left branch)
└── Prediction: $550,000
```

**Comparison with Linear:**
```
Scenario: Price jumps at exactly 2000 sq ft (lot size threshold)

Linear Regression: Gradual slope (misses the jump)
Decision Tree: Captures the threshold exactly

Feature: sq_feet
├── < 2000: Predict ~$200K
└── >= 2000: Predict ~$450K
```

## When to Use

**Advantages:**
- **Captures non-linearity**: Without feature engineering
- **Handles interactions**: Naturally through branching
- **No scaling needed**: Works with raw values
- **Interpretable**: Can visualize the tree
- **Mixed feature types**: Numerical and categorical

**Disadvantages:**
- **Prone to overfitting**: Can memorize training data
- **High variance**: Small data changes, big tree changes
- **Piecewise constant**: Can't predict smooth functions
- **Extrapolation fails**: Outside training range

**Best Practices:**
```
Preventing Overfitting:
├── Set max_depth (e.g., 5-10)
├── Set min_samples_split (e.g., 20)
├── Set min_samples_leaf (e.g., 10)
├── Prune after building
└── Use Random Forest for better results
```

## Key Takeaways

- Decision Tree Regression predicts **mean values at leaves**
- Splits to minimize **variance** (MSE) in children
- **Captures non-linear patterns** without transformation
- **Prone to overfitting**: Use depth limits
- Predictions are **piecewise constant** (step functions)
- Foundation for **Random Forest Regression**
""",
        "key_points": [
            "Predicts mean value of training samples at each leaf",
            "Splits to minimize variance (MSE)",
            "Captures non-linear patterns without feature engineering",
            "Prone to overfitting—use depth limits and pruning",
            "Predictions are piecewise constant (step functions)"
        ]
    },
    
    "random-forest-regression": {
        "content": """
## What is it?

**Random Forest Regression** is an ensemble method that builds multiple decision tree regressors and averages their predictions. By combining many trees trained on random subsets, it achieves better accuracy and reduces overfitting compared to a single tree.

It's one of the most reliable algorithms for regression problems.

## How it Works

Similar to Random Forest for classification, but with averaging instead of voting.

```
Building Random Forest Regression:
1. Create N trees (e.g., 100-500)
2. For each tree:
   ├── Bootstrap sample: Random ~63% of rows
   └── Random features: Use subset at each split
3. Train trees to predict continuous values
4. Final prediction = Average of all tree predictions

Prediction:
├── Tree 1 predicts: $340,000
├── Tree 2 predicts: $360,000
├── Tree 3 predicts: $355,000
├── ...
├── Tree 100 predicts: $345,000
└── Final: Average = $351,500
```

**Why Averaging Works:**
```
Individual trees have variance (noise)
├── Tree 1: Overestimates some houses
├── Tree 2: Underestimates same houses
└── Average: Errors cancel out!

Variance Reduction:
├── Single tree variance: σ²
└── Average of N trees: σ²/N (under independence)
```

[Diagram: Multiple Trees Contributing to Average Prediction]

## Example

**Energy Consumption Prediction:**

```
Features:
├── Temperature: 85°F
├── Humidity: 60%
├── Day type: Weekday
├── Hour: 14:00
└── Previous hour usage: 450 kWh

Individual Tree Predictions (5 of 200):
├── Tree 1: 512 kWh (focuses on temperature)
├── Tree 2: 485 kWh (focuses on time)
├── Tree 3: 498 kWh (focuses on previous usage)
├── Tree 4: 505 kWh (balanced)
├── Tree 5: 495 kWh
└── ...

Final Prediction: 498.5 kWh (average of 200 trees)

Feature Importance (from splits):
├── Temperature: 35% importance
├── Previous usage: 25%
├── Hour: 20%
├── Day type: 15%
└── Humidity: 5%
```

## When to Use

**Advantages:**
- **Excellent accuracy**: Often best out-of-box
- **Robust**: Averaging reduces variance
- **Feature importance**: Built-in ranking
- **Handles non-linearity**: No transformation needed
- **Works with missing values**: Can handle indirectly
- **Parallelizable**: Trees train independently

**Disadvantages:**
- **Less interpretable**: Can't visualize 200 trees
- **Slower prediction**: Must query all trees
- **Memory usage**: Stores many trees
- **Can't extrapolate**: Outside training range

**Key Hyperparameters:**
```
Tuning Guide:
├── n_estimators: 100-500 (more = better, diminishing returns)
├── max_depth: None or 10-30 (limit for memory/speed)
├── min_samples_split: 2-20
├── max_features: 
│   ├── 'auto' or 1.0: All features
│   ├── 'sqrt': √n (good default for classification)
│   └── 0.33: 1/3 of features (often good for regression)
└── n_jobs: -1 (use all CPU cores)
```

## Key Takeaways

- Ensemble of decision trees with **averaging**
- **More accurate** and **stable** than single trees
- Provides **feature importance** rankings
- Excellent **default choice** for regression
- Trade-off: Less interpretable, more memory
- **Can't extrapolate** beyond training data range
""",
        "key_points": [
            "Ensemble of decision trees with averaged predictions",
            "More accurate and stable than single decision trees",
            "Provides built-in feature importance rankings",
            "Excellent default choice for regression problems",
            "Cannot extrapolate beyond training data range"
        ]
    },
    
    "gradient-boosting": {
        "content": """
## What is it?

**Gradient Boosting** is an ensemble technique that builds trees sequentially, where each tree corrects the errors of the previous ones. Unlike Random Forest which builds trees independently, Gradient Boosting creates a chain of weak learners that together form a strong predictor.

Popular implementations include **XGBoost**, **LightGBM**, and **CatBoost**.

## How it Works

Gradient Boosting combines trees by learning residuals (errors).

```
Gradient Boosting Process:
1. Start with simple prediction (e.g., mean of y)
2. Calculate residuals (errors)
3. Train tree to predict residuals
4. Add tree's predictions (scaled by learning rate)
5. Repeat: Calculate new residuals, train new tree
6. Final prediction = Sum of all tree contributions

Prediction Formula:
ŷ = initial_prediction + η×tree₁ + η×tree₂ + ... + η×treeₙ

Where η = learning rate (typically 0.01-0.3)
```

**Why It Works:**
```
Each tree focuses on what previous trees got wrong:
├── Tree 1: Captures main patterns
├── Tree 2: Fixes Tree 1's biggest errors
├── Tree 3: Fixes remaining errors
├── ...
└── Ensemble: Very accurate predictions
```

[Diagram: Sequential Tree Building in Gradient Boosting]

## Example

**Sales Forecasting:**

```
Iteration 1:
├── Initial prediction: $10,000 (mean)
├── Actual: $15,000
└── Residual: +$5,000

Iteration 2:
├── Tree 1 predicts residual: +$4,000
├── New prediction: $10,000 + 0.1×$4,000 = $10,400
├── New residual: +$4,600
└── (Learning rate 0.1 slows convergence)

Iteration 3:
├── Tree 2 predicts residual: +$4,200
├── New prediction: $10,400 + 0.1×$4,200 = $10,820
└── Residual shrinking!

After 100 iterations:
├── Prediction: $14,850
└── Close to actual $15,000
```

**Popular Implementations:**
```
XGBoost:
├── Regularization built-in
├── Handles missing values
├── Very fast (parallelized)
└── Most popular for competitions

LightGBM:
├── Histogram-based (faster)
├── Handles large datasets well
└── Good for high-dimensional data

CatBoost:
├── Handles categorical features natively
├── Less hyperparameter tuning needed
└── Good for datasets with categories
```

## When to Use

**Advantages:**
- **State-of-the-art accuracy**: Wins many competitions
- **Handles complex patterns**: Very flexible
- **Feature importance**: Like Random Forest
- **Regularization options**: Prevents overfitting

**Disadvantages:**
- **Harder to tune**: More hyperparameters
- **Slower training**: Sequential (not parallel)
- **Overfitting risk**: If not regularized
- **Less interpretable**: Than simpler models

**Key Hyperparameters:**
```
Critical Parameters:
├── n_estimators: 100-1000+ (use early stopping)
├── learning_rate: 0.01-0.3 (lower = more trees needed)
├── max_depth: 3-8 (shallower than RF)
├── min_samples_leaf: 20-100
├── subsample: 0.5-0.9 (row sampling)
└── colsample_bytree: 0.5-0.9 (column sampling)

Early Stopping:
├── Monitor validation score
├── Stop when no improvement for N rounds
└── Prevents overfitting, saves time
```

## Key Takeaways

- Builds trees **sequentially**, each correcting previous errors
- **State-of-the-art** accuracy for tabular data
- **XGBoost, LightGBM, CatBoost** are popular implementations
- Requires more **hyperparameter tuning** than Random Forest
- Use **early stopping** to prevent overfitting
- **Learning rate** controls contribution of each tree
""",
        "key_points": [
            "Builds trees sequentially, each correcting previous errors",
            "State-of-the-art accuracy for tabular data",
            "XGBoost, LightGBM, CatBoost are popular implementations",
            "Requires more hyperparameter tuning than Random Forest",
            "Use early stopping to prevent overfitting"
        ]
    },
    
    "feature-importance": {
        "content": """
## What is it?

**Feature Importance** quantifies how much each feature contributes to the model's predictions. Understanding which features matter most helps with model interpretation, feature selection, and gaining business insights.

Different algorithms provide different importance measures.

## How it Works

**Tree-Based Importance (Impurity-Based):**
```
For each feature, sum up:
├── Reduction in MSE from splits using this feature
├── Weighted by number of samples at each split
└── Normalize to sum to 1.0

Example:
├── sq_feet: 0.45 (explains 45% of variance reduction)
├── bedrooms: 0.25
├── location: 0.20
├── age: 0.08
└── parking: 0.02
```

**Permutation Importance:**
```
More reliable method:
1. Train model, record baseline score
2. For each feature:
   ├── Randomly shuffle feature values
   ├── Measure drop in model performance
   └── Importance = Performance drop
3. Larger drop = More important feature

Advantage: Works for any model type
```

**SHAP Values (Advanced):**
```
Game theory-based importance:
├── Shows contribution of each feature to each prediction
├── Can be positive or negative
├── Sums to prediction difference from baseline
└── Most comprehensive but computationally expensive
```

## Example

**House Price Model - Feature Importance Analysis:**

```
Random Forest Feature Importance:
1. sq_feet: 0.42     ████████████████████
2. location_score: 0.28  █████████████
3. bedrooms: 0.12    █████
4. bathrooms: 0.08   ███
5. age: 0.06         ██
6. parking: 0.03     █
7. paint_color: 0.01 

Insights:
├── Size (sq_feet) dominates price prediction
├── Location is second most important
├── Cosmetic features (paint_color) almost irrelevant
└── Consider dropping paint_color feature
```

**Permutation Importance (more reliable):**
```
Permutation Results (R² drop):
1. sq_feet: 0.35     (R² drops from 0.85 to 0.50)
2. location_score: 0.22
3. age: 0.10         (More important than tree-based suggested!)
4. bedrooms: 0.08
5. bathrooms: 0.05
6. parking: 0.02
7. paint_color: 0.00

Key difference: 'age' is more important than tree-based showed
├── Tree-based can be biased for high-cardinality features
└── Permutation importance is more trustworthy
```

## When to Use

**Use Feature Importance For:**
- **Model interpretation**: Understanding what drives predictions
- **Feature selection**: Removing unimportant features
- **Business insights**: Identifying key factors
- **Debugging**: Finding if model relies on wrong features
- **Simplification**: Building simpler models

**Choosing Method:**
```
Method Comparison:
├── Tree-based (built-in):
│   ├── Fast to compute
│   ├── Can be biased
│   └── Good for quick overview
│
├── Permutation:
│   ├── More reliable
│   ├── Model-agnostic
│   └── Slower (requires many predictions)
│
└── SHAP:
    ├── Most detailed (per-prediction)
    ├── Computationally expensive
    └── Best for deep understanding
```

**Caution:**
```
Important Considerations:
├── Correlated features share importance
├── Importance ≠ Causation
├── Feature importance can change with different random seeds
└── Use multiple methods to confirm findings
```

## Key Takeaways

- Feature importance shows **contribution** of each feature
- **Tree-based**: Fast but potentially biased
- **Permutation**: More reliable, works for any model
- **SHAP**: Most comprehensive, shows per-prediction contributions
- Use for **interpretation, feature selection, debugging**
- Correlated features **share importance**—interpret carefully
""",
        "key_points": [
            "Quantifies how much each feature contributes to predictions",
            "Tree-based importance is fast but potentially biased",
            "Permutation importance is more reliable and model-agnostic",
            "SHAP provides per-prediction feature contributions",
            "Correlated features share importance—interpret carefully"
        ]
    },
    
    "practice-housing": {
        "content": """
## What is it?

The **Housing dataset** is a classic regression dataset used for learning and practicing. The California Housing dataset contains information about housing blocks in California, with the goal of predicting median house values. It's larger and more realistic than toy datasets, making it ideal for practice.

This lesson walks through a complete regression workflow.

## How it Works

**Dataset Overview:**
```
California Housing Dataset:
├── Samples: ~20,000 block groups
├── Features: 8 numerical
│   ├── MedInc: Median income
│   ├── HouseAge: Median house age
│   ├── AveRooms: Average rooms per household
│   ├── AveBedrms: Average bedrooms per household
│   ├── Population: Block group population
│   ├── AveOccup: Average house occupancy
│   ├── Latitude: Location (N-S)
│   └── Longitude: Location (E-W)
├── Target: Median house value (hundreds of thousands)
└── Real-world: Contains noise and patterns
```

**Complete Workflow:**
```
Step 1: Load and Explore
├── Check shape, types, missing values
├── Visualize distributions
├── Check for outliers
└── Examine correlations

Step 2: Preprocess
├── Handle outliers if needed
├── Scale features (for some algorithms)
└── Create train/test split

Step 3: Train Multiple Models
├── Linear Regression (baseline)
├── Ridge/Lasso Regression
├── Random Forest
└── Gradient Boosting

Step 4: Evaluate
├── R² score (explained variance)
├── RMSE (root mean squared error)
├── MAE (mean absolute error)
└── Compare models

Step 5: Analyze
├── Feature importance
├── Residual plots
└── Error distribution
```

## Example

**Step-by-Step Regression:**

```
# Pseudocode Workflow

# Step 1: Load and Explore
data = load_california_housing()
X = data.features  # Shape: (20640, 8)
y = data.target    # Median house values

# Check statistics
print(X.describe())
print(y.describe())  # Range: 0.15 to 5.00 (in $100k)

# Correlation with target
correlations = {
    'MedInc': 0.69,     # Strong positive
    'AveRooms': 0.15,   # Weak positive
    'HouseAge': 0.11,   # Weak positive
    'Latitude': -0.14,  # Weak negative (south = higher)
    # ...
}

# Step 2: Split and Scale
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 3: Train Models
models = {
    'Linear': LinearRegression(),
    'Ridge': Ridge(alpha=1.0),
    'Random Forest': RandomForest(n_estimators=100),
    'Gradient Boosting': GradientBoosting(n_estimators=100)
}

# Step 4: Evaluate
Results:
Model              | R²    | RMSE   | MAE
Linear Regression  | 0.60  | 0.73   | 0.53
Ridge              | 0.60  | 0.73   | 0.53
Random Forest      | 0.81  | 0.50   | 0.33
Gradient Boosting  | 0.84  | 0.46   | 0.31  ← Best

# Step 5: Analyze Best Model (Gradient Boosting)
Feature Importance:
├── MedInc: 0.52 (income is key predictor)
├── AveOccup: 0.11
├── Latitude: 0.10
├── Longitude: 0.09
├── HouseAge: 0.07
├── AveRooms: 0.05
├── Population: 0.04
└── AveBedrms: 0.02
```

## When to Use

**This Workflow Applies To:**
- Any regression problem
- Comparing algorithm performance
- Understanding feature importance
- Baseline before complex approaches

**Practice Extensions:**
```
Try These Exercises:
├── Feature Engineering:
│   ├── Create rooms_per_person
│   ├── Create distance_to_coast
│   └── Bin latitude into regions
├── Hyperparameter Tuning:
│   ├── Grid search for Random Forest
│   └── Learning rate/depth for Gradient Boosting
├── Ensemble:
│   └── Average predictions from multiple models
└── Visualization:
    ├── Actual vs Predicted plot
    ├── Residual distribution
    └── Geographic error heatmap
```

## Key Takeaways

- **Full workflow**: Load → Explore → Preprocess → Train → Evaluate → Analyze
- **Baseline first**: Start with Linear Regression
- **Tree ensembles** often outperform linear models on complex data
- **Feature importance** reveals what drives predictions
- **MedInc (income)** is strongest predictor of housing prices
- Always **compare multiple algorithms** before choosing final model
""",
        "key_points": [
            "Housing datasets are realistic for practicing regression",
            "Full workflow: Load → Explore → Preprocess → Train → Evaluate",
            "Start with linear regression as baseline",
            "Tree ensembles often outperform linear models",
            "Feature importance analysis reveals key predictors"
        ]
    }
}
