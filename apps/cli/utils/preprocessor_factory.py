# cli/utils/preprocessor_factory.py
"""
Factory for instantiating preprocessors by name.
Maps preprocessor names to preprocessor classes.
"""

from typing import Dict, Type, List, Any, Optional
from apps.api.app.ml.preprocessors.base import BasePreprocessor
from apps.api.app.ml.preprocessors.duplicate_removal import DuplicateRemovalPreprocessor
from apps.api.app.ml.preprocessors.data_type_conversion import DataTypeConversionPreprocessor
from apps.api.app.ml.preprocessors.missing_value_imputation import MissingValueImputationPreprocessor
from apps.api.app.ml.preprocessors.outlier_handling import OutlierHandlingPreprocessor
from apps.api.app.ml.preprocessors.feature_scaling import FeatureScalingPreprocessor
from apps.api.app.ml.preprocessors.one_hot_encoding import OneHotEncodingPreprocessor
from apps.api.app.ml.preprocessors.ordinal_label_encoding import OrdinalLabelEncodingPreprocessor
from apps.api.app.ml.preprocessors.datetime_feature_extraction import DatetimeFeatureExtractionPreprocessor


# Mapping of preprocessor names to classes
PREPROCESSORS_MAP: Dict[str, Type[BasePreprocessor]] = {
    # Simple preprocessors
    "duplicate_removal": DuplicateRemovalPreprocessor,
    "data_type_conversion": DataTypeConversionPreprocessor,
    # Statistical preprocessors
    "missing_value_imputation": MissingValueImputationPreprocessor,
    "outlier_handling": OutlierHandlingPreprocessor,
    "feature_scaling": FeatureScalingPreprocessor,
    # Encoding preprocessors
    "one_hot_encoding": OneHotEncodingPreprocessor,
    "ordinal_label_encoding": OrdinalLabelEncodingPreprocessor,
    "datetime_feature_extraction": DatetimeFeatureExtractionPreprocessor,
}

# Short aliases for convenience
PREPROCESSOR_ALIASES: Dict[str, str] = {
    # Duplicate removal
    "duplicates": "duplicate_removal",
    "dedup": "duplicate_removal",
    # Data type conversion
    "convert": "data_type_conversion",
    "dtype": "data_type_conversion",
    # Missing values
    "missing": "missing_value_imputation",
    "impute": "missing_value_imputation",
    "fillna": "missing_value_imputation",
    # Outliers
    "outliers": "outlier_handling",
    "outlier": "outlier_handling",
    # Scaling
    "scale": "feature_scaling",
    "scaling": "feature_scaling",
    "normalize": "feature_scaling",
    # One-hot encoding
    "onehot": "one_hot_encoding",
    "one_hot": "one_hot_encoding",
    "dummies": "one_hot_encoding",
    # Label/ordinal encoding
    "label": "ordinal_label_encoding",
    "ordinal": "ordinal_label_encoding",
    "label_encoding": "ordinal_label_encoding",
    # Datetime
    "datetime": "datetime_feature_extraction",
    "date": "datetime_feature_extraction",
}

# Preprocessor descriptions for help text
PREPROCESSOR_DESCRIPTIONS: Dict[str, str] = {
    "duplicate_removal": "Remove duplicate rows from dataset",
    "data_type_conversion": "Convert column data types (int, float, str, category, datetime)",
    "missing_value_imputation": "Handle missing values (drop, mean, median, mode, constant)",
    "outlier_handling": "Detect and handle outliers (IQR, z-score methods)",
    "feature_scaling": "Scale numeric features (standard, minmax, robust, maxabs)",
    "one_hot_encoding": "One-hot encode categorical columns into binary columns",
    "ordinal_label_encoding": "Encode categorical columns as integers",
    "datetime_feature_extraction": "Extract features from datetime columns (year, month, day, etc.)",
}


def resolve_preprocessor_name(name: str) -> str:
    """
    Resolve preprocessor name from alias.
    
    Args:
        name: Preprocessor name or alias
        
    Returns:
        Canonical preprocessor name
    """
    name = name.lower().strip()
    return PREPROCESSOR_ALIASES.get(name, name)


def get_preprocessor(
    method: str,
    params: Optional[Dict[str, Any]] = None
) -> BasePreprocessor:
    """
    Get a preprocessor instance by method name.
    
    Args:
        method: Preprocessor name or alias (e.g., "missing_value_imputation", "impute")
        params: Configuration parameters for the preprocessor
        
    Returns:
        Instantiated preprocessor ready for fit()
        
    Raises:
        ValueError: If preprocessor not found
    """
    # Resolve alias to canonical name
    canonical_name = resolve_preprocessor_name(method)
    
    if canonical_name not in PREPROCESSORS_MAP:
        available = ", ".join(PREPROCESSORS_MAP.keys())
        raise ValueError(
            f"Preprocessor '{method}' not found.\n"
            f"Available preprocessors: {available}"
        )
    
    preprocessor_class = PREPROCESSORS_MAP[canonical_name]
    
    # Instantiate with name and params
    preprocessor = preprocessor_class(
        name=canonical_name,
        params=params
    )
    
    return preprocessor


def list_available_preprocessors(include_aliases: bool = False) -> List[str]:
    """
    Get list of available preprocessors.
    
    Args:
        include_aliases: Whether to include short aliases
        
    Returns:
        List of preprocessor names
    """
    if include_aliases:
        return list(PREPROCESSORS_MAP.keys()) + list(PREPROCESSOR_ALIASES.keys())
    return list(PREPROCESSORS_MAP.keys())


def get_preprocessor_info(method: str) -> Dict[str, Any]:
    """
    Get information about a preprocessor.
    
    Args:
        method: Preprocessor name or alias
        
    Returns:
        Dictionary with name, description, and parameter info
    """
    canonical_name = resolve_preprocessor_name(method)
    
    if canonical_name not in PREPROCESSORS_MAP:
        raise ValueError(f"Preprocessor '{method}' not found.")
    
    preprocessor_class = PREPROCESSORS_MAP[canonical_name]
    
    return {
        "name": canonical_name,
        "description": PREPROCESSOR_DESCRIPTIONS.get(canonical_name, ""),
        "class": preprocessor_class.__name__,
        "aliases": [alias for alias, target in PREPROCESSOR_ALIASES.items() if target == canonical_name]
    }
