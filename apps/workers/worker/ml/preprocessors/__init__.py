# apps/workers/worker/ml/preprocessors/__init__.py
"""
Preprocessors package for AutoML Platform.
Contains data preprocessing modules for cleaning, encoding, and scaling.
"""

from .base import DataContainer, BasePreprocessor
from .duplicate_removal import DuplicateRemovalPreprocessor
from .data_type_conversion import DataTypeConversionPreprocessor
from .missing_value_imputation import MissingValueImputationPreprocessor
from .outlier_handling import OutlierHandlingPreprocessor
from .feature_scaling import FeatureScalingPreprocessor
from .one_hot_encoding import OneHotEncodingPreprocessor
from .ordinal_label_encoding import OrdinalLabelEncodingPreprocessor
from .datetime_feature_extraction import DatetimeFeatureExtractionPreprocessor

__all__ = [
    # Base classes
    "DataContainer",
    "BasePreprocessor",
    # Phase 2: Simple preprocessors
    "DuplicateRemovalPreprocessor",
    "DataTypeConversionPreprocessor",
    # Phase 3: Statistical preprocessors
    "MissingValueImputationPreprocessor",
    "OutlierHandlingPreprocessor",
    "FeatureScalingPreprocessor",
    # Phase 4: Encoding preprocessors
    "OneHotEncodingPreprocessor",
    "OrdinalLabelEncodingPreprocessor",
    "DatetimeFeatureExtractionPreprocessor",
]
