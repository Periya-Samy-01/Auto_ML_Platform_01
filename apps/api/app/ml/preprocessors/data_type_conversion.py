# apps/workers/worker/ml/preprocessors/data_type_conversion.py
"""
Data Type Conversion Preprocessor.
Converts column data types (numeric, categorical, datetime).
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class DataTypeConversionPreprocessor(BasePreprocessor):
    """
    Convert column data types.
    
    Parameters:
        conversions (Dict[str, str]): Mapping of column names to target types.
            Supported types:
            - 'int' or 'int64': Convert to integer
            - 'float' or 'float64': Convert to float
            - 'str' or 'string': Convert to string
            - 'category': Convert to pandas categorical
            - 'datetime': Convert to datetime
            - 'bool': Convert to boolean
        errors (str): How to handle conversion errors.
            - 'raise': Raise exception on error (default)
            - 'coerce': Set invalid values to NaN
            - 'ignore': Leave unconvertible values unchanged
    
    Example:
        >>> preprocessor = DataTypeConversionPreprocessor(
        ...     name="convert_types",
        ...     params={
        ...         "conversions": {
        ...             "age": "int",
        ...             "price": "float",
        ...             "category": "category",
        ...             "date": "datetime"
        ...         },
        ...         "errors": "coerce"
        ...     }
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    # Supported target types
    SUPPORTED_TYPES = {
        'int', 'int64', 'int32',
        'float', 'float64', 'float32',
        'str', 'string', 'object',
        'category',
        'datetime', 'datetime64',
        'bool', 'boolean'
    }
    
    # Valid error handling modes
    VALID_ERRORS = {'raise', 'coerce', 'ignore'}
    
    def __init__(self, name: str = "data_type_conversion", params: Optional[Dict[str, Any]] = None):
        """
        Initialize DataTypeConversionPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration with 'conversions' dict and 'errors' mode
        """
        # Set defaults before validation
        params = params or {}
        if 'conversions' not in params:
            params['conversions'] = {}
        if 'errors' not in params:
            params['errors'] = 'raise'
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate 'conversions' parameter
        conversions = self.params.get('conversions', {})
        if not isinstance(conversions, dict):
            raise ValueError(
                f"'conversions' must be a dict, got {type(conversions).__name__}"
            )
        
        # Validate each target type
        for col, target_type in conversions.items():
            if target_type not in self.SUPPORTED_TYPES:
                raise ValueError(
                    f"Unsupported target type '{target_type}' for column '{col}'. "
                    f"Supported types: {self.SUPPORTED_TYPES}"
                )
        
        # Validate 'errors' parameter
        errors = self.params.get('errors', 'raise')
        if errors not in self.VALID_ERRORS:
            raise ValueError(
                f"Invalid 'errors' value: {errors}. "
                f"Must be one of: {self.VALID_ERRORS}"
            )
    
    def fit(self, data: DataContainer) -> 'DataTypeConversionPreprocessor':
        """
        Fit preprocessor (validates columns exist and records original types).
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        conversions = self.params.get('conversions', {})
        
        # Validate columns exist
        missing_cols = set(conversions.keys()) - set(data.feature_names)
        if missing_cols:
            raise ValueError(
                f"Columns not found in data: {missing_cols}. "
                f"Available columns: {data.feature_names}"
            )
        
        # Record original types
        original_types = {}
        for col in conversions.keys():
            original_types[col] = str(data.X[col].dtype)
        
        # Store fit metadata
        self._fit_metadata = {
            "original_types": original_types,
            "target_types": conversions.copy()
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply type conversions to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with converted types
            
        Raises:
            RuntimeError: If fit() not called first
            ValueError: If conversion fails and errors='raise'
        """
        self._check_is_fitted()
        
        # Create copy to avoid modifying original
        result = data.copy()
        
        conversions = self.params.get('conversions', {})
        errors = self.params.get('errors', 'raise')
        
        # Track conversion results
        successful_conversions = []
        failed_conversions = []
        coerced_values = {}
        
        for col, target_type in conversions.items():
            try:
                original_nulls = result.X[col].isna().sum()
                result.X[col] = self._convert_column(result.X[col], target_type, errors)
                new_nulls = result.X[col].isna().sum()
                
                successful_conversions.append(col)
                
                # Track if coercion created new nulls
                if new_nulls > original_nulls:
                    coerced_values[col] = int(new_nulls - original_nulls)
                    
            except Exception as e:
                if errors == 'raise':
                    raise ValueError(f"Failed to convert column '{col}' to {target_type}: {str(e)}")
                elif errors == 'ignore':
                    failed_conversions.append(col)
                # 'coerce' is handled inside _convert_column
        
        # Update feature names (columns unchanged)
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "coerced_to_null": coerced_values,
            "final_types": {col: str(result.X[col].dtype) for col in conversions.keys()}
        }
        
        # Add record to data's preprocessing history
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
    
    def _convert_column(self, series: pd.Series, target_type: str, errors: str) -> pd.Series:
        """
        Convert a single column to target type.
        
        Args:
            series: Column to convert
            target_type: Target data type
            errors: Error handling mode
            
        Returns:
            Converted series
        """
        # Normalize type names
        type_map = {
            'int': 'int64',
            'int32': 'int32',
            'int64': 'int64',
            'float': 'float64',
            'float32': 'float32',
            'float64': 'float64',
            'str': 'string',
            'string': 'string',
            'object': 'object',
            'category': 'category',
            'datetime': 'datetime64[ns]',
            'datetime64': 'datetime64[ns]',
            'bool': 'boolean',
            'boolean': 'boolean'
        }
        
        normalized_type = type_map.get(target_type, target_type)
        
        # Handle different type conversions
        if normalized_type in ('int64', 'int32'):
            # Integer conversion - need to handle NaN (use nullable int)
            if errors == 'coerce':
                series = pd.to_numeric(series, errors='coerce')
            return series.astype('Int64' if normalized_type == 'int64' else 'Int32')
        
        elif normalized_type in ('float64', 'float32'):
            if errors == 'coerce':
                return pd.to_numeric(series, errors='coerce').astype(normalized_type)
            return series.astype(normalized_type)
        
        elif normalized_type in ('string', 'object'):
            return series.astype(str)
        
        elif normalized_type == 'category':
            return series.astype('category')
        
        elif normalized_type == 'datetime64[ns]':
            return pd.to_datetime(series, errors=errors if errors != 'raise' else 'raise')
        
        elif normalized_type == 'boolean':
            # Boolean conversion
            if errors == 'coerce':
                # Map common boolean representations
                bool_map = {
                    'true': True, 'false': False,
                    'yes': True, 'no': False,
                    '1': True, '0': False,
                    1: True, 0: False
                }
                series = series.map(lambda x: bool_map.get(str(x).lower(), x) if pd.notna(x) else x)
            return series.astype('boolean')
        
        else:
            return series.astype(normalized_type)
