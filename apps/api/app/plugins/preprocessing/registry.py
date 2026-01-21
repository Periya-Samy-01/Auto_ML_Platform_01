"""
Preprocessing methods registry.

Defines all available preprocessing operations with their metadata,
parameters, and execution logic.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer


# =============================================================================
# CATEGORIES
# =============================================================================

PREPROCESSING_CATEGORIES = [
    {
        "key": "missing_values",
        "name": "Missing Values",
        "description": "Handle missing data in your dataset",
        "icon": "🔍",
    },
    {
        "key": "scaling",
        "name": "Feature Scaling",
        "description": "Normalize or standardize numeric features",
        "icon": "📏",
    },
    {
        "key": "encoding",
        "name": "Encoding",
        "description": "Convert categorical variables to numeric",
        "icon": "🔢",
    },
    {
        "key": "outliers",
        "name": "Outlier Handling",
        "description": "Detect and handle outliers",
        "icon": "📊",
    },
    {
        "key": "cleaning",
        "name": "Data Cleaning",
        "description": "Remove duplicates and unwanted columns",
        "icon": "🧹",
    },
]


# =============================================================================
# METHOD DEFINITIONS
# =============================================================================

PREPROCESSING_METHODS: List[Dict[str, Any]] = [
    # ----- MISSING VALUES -----
    {
        "slug": "fill_missing_mean",
        "name": "Fill Missing (Mean)",
        "description": "Replace missing values with column mean",
        "category": "missing_values",
        "applies_to": ["numeric"],
        "parameters": [],
    },
    {
        "slug": "fill_missing_median",
        "name": "Fill Missing (Median)",
        "description": "Replace missing values with column median",
        "category": "missing_values",
        "applies_to": ["numeric"],
        "parameters": [],
    },
    {
        "slug": "fill_missing_mode",
        "name": "Fill Missing (Mode)",
        "description": "Replace missing values with most frequent value",
        "category": "missing_values",
        "applies_to": ["numeric", "categorical"],
        "parameters": [],
    },
    {
        "slug": "fill_missing_constant",
        "name": "Fill Missing (Constant)",
        "description": "Replace missing values with a constant value",
        "category": "missing_values",
        "applies_to": ["numeric", "categorical"],
        "parameters": [
            {
                "key": "fill_value",
                "name": "Fill Value",
                "type": "text",
                "default": "0",
                "description": "Value to use for filling missing data",
            }
        ],
    },
    {
        "slug": "drop_missing_rows",
        "name": "Drop Rows with Missing",
        "description": "Remove rows containing any missing values",
        "category": "missing_values",
        "applies_to": ["numeric", "categorical"],
        "parameters": [
            {
                "key": "threshold",
                "name": "Threshold (%)",
                "type": "float",
                "default": 0,
                "min": 0,
                "max": 100,
                "description": "Only drop rows with more than this % missing",
            }
        ],
    },
    {
        "slug": "drop_missing_columns",
        "name": "Drop Columns with Missing",
        "description": "Remove columns with too many missing values",
        "category": "missing_values",
        "applies_to": ["numeric", "categorical"],
        "parameters": [
            {
                "key": "threshold",
                "name": "Threshold (%)",
                "type": "float",
                "default": 50,
                "min": 0,
                "max": 100,
                "description": "Drop columns with more than this % missing",
            }
        ],
    },

    # ----- SCALING -----
    {
        "slug": "standard_scaler",
        "name": "Standard Scaler",
        "description": "Standardize features to zero mean and unit variance",
        "category": "scaling",
        "applies_to": ["numeric"],
        "parameters": [],
    },
    {
        "slug": "minmax_scaler",
        "name": "Min-Max Scaler",
        "description": "Scale features to a given range (default 0-1)",
        "category": "scaling",
        "applies_to": ["numeric"],
        "parameters": [
            {
                "key": "feature_range_min",
                "name": "Range Min",
                "type": "float",
                "default": 0,
                "description": "Minimum value of the output range",
            },
            {
                "key": "feature_range_max",
                "name": "Range Max",
                "type": "float",
                "default": 1,
                "description": "Maximum value of the output range",
            },
        ],
    },
    {
        "slug": "robust_scaler",
        "name": "Robust Scaler",
        "description": "Scale using statistics robust to outliers",
        "category": "scaling",
        "applies_to": ["numeric"],
        "parameters": [],
    },
    {
        "slug": "maxabs_scaler",
        "name": "Max Absolute Scaler",
        "description": "Scale each feature by its maximum absolute value",
        "category": "scaling",
        "applies_to": ["numeric"],
        "parameters": [],
    },

    # ----- ENCODING -----
    {
        "slug": "onehot_encoder",
        "name": "One-Hot Encoder",
        "description": "Create binary columns for each category",
        "category": "encoding",
        "applies_to": ["categorical"],
        "parameters": [
            {
                "key": "drop_first",
                "name": "Drop First",
                "type": "bool",
                "default": False,
                "description": "Drop first category to avoid multicollinearity",
            },
            {
                "key": "columns",
                "name": "Columns",
                "type": "column_select",
                "default": [],
                "description": "Columns to encode (empty = all categorical)",
            },
        ],
    },
    {
        "slug": "label_encoder",
        "name": "Label Encoder",
        "description": "Encode categories as integers",
        "category": "encoding",
        "applies_to": ["categorical"],
        "parameters": [
            {
                "key": "columns",
                "name": "Columns",
                "type": "column_select",
                "default": [],
                "description": "Columns to encode (empty = all categorical)",
            },
        ],
    },

    # ----- OUTLIERS -----
    {
        "slug": "outlier_iqr",
        "name": "Remove Outliers (IQR)",
        "description": "Remove outliers using Interquartile Range method",
        "category": "outliers",
        "applies_to": ["numeric"],
        "parameters": [
            {
                "key": "iqr_multiplier",
                "name": "IQR Multiplier",
                "type": "float",
                "default": 1.5,
                "min": 1.0,
                "max": 3.0,
                "description": "Multiplier for IQR to define outlier bounds",
            },
        ],
    },
    {
        "slug": "outlier_zscore",
        "name": "Remove Outliers (Z-Score)",
        "description": "Remove outliers using Z-Score method",
        "category": "outliers",
        "applies_to": ["numeric"],
        "parameters": [
            {
                "key": "z_threshold",
                "name": "Z-Score Threshold",
                "type": "float",
                "default": 3.0,
                "min": 2.0,
                "max": 5.0,
                "description": "Z-score threshold for outlier detection",
            },
        ],
    },
    {
        "slug": "outlier_clip",
        "name": "Clip Outliers",
        "description": "Clip outliers to specified percentiles",
        "category": "outliers",
        "applies_to": ["numeric"],
        "parameters": [
            {
                "key": "lower_percentile",
                "name": "Lower Percentile",
                "type": "float",
                "default": 1,
                "min": 0,
                "max": 50,
                "description": "Lower percentile for clipping",
            },
            {
                "key": "upper_percentile",
                "name": "Upper Percentile",
                "type": "float",
                "default": 99,
                "min": 50,
                "max": 100,
                "description": "Upper percentile for clipping",
            },
        ],
    },

    # ----- CLEANING -----
    {
        "slug": "remove_duplicates",
        "name": "Remove Duplicates",
        "description": "Remove duplicate rows from the dataset",
        "category": "cleaning",
        "applies_to": ["numeric", "categorical"],
        "parameters": [
            {
                "key": "keep",
                "name": "Keep",
                "type": "select",
                "default": "first",
                "options": [
                    {"value": "first", "label": "Keep First"},
                    {"value": "last", "label": "Keep Last"},
                ],
                "description": "Which duplicate to keep",
            },
        ],
    },
    {
        "slug": "drop_columns",
        "name": "Drop Columns",
        "description": "Remove specified columns from the dataset",
        "category": "cleaning",
        "applies_to": ["numeric", "categorical"],
        "parameters": [
            {
                "key": "columns",
                "name": "Columns to Drop",
                "type": "column_select",
                "default": [],
                "description": "Select columns to remove",
            },
        ],
    },
]


# =============================================================================
# REGISTRY FUNCTIONS
# =============================================================================

def get_method(slug: str) -> Optional[Dict[str, Any]]:
    """Get a preprocessing method by slug."""
    for method in PREPROCESSING_METHODS:
        if method["slug"] == slug:
            return method
    return None


def get_all_methods() -> List[Dict[str, Any]]:
    """Get all preprocessing methods."""
    return PREPROCESSING_METHODS


def get_methods_by_category(category: str) -> List[Dict[str, Any]]:
    """Get preprocessing methods in a category."""
    return [m for m in PREPROCESSING_METHODS if m["category"] == category]


# =============================================================================
# EXECUTION FUNCTIONS
# =============================================================================

def apply_preprocessing(
    df: pd.DataFrame,
    method_slug: str,
    parameters: Dict[str, Any],
    target_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Apply a preprocessing method to a DataFrame.

    Args:
        df: Input DataFrame
        method_slug: The preprocessing method to apply
        parameters: Method-specific parameters
        target_column: Target column to exclude from preprocessing

    Returns:
        Transformed DataFrame
    """
    method = get_method(method_slug)
    if method is None:
        raise ValueError(f"Unknown preprocessing method: {method_slug}")

    # Get numeric and categorical columns (excluding target)
    exclude_cols = [target_column] if target_column else []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in exclude_cols]
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    categorical_cols = [c for c in categorical_cols if c not in exclude_cols]

    result = df.copy()

    # ----- MISSING VALUES -----
    if method_slug == "fill_missing_mean":
        imputer = SimpleImputer(strategy='mean')
        if numeric_cols:
            result[numeric_cols] = imputer.fit_transform(result[numeric_cols])

    elif method_slug == "fill_missing_median":
        imputer = SimpleImputer(strategy='median')
        if numeric_cols:
            result[numeric_cols] = imputer.fit_transform(result[numeric_cols])

    elif method_slug == "fill_missing_mode":
        imputer = SimpleImputer(strategy='most_frequent')
        cols = numeric_cols + categorical_cols
        if cols:
            result[cols] = imputer.fit_transform(result[cols])

    elif method_slug == "fill_missing_constant":
        fill_value = parameters.get("fill_value", "0")
        result = result.fillna(fill_value)

    elif method_slug == "drop_missing_rows":
        threshold = parameters.get("threshold", 0) / 100
        if threshold > 0:
            # Drop rows where more than threshold % of columns are missing
            thresh_count = int((1 - threshold) * len(result.columns))
            result = result.dropna(thresh=thresh_count)
        else:
            result = result.dropna()

    elif method_slug == "drop_missing_columns":
        threshold = parameters.get("threshold", 50) / 100
        # Drop columns with more than threshold % missing
        missing_pct = result.isnull().sum() / len(result)
        cols_to_keep = missing_pct[missing_pct <= threshold].index
        result = result[cols_to_keep]

    # ----- SCALING -----
    elif method_slug == "standard_scaler":
        scaler = StandardScaler()
        if numeric_cols:
            result[numeric_cols] = scaler.fit_transform(result[numeric_cols])

    elif method_slug == "minmax_scaler":
        range_min = parameters.get("feature_range_min", 0)
        range_max = parameters.get("feature_range_max", 1)
        scaler = MinMaxScaler(feature_range=(range_min, range_max))
        if numeric_cols:
            result[numeric_cols] = scaler.fit_transform(result[numeric_cols])

    elif method_slug == "robust_scaler":
        scaler = RobustScaler()
        if numeric_cols:
            result[numeric_cols] = scaler.fit_transform(result[numeric_cols])

    elif method_slug == "maxabs_scaler":
        scaler = MaxAbsScaler()
        if numeric_cols:
            result[numeric_cols] = scaler.fit_transform(result[numeric_cols])

    # ----- ENCODING -----
    elif method_slug == "onehot_encoder":
        columns = parameters.get("columns", [])
        drop_first = parameters.get("drop_first", False)

        if not columns:
            columns = categorical_cols

        if columns:
            result = pd.get_dummies(
                result,
                columns=columns,
                drop_first=drop_first,
                dtype=int
            )

    elif method_slug == "label_encoder":
        columns = parameters.get("columns", [])
        if not columns:
            columns = categorical_cols

        for col in columns:
            if col in result.columns:
                le = LabelEncoder()
                result[col] = le.fit_transform(result[col].astype(str))

    # ----- OUTLIERS -----
    elif method_slug == "outlier_iqr":
        multiplier = parameters.get("iqr_multiplier", 1.5)
        for col in numeric_cols:
            Q1 = result[col].quantile(0.25)
            Q3 = result[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            result = result[(result[col] >= lower_bound) & (result[col] <= upper_bound)]

    elif method_slug == "outlier_zscore":
        threshold = parameters.get("z_threshold", 3.0)
        from scipy import stats
        for col in numeric_cols:
            z_scores = np.abs(stats.zscore(result[col].dropna()))
            mask = z_scores < threshold
            # Create full mask including NaN positions
            full_mask = result[col].isna() | result[col].index.isin(result[col].dropna().index[mask])
            result = result[full_mask]

    elif method_slug == "outlier_clip":
        lower_pct = parameters.get("lower_percentile", 1)
        upper_pct = parameters.get("upper_percentile", 99)
        for col in numeric_cols:
            lower_val = result[col].quantile(lower_pct / 100)
            upper_val = result[col].quantile(upper_pct / 100)
            result[col] = result[col].clip(lower_val, upper_val)

    # ----- CLEANING -----
    elif method_slug == "remove_duplicates":
        keep = parameters.get("keep", "first")
        result = result.drop_duplicates(keep=keep)

    elif method_slug == "drop_columns":
        columns = parameters.get("columns", [])
        if columns:
            result = result.drop(columns=[c for c in columns if c in result.columns], errors='ignore')

    return result
