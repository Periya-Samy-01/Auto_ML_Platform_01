# apps/workers/worker/ml/preprocessors/one_hot_encoding.py
"""
One-Hot Encoding Preprocessor.
Converts categorical columns into binary columns.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class OneHotEncodingPreprocessor(BasePreprocessor):
    """
    One-hot encode categorical columns.
    
    Creates binary columns for each unique category value.
    
    Parameters:
        columns (List[str], optional): Columns to encode.
            If None, encodes all categorical/object columns. Default: None
        drop_first (bool): Whether to drop first category to avoid multicollinearity.
            Default: False
        max_categories (int, optional): Maximum unique values per column.
            Columns with more categories are skipped. Default: None (no limit)
        handle_unknown (str): How to handle unknown categories during transform.
            - 'error': Raise error (default)
            - 'ignore': Set all encoded columns to 0
            Default: 'error'
        sparse (bool): Whether to create sparse output (not implemented, always dense).
            Default: False
    
    Example:
        >>> preprocessor = OneHotEncodingPreprocessor(
        ...     name="onehot_encode",
        ...     params={"columns": ["city", "gender"], "drop_first": True}
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    VALID_HANDLE_UNKNOWN = {'error', 'ignore'}
    
    def __init__(self, name: str = "one_hot_encoding", params: Optional[Dict[str, Any]] = None):
        """
        Initialize OneHotEncodingPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters
        """
        params = params or {}
        if 'columns' not in params:
            params['columns'] = None
        if 'drop_first' not in params:
            params['drop_first'] = False
        if 'max_categories' not in params:
            params['max_categories'] = None
        if 'handle_unknown' not in params:
            params['handle_unknown'] = 'error'
        if 'sparse' not in params:
            params['sparse'] = False
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """Validate configuration parameters."""
        columns = self.params.get('columns')
        if columns is not None and not isinstance(columns, list):
            raise ValueError(f"'columns' must be a list or None, got {type(columns).__name__}")
        
        drop_first = self.params.get('drop_first', False)
        if not isinstance(drop_first, bool):
            raise ValueError(f"'drop_first' must be boolean, got {type(drop_first).__name__}")
        
        max_categories = self.params.get('max_categories')
        if max_categories is not None:
            if not isinstance(max_categories, int) or max_categories < 2:
                raise ValueError(f"'max_categories' must be an integer >= 2 or None, got {max_categories}")
        
        handle_unknown = self.params.get('handle_unknown', 'error')
        if handle_unknown not in self.VALID_HANDLE_UNKNOWN:
            raise ValueError(
                f"Invalid 'handle_unknown': {handle_unknown}. "
                f"Must be one of: {self.VALID_HANDLE_UNKNOWN}"
            )
    
    def fit(self, data: DataContainer) -> 'OneHotEncodingPreprocessor':
        """
        Learn category values from data.
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        columns = self.params.get('columns')
        max_categories = self.params.get('max_categories')
        
        # Determine columns to encode
        if columns is None:
            categorical_cols = data.get_categorical_columns()
        else:
            # Validate specified columns exist
            missing_cols = set(columns) - set(data.feature_names)
            if missing_cols:
                raise ValueError(f"Columns not found: {missing_cols}")
            categorical_cols = columns
        
        # Learn categories for each column
        categories = {}
        skipped_columns = []
        
        for col in categorical_cols:
            unique_values = data.X[col].dropna().unique().tolist()
            n_unique = len(unique_values)
            
            # Skip if too many categories
            if max_categories is not None and n_unique > max_categories:
                skipped_columns.append({
                    "column": col,
                    "reason": f"Too many categories ({n_unique} > {max_categories})"
                })
                continue
            
            # Sort for consistent ordering
            try:
                unique_values = sorted(unique_values)
            except TypeError:
                # Mixed types, keep original order
                pass
            
            categories[col] = unique_values
        
        self._fit_metadata = {
            "columns_to_encode": list(categories.keys()),
            "categories": categories,
            "skipped_columns": skipped_columns,
            "drop_first": self.params.get('drop_first', False)
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply one-hot encoding to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with encoded columns
        """
        self._check_is_fitted()
        
        result = data.copy()
        categories = self._fit_metadata['categories']
        drop_first = self._fit_metadata['drop_first']
        handle_unknown = self.params.get('handle_unknown', 'error')
        
        columns_encoded = []
        new_columns_created = []
        unknown_categories_found = {}
        
        for col, known_categories in categories.items():
            if col not in result.X.columns:
                continue
            
            # Check for unknown categories
            current_values = result.X[col].dropna().unique()
            unknown = set(current_values) - set(known_categories)
            
            if unknown:
                if handle_unknown == 'error':
                    raise ValueError(
                        f"Unknown categories found in column '{col}': {unknown}. "
                        f"Known categories: {known_categories}"
                    )
                else:
                    unknown_categories_found[col] = list(unknown)
            
            # Create one-hot encoded columns
            categories_to_encode = known_categories[1:] if drop_first else known_categories
            
            for category in categories_to_encode:
                new_col_name = f"{col}_{category}"
                result.X[new_col_name] = (result.X[col] == category).astype(int)
                new_columns_created.append(new_col_name)
            
            # Drop original column
            result.X = result.X.drop(columns=[col])
            columns_encoded.append(col)
        
        # Update feature names
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "columns_encoded": columns_encoded,
            "new_columns_created": new_columns_created,
            "columns_removed": columns_encoded,
            "unknown_categories_found": unknown_categories_found,
            "total_new_columns": len(new_columns_created)
        }
        
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
