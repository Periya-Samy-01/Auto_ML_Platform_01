# apps/workers/worker/ml/preprocessors/feature_scaling.py
"""
Feature Scaling Preprocessor.
Scales numeric features using various methods.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class FeatureScalingPreprocessor(BasePreprocessor):
    """
    Scale numeric features using various methods.
    
    Parameters:
        method (str): Scaling method.
            - 'standard': StandardScaler (mean=0, std=1)
            - 'minmax': MinMaxScaler (scale to 0-1 range)
            - 'robust': RobustScaler (use median and IQR, robust to outliers)
            - 'maxabs': MaxAbsScaler (scale by max absolute value, range -1 to 1)
            Default: 'standard'
        columns (List[str], optional): Columns to scale.
            If None, scales all numeric columns. Default: None
        feature_range (tuple): For 'minmax' only, target range. Default: (0, 1)
    
    Example:
        >>> preprocessor = FeatureScalingPreprocessor(
        ...     name="scale_features",
        ...     params={"method": "standard", "columns": ["age", "income"]}
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    VALID_METHODS = {'standard', 'minmax', 'robust', 'maxabs'}
    
    def __init__(self, name: str = "feature_scaling", params: Optional[Dict[str, Any]] = None):
        """
        Initialize FeatureScalingPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters
        """
        params = params or {}
        if 'method' not in params:
            params['method'] = 'standard'
        if 'columns' not in params:
            params['columns'] = None
        if 'feature_range' not in params:
            params['feature_range'] = (0, 1)
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """Validate configuration parameters."""
        method = self.params.get('method', 'standard')
        if method not in self.VALID_METHODS:
            raise ValueError(
                f"Invalid method: {method}. Must be one of: {self.VALID_METHODS}"
            )
        
        columns = self.params.get('columns')
        if columns is not None and not isinstance(columns, list):
            raise ValueError(f"'columns' must be a list or None, got {type(columns).__name__}")
        
        feature_range = self.params.get('feature_range', (0, 1))
        if not isinstance(feature_range, (tuple, list)) or len(feature_range) != 2:
            raise ValueError(f"'feature_range' must be a tuple of (min, max), got {feature_range}")
        if feature_range[0] >= feature_range[1]:
            raise ValueError(f"'feature_range' min must be less than max, got {feature_range}")
    
    def fit(self, data: DataContainer) -> 'FeatureScalingPreprocessor':
        """
        Learn scaling parameters from data.
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        method = self.params.get('method')
        columns = self.params.get('columns')
        
        # Determine columns to process
        if columns is None:
            numeric_cols = data.get_numeric_columns()
        else:
            # Validate specified columns exist and are numeric
            missing_cols = set(columns) - set(data.feature_names)
            if missing_cols:
                raise ValueError(f"Columns not found: {missing_cols}")
            
            numeric_cols = []
            for col in columns:
                if pd.api.types.is_numeric_dtype(data.X[col]):
                    numeric_cols.append(col)
                else:
                    raise ValueError(f"Column '{col}' is not numeric.")
        
        # Calculate scaling parameters for each column
        scaling_params = {}
        
        for col in numeric_cols:
            col_data = data.X[col].dropna()
            
            if method == 'standard':
                mean = col_data.mean()
                std = col_data.std()
                # Avoid division by zero
                if std == 0:
                    std = 1.0
                scaling_params[col] = {
                    "mean": float(mean),
                    "std": float(std)
                }
                
            elif method == 'minmax':
                min_val = col_data.min()
                max_val = col_data.max()
                # Avoid division by zero
                range_val = max_val - min_val
                if range_val == 0:
                    range_val = 1.0
                scaling_params[col] = {
                    "min": float(min_val),
                    "max": float(max_val),
                    "range": float(range_val)
                }
                
            elif method == 'robust':
                median = col_data.median()
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                # Avoid division by zero
                if iqr == 0:
                    iqr = 1.0
                scaling_params[col] = {
                    "median": float(median),
                    "q1": float(q1),
                    "q3": float(q3),
                    "iqr": float(iqr)
                }
                
            elif method == 'maxabs':
                max_abs = col_data.abs().max()
                # Avoid division by zero
                if max_abs == 0:
                    max_abs = 1.0
                scaling_params[col] = {
                    "max_abs": float(max_abs)
                }
        
        self._fit_metadata = {
            "method": method,
            "columns_processed": numeric_cols,
            "scaling_params": scaling_params,
            "feature_range": self.params.get('feature_range', (0, 1))
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply scaling to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with scaled features
        """
        self._check_is_fitted()
        
        result = data.copy()
        method = self._fit_metadata['method']
        scaling_params = self._fit_metadata['scaling_params']
        feature_range = self._fit_metadata.get('feature_range', (0, 1))
        
        scaled_columns = []
        
        for col, params in scaling_params.items():
            if col not in result.X.columns:
                continue
            
            original_dtype = result.X[col].dtype
            
            if method == 'standard':
                # z = (x - mean) / std
                result.X[col] = (result.X[col] - params['mean']) / params['std']
                
            elif method == 'minmax':
                # x_scaled = (x - min) / range * (max_range - min_range) + min_range
                min_range, max_range = feature_range
                x_std = (result.X[col] - params['min']) / params['range']
                result.X[col] = x_std * (max_range - min_range) + min_range
                
            elif method == 'robust':
                # x_scaled = (x - median) / IQR
                result.X[col] = (result.X[col] - params['median']) / params['iqr']
                
            elif method == 'maxabs':
                # x_scaled = x / max_abs
                result.X[col] = result.X[col] / params['max_abs']
            
            scaled_columns.append(col)
        
        # Update feature names (unchanged)
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "method": method,
            "columns_scaled": scaled_columns,
            "scaling_params_applied": scaling_params
        }
        
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
    
    def inverse_transform(self, data: DataContainer) -> DataContainer:
        """
        Reverse the scaling transformation.
        
        Args:
            data: DataContainer to inverse transform
            
        Returns:
            New DataContainer with original scale restored
        """
        self._check_is_fitted()
        
        result = data.copy()
        method = self._fit_metadata['method']
        scaling_params = self._fit_metadata['scaling_params']
        feature_range = self._fit_metadata.get('feature_range', (0, 1))
        
        for col, params in scaling_params.items():
            if col not in result.X.columns:
                continue
            
            if method == 'standard':
                # x = z * std + mean
                result.X[col] = result.X[col] * params['std'] + params['mean']
                
            elif method == 'minmax':
                # x = (x_scaled - min_range) / (max_range - min_range) * range + min
                min_range, max_range = feature_range
                x_std = (result.X[col] - min_range) / (max_range - min_range)
                result.X[col] = x_std * params['range'] + params['min']
                
            elif method == 'robust':
                # x = x_scaled * IQR + median
                result.X[col] = result.X[col] * params['iqr'] + params['median']
                
            elif method == 'maxabs':
                # x = x_scaled * max_abs
                result.X[col] = result.X[col] * params['max_abs']
        
        result.feature_names = result.X.columns.tolist()
        return result
