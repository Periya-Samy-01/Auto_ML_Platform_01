# apps/workers/worker/ml/preprocessors/missing_value_imputation.py
"""
Missing Value Imputation Preprocessor.
Handles missing values through various strategies.
"""

from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class MissingValueImputationPreprocessor(BasePreprocessor):
    """
    Handle missing values in the dataset.
    
    Parameters:
        strategy (str): Imputation strategy.
            - 'drop_rows': Remove rows with missing values
            - 'drop_cols': Remove columns with missing values above threshold
            - 'mean': Fill with column mean (numeric only)
            - 'median': Fill with column median (numeric only)
            - 'mode': Fill with most frequent value
            - 'constant': Fill with a constant value
            Default: 'mean'
        columns (List[str], optional): Columns to apply imputation to.
            If None, applies to all columns with missing values. Default: None
        threshold (float): For 'drop_rows'/'drop_cols', drop if missing ratio exceeds this.
            Range: 0.0 to 1.0. Default: 0.0 (drop if any missing)
        fill_value (Any): Value to use when strategy='constant'. Default: 0
    
    Example:
        >>> preprocessor = MissingValueImputationPreprocessor(
        ...     name="impute_missing",
        ...     params={"strategy": "mean", "columns": ["age", "income"]}
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    VALID_STRATEGIES = {'drop_rows', 'drop_cols', 'mean', 'median', 'mode', 'constant'}
    
    def __init__(self, name: str = "missing_value_imputation", params: Optional[Dict[str, Any]] = None):
        """
        Initialize MissingValueImputationPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters
        """
        params = params or {}
        if 'strategy' not in params:
            params['strategy'] = 'mean'
        if 'columns' not in params:
            params['columns'] = None
        if 'threshold' not in params:
            params['threshold'] = 0.0
        if 'fill_value' not in params:
            params['fill_value'] = 0
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """Validate configuration parameters."""
        strategy = self.params.get('strategy', 'mean')
        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(
                f"Invalid strategy: {strategy}. "
                f"Must be one of: {self.VALID_STRATEGIES}"
            )
        
        threshold = self.params.get('threshold', 0.0)
        if not isinstance(threshold, (int, float)) or not 0.0 <= threshold <= 1.0:
            raise ValueError(
                f"'threshold' must be a float between 0.0 and 1.0, got {threshold}"
            )
        
        columns = self.params.get('columns')
        if columns is not None and not isinstance(columns, list):
            raise ValueError(
                f"'columns' must be a list or None, got {type(columns).__name__}"
            )
    
    def fit(self, data: DataContainer) -> 'MissingValueImputationPreprocessor':
        """
        Learn imputation values from data.
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        strategy = self.params.get('strategy')
        columns = self.params.get('columns')
        
        # Determine columns to process
        if columns is None:
            # Find columns with missing values
            cols_with_missing = data.X.columns[data.X.isna().any()].tolist()
        else:
            # Validate specified columns exist
            missing_cols = set(columns) - set(data.feature_names)
            if missing_cols:
                raise ValueError(
                    f"Columns not found: {missing_cols}. "
                    f"Available: {data.feature_names}"
                )
            cols_with_missing = columns
        
        # Calculate imputation values based on strategy
        imputation_values = {}
        
        if strategy == 'mean':
            for col in cols_with_missing:
                if pd.api.types.is_numeric_dtype(data.X[col]):
                    imputation_values[col] = data.X[col].mean()
                    
        elif strategy == 'median':
            for col in cols_with_missing:
                if pd.api.types.is_numeric_dtype(data.X[col]):
                    imputation_values[col] = data.X[col].median()
                    
        elif strategy == 'mode':
            for col in cols_with_missing:
                mode_result = data.X[col].mode()
                if len(mode_result) > 0:
                    imputation_values[col] = mode_result.iloc[0]
                    
        elif strategy == 'constant':
            fill_value = self.params.get('fill_value', 0)
            for col in cols_with_missing:
                imputation_values[col] = fill_value
        
        # Calculate missing value statistics
        missing_stats = {}
        for col in data.feature_names:
            missing_count = data.X[col].isna().sum()
            missing_stats[col] = {
                "count": int(missing_count),
                "ratio": float(missing_count / len(data.X))
            }
        
        self._fit_metadata = {
            "strategy": strategy,
            "columns_processed": cols_with_missing,
            "imputation_values": imputation_values,
            "missing_stats": missing_stats,
            "original_row_count": data.n_samples
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply imputation to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with missing values handled
        """
        self._check_is_fitted()
        
        result = data.copy()
        strategy = self.params.get('strategy')
        threshold = self.params.get('threshold', 0.0)
        
        rows_before = len(result.X)
        cols_before = len(result.X.columns)
        values_imputed = {}
        
        if strategy == 'drop_rows':
            # Drop rows with missing values above threshold
            columns = self._fit_metadata['columns_processed']
            if columns:
                # Calculate missing ratio per row for specified columns
                missing_per_row = result.X[columns].isna().sum(axis=1) / len(columns)
                rows_to_keep = missing_per_row <= threshold
            else:
                # No columns with missing values
                rows_to_keep = pd.Series([True] * len(result.X))
            
            result.X = result.X[rows_to_keep].reset_index(drop=True)
            if result.y is not None:
                result.y = result.y[rows_to_keep].reset_index(drop=True)
                
        elif strategy == 'drop_cols':
            # Drop columns with missing values above threshold
            cols_to_drop = []
            for col, stats in self._fit_metadata['missing_stats'].items():
                if stats['ratio'] > threshold:
                    cols_to_drop.append(col)
            
            result.X = result.X.drop(columns=cols_to_drop)
            result.feature_names = result.X.columns.tolist()
            
        else:
            # Imputation strategies (mean, median, mode, constant)
            imputation_values = self._fit_metadata['imputation_values']
            
            for col, fill_value in imputation_values.items():
                if col in result.X.columns:
                    missing_count = result.X[col].isna().sum()
                    if missing_count > 0:
                        result.X[col] = result.X[col].fillna(fill_value)
                        values_imputed[col] = {
                            "count": int(missing_count),
                            "fill_value": fill_value if not isinstance(fill_value, (np.floating, np.integer)) else float(fill_value)
                        }
        
        # Update feature names
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "strategy": strategy,
            "rows_before": rows_before,
            "rows_after": len(result.X),
            "rows_dropped": rows_before - len(result.X),
            "cols_before": cols_before,
            "cols_after": len(result.X.columns),
            "cols_dropped": cols_before - len(result.X.columns),
            "values_imputed": values_imputed
        }
        
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
