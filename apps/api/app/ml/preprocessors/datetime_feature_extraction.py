# apps/workers/worker/ml/preprocessors/datetime_feature_extraction.py
"""
Datetime Feature Extraction Preprocessor.
Extracts useful features from datetime columns.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class DatetimeFeatureExtractionPreprocessor(BasePreprocessor):
    """
    Extract features from datetime columns.
    
    Extracts components like year, month, day, weekday, hour, etc.
    
    Parameters:
        columns (List[str], optional): Datetime columns to process.
            If None, processes all datetime columns. Default: None
        features (List[str]): Which features to extract. Options:
            - 'year': Year (e.g., 2024)
            - 'month': Month (1-12)
            - 'day': Day of month (1-31)
            - 'weekday': Day of week (0=Monday, 6=Sunday)
            - 'dayofweek': Same as weekday
            - 'hour': Hour (0-23)
            - 'minute': Minute (0-59)
            - 'second': Second (0-59)
            - 'quarter': Quarter (1-4)
            - 'dayofyear': Day of year (1-366)
            - 'weekofyear': Week of year (1-53)
            - 'is_weekend': Boolean (Saturday or Sunday)
            - 'is_month_start': Boolean
            - 'is_month_end': Boolean
            Default: ['year', 'month', 'day', 'weekday']
        drop_original (bool): Whether to drop original datetime columns.
            Default: True
        parse_dates (bool): Whether to attempt parsing string columns as dates.
            Default: True
        date_format (str, optional): Expected date format for parsing (e.g., '%Y-%m-%d').
            If None, pandas will infer the format. Default: None
    
    Example:
        >>> preprocessor = DatetimeFeatureExtractionPreprocessor(
        ...     name="extract_datetime",
        ...     params={
        ...         "columns": ["created_at", "updated_at"],
        ...         "features": ["year", "month", "day", "weekday", "is_weekend"]
        ...     }
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    VALID_FEATURES = {
        'year', 'month', 'day', 'weekday', 'dayofweek', 'hour', 'minute', 'second',
        'quarter', 'dayofyear', 'weekofyear', 'is_weekend', 'is_month_start', 'is_month_end'
    }
    
    def __init__(self, name: str = "datetime_feature_extraction", params: Optional[Dict[str, Any]] = None):
        """
        Initialize DatetimeFeatureExtractionPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters
        """
        params = params or {}
        if 'columns' not in params:
            params['columns'] = None
        if 'features' not in params:
            params['features'] = ['year', 'month', 'day', 'weekday']
        if 'drop_original' not in params:
            params['drop_original'] = True
        if 'parse_dates' not in params:
            params['parse_dates'] = True
        if 'date_format' not in params:
            params['date_format'] = None
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """Validate configuration parameters."""
        columns = self.params.get('columns')
        if columns is not None and not isinstance(columns, list):
            raise ValueError(f"'columns' must be a list or None, got {type(columns).__name__}")
        
        features = self.params.get('features', [])
        if not isinstance(features, list):
            raise ValueError(f"'features' must be a list, got {type(features).__name__}")
        
        invalid_features = set(features) - self.VALID_FEATURES
        if invalid_features:
            raise ValueError(
                f"Invalid features: {invalid_features}. "
                f"Valid options: {self.VALID_FEATURES}"
            )
        
        drop_original = self.params.get('drop_original', True)
        if not isinstance(drop_original, bool):
            raise ValueError(f"'drop_original' must be boolean, got {type(drop_original).__name__}")
    
    def fit(self, data: DataContainer) -> 'DatetimeFeatureExtractionPreprocessor':
        """
        Identify datetime columns to process.
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        columns = self.params.get('columns')
        parse_dates = self.params.get('parse_dates', True)
        date_format = self.params.get('date_format')
        
        # Determine columns to process
        if columns is None:
            # Find datetime columns
            datetime_cols = data.get_datetime_columns()
            
            # If parse_dates is True, also try to identify string columns that look like dates
            if parse_dates:
                for col in data.get_categorical_columns():
                    if col not in datetime_cols:
                        # Try to parse a sample
                        try:
                            sample = data.X[col].dropna().head(10)
                            if len(sample) > 0:
                                parsed = pd.to_datetime(sample, format=date_format, errors='coerce')
                                # If most values parsed successfully, include this column
                                if parsed.notna().sum() >= len(sample) * 0.8:
                                    datetime_cols.append(col)
                        except:
                            pass
        else:
            # Validate specified columns exist
            missing_cols = set(columns) - set(data.feature_names)
            if missing_cols:
                raise ValueError(f"Columns not found: {missing_cols}")
            datetime_cols = columns
        
        # Store column types for transform
        column_types = {}
        for col in datetime_cols:
            dtype = str(data.X[col].dtype)
            column_types[col] = {
                "original_dtype": dtype,
                "needs_parsing": 'datetime' not in dtype.lower()
            }
        
        self._fit_metadata = {
            "columns_to_process": datetime_cols,
            "column_types": column_types,
            "features_to_extract": self.params.get('features', [])
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Extract datetime features from data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with extracted features
        """
        self._check_is_fitted()
        
        result = data.copy()
        columns_to_process = self._fit_metadata['columns_to_process']
        column_types = self._fit_metadata['column_types']
        features_to_extract = self._fit_metadata['features_to_extract']
        drop_original = self.params.get('drop_original', True)
        date_format = self.params.get('date_format')
        
        columns_processed = []
        new_columns_created = []
        parsing_errors = {}
        
        for col in columns_to_process:
            if col not in result.X.columns:
                continue
            
            col_info = column_types.get(col, {})
            
            # Parse to datetime if needed
            if col_info.get('needs_parsing', True):
                try:
                    dt_series = pd.to_datetime(result.X[col], format=date_format, errors='coerce')
                    null_count = dt_series.isna().sum() - result.X[col].isna().sum()
                    if null_count > 0:
                        parsing_errors[col] = f"{null_count} values could not be parsed"
                except Exception as e:
                    parsing_errors[col] = str(e)
                    continue
            else:
                dt_series = result.X[col]
            
            # Extract features
            for feature in features_to_extract:
                new_col_name = f"{col}_{feature}"
                
                if feature == 'year':
                    result.X[new_col_name] = dt_series.dt.year
                elif feature == 'month':
                    result.X[new_col_name] = dt_series.dt.month
                elif feature == 'day':
                    result.X[new_col_name] = dt_series.dt.day
                elif feature in ('weekday', 'dayofweek'):
                    result.X[new_col_name] = dt_series.dt.dayofweek
                elif feature == 'hour':
                    result.X[new_col_name] = dt_series.dt.hour
                elif feature == 'minute':
                    result.X[new_col_name] = dt_series.dt.minute
                elif feature == 'second':
                    result.X[new_col_name] = dt_series.dt.second
                elif feature == 'quarter':
                    result.X[new_col_name] = dt_series.dt.quarter
                elif feature == 'dayofyear':
                    result.X[new_col_name] = dt_series.dt.dayofyear
                elif feature == 'weekofyear':
                    result.X[new_col_name] = dt_series.dt.isocalendar().week
                elif feature == 'is_weekend':
                    result.X[new_col_name] = dt_series.dt.dayofweek.isin([5, 6]).astype(int)
                elif feature == 'is_month_start':
                    result.X[new_col_name] = dt_series.dt.is_month_start.astype(int)
                elif feature == 'is_month_end':
                    result.X[new_col_name] = dt_series.dt.is_month_end.astype(int)
                
                new_columns_created.append(new_col_name)
            
            columns_processed.append(col)
        
        # Drop original columns if requested
        if drop_original:
            result.X = result.X.drop(columns=columns_processed, errors='ignore')
        
        # Update feature names
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "columns_processed": columns_processed,
            "new_columns_created": new_columns_created,
            "columns_dropped": columns_processed if drop_original else [],
            "features_extracted": features_to_extract,
            "parsing_errors": parsing_errors
        }
        
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
