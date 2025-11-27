# apps/workers/worker/ml/preprocessors/outlier_handling.py
"""
Outlier Handling Preprocessor.
Detects and handles outliers using various methods.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class OutlierHandlingPreprocessor(BasePreprocessor):
    """
    Detect and handle outliers in the dataset.
    
    Parameters:
        method (str): Outlier detection method.
            - 'iqr': Interquartile Range method (default)
            - 'zscore': Z-score method
            Default: 'iqr'
        action (str): How to handle detected outliers.
            - 'remove': Remove rows containing outliers
            - 'clip': Clip outliers to boundary values
            - 'nan': Replace outliers with NaN
            Default: 'clip'
        columns (List[str], optional): Columns to check for outliers.
            If None, applies to all numeric columns. Default: None
        threshold (float): Threshold for outlier detection.
            - For 'iqr': Multiplier for IQR (default: 1.5)
            - For 'zscore': Number of standard deviations (default: 3.0)
    
    Example:
        >>> preprocessor = OutlierHandlingPreprocessor(
        ...     name="handle_outliers",
        ...     params={"method": "iqr", "action": "clip", "threshold": 1.5}
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    VALID_METHODS = {'iqr', 'zscore'}
    VALID_ACTIONS = {'remove', 'clip', 'nan'}
    
    def __init__(self, name: str = "outlier_handling", params: Optional[Dict[str, Any]] = None):
        """
        Initialize OutlierHandlingPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters
        """
        params = params or {}
        if 'method' not in params:
            params['method'] = 'iqr'
        if 'action' not in params:
            params['action'] = 'clip'
        if 'columns' not in params:
            params['columns'] = None
        if 'threshold' not in params:
            # Default threshold depends on method
            params['threshold'] = 1.5 if params['method'] == 'iqr' else 3.0
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """Validate configuration parameters."""
        method = self.params.get('method', 'iqr')
        if method not in self.VALID_METHODS:
            raise ValueError(
                f"Invalid method: {method}. Must be one of: {self.VALID_METHODS}"
            )
        
        action = self.params.get('action', 'clip')
        if action not in self.VALID_ACTIONS:
            raise ValueError(
                f"Invalid action: {action}. Must be one of: {self.VALID_ACTIONS}"
            )
        
        threshold = self.params.get('threshold', 1.5)
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            raise ValueError(f"'threshold' must be a positive number, got {threshold}")
        
        columns = self.params.get('columns')
        if columns is not None and not isinstance(columns, list):
            raise ValueError(f"'columns' must be a list or None, got {type(columns).__name__}")
    
    def fit(self, data: DataContainer) -> 'OutlierHandlingPreprocessor':
        """
        Learn outlier boundaries from data.
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        method = self.params.get('method')
        threshold = self.params.get('threshold')
        columns = self.params.get('columns')
        
        # Determine columns to process
        if columns is None:
            # Use all numeric columns
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
                    raise ValueError(f"Column '{col}' is not numeric. Outlier detection requires numeric columns.")
        
        # Calculate boundaries for each column
        boundaries = {}
        
        for col in numeric_cols:
            col_data = data.X[col].dropna()
            
            if method == 'iqr':
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                
                boundaries[col] = {
                    "lower": float(lower),
                    "upper": float(upper),
                    "q1": float(q1),
                    "q3": float(q3),
                    "iqr": float(iqr)
                }
                
            elif method == 'zscore':
                mean = col_data.mean()
                std = col_data.std()
                lower = mean - threshold * std
                upper = mean + threshold * std
                
                boundaries[col] = {
                    "lower": float(lower),
                    "upper": float(upper),
                    "mean": float(mean),
                    "std": float(std)
                }
        
        self._fit_metadata = {
            "method": method,
            "threshold": threshold,
            "columns_processed": numeric_cols,
            "boundaries": boundaries
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply outlier handling to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with outliers handled
        """
        self._check_is_fitted()
        
        result = data.copy()
        action = self.params.get('action')
        boundaries = self._fit_metadata['boundaries']
        
        rows_before = len(result.X)
        outlier_stats = {}
        rows_with_outliers = pd.Series([False] * len(result.X))
        
        for col, bounds in boundaries.items():
            if col not in result.X.columns:
                continue
            
            lower = bounds['lower']
            upper = bounds['upper']
            
            # Detect outliers
            is_outlier = (result.X[col] < lower) | (result.X[col] > upper)
            outlier_count = is_outlier.sum()
            
            outlier_stats[col] = {
                "outliers_detected": int(outlier_count),
                "lower_bound": lower,
                "upper_bound": upper
            }
            
            if action == 'remove':
                rows_with_outliers = rows_with_outliers | is_outlier
                
            elif action == 'clip':
                result.X[col] = result.X[col].clip(lower=lower, upper=upper)
                
            elif action == 'nan':
                result.X.loc[is_outlier, col] = np.nan
        
        # Remove rows if action is 'remove'
        if action == 'remove':
            result.X = result.X[~rows_with_outliers].reset_index(drop=True)
            if result.y is not None:
                result.y = result.y[~rows_with_outliers].reset_index(drop=True)
        
        # Update feature names
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        total_outliers = sum(stats['outliers_detected'] for stats in outlier_stats.values())
        
        self._transform_metadata = {
            "action": action,
            "rows_before": rows_before,
            "rows_after": len(result.X),
            "rows_removed": rows_before - len(result.X),
            "total_outliers_detected": total_outliers,
            "outlier_stats": outlier_stats
        }
        
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
