# ML Pipeline

> **Note**: This documentation reflects the current ML implementation. The algorithms and features may evolve as the platform develops.

## Overview

The ML Pipeline is the core of the AutoML Platform's machine learning capabilities. It consists of three main components:

1. **Preprocessors** - Clean and transform data before training
2. **Trainers** - Train ML models using various algorithms
3. **Evaluators** - Measure model performance with appropriate metrics

All components follow a consistent pattern with abstract base classes that define the interface, and concrete implementations for each algorithm or method.

---

## How the Pipeline Works

When a user executes a workflow, the system:

1. **Loads the dataset** from storage
2. **Applies preprocessing** nodes in order (as defined by workflow edges)
3. **Splits data** into training and test sets (if specified)
4. **Trains the model** using the selected algorithm
5. **Evaluates performance** using appropriate metrics
6. **Saves results** (model file, metrics, visualizations)

Each node in the workflow corresponds to a component in the ML pipeline.

---

## Preprocessors

Preprocessors transform raw data into a format suitable for ML training. They handle common data quality issues and feature engineering tasks.

### Available Preprocessors

| Preprocessor | Category | Purpose |
|--------------|----------|---------|
| **DuplicateRemoval** | Cleaning | Remove duplicate rows from dataset |
| **DataTypeConversion** | Cleaning | Convert columns to appropriate data types |
| **MissingValueImputation** | Missing Values | Fill in missing values using various strategies |
| **OutlierHandling** | Outliers | Detect and handle outlier values |
| **FeatureScaling** | Scaling | Normalize or standardize numeric features |
| **OneHotEncoding** | Encoding | Convert categorical variables to binary columns |
| **OrdinalLabelEncoding** | Encoding | Convert categories to ordered integers |
| **DatetimeFeatureExtraction** | Feature Engineering | Extract features from datetime columns |

### How Preprocessors Work

Each preprocessor follows the same pattern:

1. **Configure** - Set parameters (which columns, what strategy, etc.)
2. **Fit** - Learn statistics from training data (means, categories, etc.)
3. **Transform** - Apply transformation to data
4. **Fit-Transform** - Combined fit and transform for convenience

### DataContainer

Preprocessors work with a `DataContainer` class that wraps the data and metadata:

- Holds the dataframe being processed
- Tracks column names and types
- Maintains transformation history
- Separates features from target column

### Detailed Preprocessor Descriptions

**DuplicateRemoval**:
- Identifies and removes duplicate rows
- Can keep first, last, or no duplicates
- Useful for cleaning datasets with repeated entries

**DataTypeConversion**:
- Converts string columns to appropriate types
- Handles numeric, datetime, and categorical conversions
- Improves memory usage and enables proper analysis

**MissingValueImputation**:
- Strategies: mean, median, mode, constant, drop
- Can apply different strategies per column
- Important for algorithms that can't handle null values

**OutlierHandling**:
- Detection methods: IQR, Z-score, percentile
- Handling options: remove, cap, replace with null
- Helps prevent extreme values from skewing models

**FeatureScaling**:
- Methods: StandardScaler (z-score), MinMaxScaler (0-1), RobustScaler
- Normalizes numeric features to similar ranges
- Important for distance-based algorithms (KNN, Neural Networks)

**OneHotEncoding**:
- Creates binary column for each category
- Handles unknown categories during inference
- Suitable for low-cardinality categorical features

**OrdinalLabelEncoding**:
- Converts categories to integers (0, 1, 2, ...)
- Can preserve order for ordinal data
- More memory-efficient than one-hot for high cardinality

**DatetimeFeatureExtraction**:
- Extracts: year, month, day, weekday, hour, etc.
- Can calculate time since/until reference date
- Enables models to learn from temporal patterns

---

## Trainers

Trainers implement machine learning algorithms. Each trainer wraps a scikit-learn or XGBoost model with a consistent interface.

### Available Trainers

| Trainer | Task Type | Best For |
|---------|-----------|----------|
| **LogisticRegression** | Classification | Binary/multiclass classification with linear decision boundaries |
| **NaiveBayes** | Classification | Text classification, quick baseline models |
| **KNN** | Classification | Small datasets, instance-based learning |
| **DecisionTree** | Classification/Regression | Interpretable models, feature importance |
| **RandomForest** | Classification/Regression | Robust predictions, handles outliers well |
| **XGBoost** | Classification/Regression | Best performance on tabular data |
| **LinearRegression** | Regression | Simple linear relationships |
| **KMeans** | Clustering | Grouping similar data points |
| **PCA** | Dimensionality Reduction | Reducing features while preserving variance |
| **NeuralNetwork** | Classification/Regression | Complex patterns, large datasets |

### Task Types

- **Classification**: Predict categorical labels (spam/not spam, categories)
- **Regression**: Predict continuous values (price, temperature)
- **Clustering**: Group similar items without labels
- **Dimensionality Reduction**: Reduce number of features

### BaseTrainer Interface

All trainers inherit from `BaseTrainer` and implement these core methods:

**fit(X, y)**:
- Trains the model on provided data
- X is the feature matrix
- y is the target (None for unsupervised tasks)
- Returns self for method chaining

**predict(X)**:
- Makes predictions on new data
- Returns predictions (labels, values, or clusters)

**predict_proba(X)** (Classification only):
- Returns class probabilities
- Useful for ROC-AUC and probability thresholds

### Optional Methods

**get_feature_importance()**:
- Returns importance scores for each feature
- Supported by tree-based models and linear models
- Helps understand which features matter most

**suggest_optuna_params(trial)**:
- Defines hyperparameter search space
- Used for automatic hyperparameter tuning (Pro feature)

### Model Persistence

Trainers can be saved and loaded:

**save(path)**:
- Saves `model.joblib` (the trained model)
- Saves `metadata.json` (hyperparameters, training info)

**load(path)**:
- Restores trainer from saved files
- Can make predictions without retraining

### Hyperparameters

Each trainer has configurable hyperparameters. The frontend's plugin system provides the UI for these, and they're validated in the trainer's `_validate_hyperparameters()` method.

Example hyperparameters by model type:

**RandomForest**:
- n_estimators: Number of trees
- max_depth: Maximum tree depth
- min_samples_split: Minimum samples to split a node

**XGBoost**:
- n_estimators: Number of boosting rounds
- learning_rate: Step size shrinkage
- max_depth: Maximum tree depth
- subsample: Fraction of samples per tree

**Neural Network**:
- hidden_layer_sizes: Neurons per layer
- activation: Activation function
- learning_rate: Learning rate schedule
- max_iter: Maximum training iterations

---

## Evaluators

Evaluators calculate performance metrics appropriate for each task type.

### Available Evaluators

| Evaluator | Task Type | Output Metrics |
|-----------|-----------|----------------|
| **ClassificationEvaluator** | Classification | Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC |
| **RegressionEvaluator** | Regression | MSE, RMSE, MAE, R², MAPE |
| **ClusteringEvaluator** | Clustering | Silhouette Score, Calinski-Harabasz, Davies-Bouldin |

### Classification Metrics

| Metric | Description | Higher is Better? |
|--------|-------------|-------------------|
| **Accuracy** | Percentage of correct predictions | Yes |
| **Precision** | Of predicted positives, how many were correct | Yes |
| **Recall** | Of actual positives, how many were found | Yes |
| **F1 Score** | Harmonic mean of precision and recall | Yes |
| **ROC-AUC** | Area under ROC curve (binary only) | Yes |

The evaluator automatically handles binary vs. multiclass:
- Binary: Uses direct binary metrics
- Multiclass: Uses weighted average across classes

### Regression Metrics

| Metric | Description | Lower is Better? |
|--------|-------------|------------------|
| **MSE** | Mean Squared Error | Yes (lower) |
| **RMSE** | Root Mean Squared Error | Yes (lower) |
| **MAE** | Mean Absolute Error | Yes (lower) |
| **R²** | Coefficient of Determination | No (higher is better) |
| **MAPE** | Mean Absolute Percentage Error | Yes (lower) |

### Clustering Metrics

| Metric | Description | Higher is Better? |
|--------|-------------|-------------------|
| **Silhouette Score** | Measures cluster cohesion vs separation (-1 to 1) | Yes |
| **Calinski-Harabasz** | Ratio of between-cluster to within-cluster dispersion | Yes |
| **Davies-Bouldin** | Average similarity between clusters | No (lower is better) |

### How Evaluators Work

Evaluators take predictions and ground truth, returning a dictionary of metrics:

**Input**:
- `y_true`: Actual values from test set
- `y_pred`: Model predictions
- `y_pred_proba`: Probability predictions (optional, for ROC-AUC)

**Output**:
- Dictionary with all relevant metrics
- Values are Python floats (JSON-serializable)
- Confusion matrix as 2D list

---

## Directory Structure

```
apps/api/app/ml/
├── __init__.py           # Exports all components
├── constants.py          # Shared constants
├── errors.py             # Custom exceptions
├── logging_config.py     # Logging setup
├── worker_utils.py       # Worker helper functions
├── trainers/
│   ├── __init__.py       # Exports all trainers
│   ├── base.py           # BaseTrainer abstract class
│   ├── logistic_regression.py
│   ├── naive_bayes.py
│   ├── knn.py
│   ├── decision_tree.py
│   ├── random_forest.py
│   ├── xgboost.py
│   ├── linear_regression.py
│   ├── kmeans.py
│   ├── pca.py
│   └── neural_network.py
├── evaluators/
│   ├── __init__.py       # Exports all evaluators
│   ├── base.py           # BaseEvaluator abstract class
│   ├── classification_evaluator.py
│   ├── regression_evaluator.py
│   └── clustering_evaluator.py
├── preprocessors/
│   ├── __init__.py       # Exports all preprocessors
│   ├── base.py           # DataContainer, BasePreprocessor
│   ├── duplicate_removal.py
│   ├── data_type_conversion.py
│   ├── missing_value_imputation.py
│   ├── outlier_handling.py
│   ├── feature_scaling.py
│   ├── one_hot_encoding.py
│   ├── ordinal_label_encoding.py
│   └── datetime_feature_extraction.py
└── utils/
    └── ...               # Utility functions
```

---

## Integration with Plugin System

The frontend gets information about available algorithms and their hyperparameters through the Plugin API (`/api/plugins`). This creates a dynamic, extensible system:

1. **Plugin registry** lists available trainers/preprocessors
2. **Frontend** fetches plugin info and renders appropriate UI
3. **User** configures hyperparameters in the inspector panel
4. **Configuration** is stored in the workflow node
5. **Worker** reads config and instantiates the correct component

This separation allows adding new algorithms without changing the frontend.

---

## Adding New Algorithms

To add a new ML algorithm:

1. **Create trainer class** inheriting from `BaseTrainer`
2. **Implement required methods** (`fit`, `predict`, `_validate_hyperparameters`, `get_model_type`)
3. **Add to `__init__.py`** exports
4. **Register in plugin system** with hyperparameter schema
5. **Frontend auto-discovers** through plugins API

The same pattern applies for preprocessors and evaluators.
