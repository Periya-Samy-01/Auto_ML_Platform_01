# apps/workers/worker/ml/preprocessors/ordinal_label_encoding.py
"""
Ordinal/Label Encoding Preprocessor.
Converts categorical columns into integer codes.
"""

from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np
from .base import BasePreprocessor, DataContainer


class OrdinalLabelEncodingPreprocessor(BasePreprocessor):
    """
    Encode categorical columns as integers.
    
    Two modes:
    - Label encoding: Arbitrary integer assignment (0, 1, 2, ...)
    - Ordinal encoding: User-defined order for ordered categories
    
    Parameters:
        columns (List[str], optional): Columns to encode.
            If None, encodes all categorical/object columns. Default: None
        mode (str): Encoding mode.
            - 'label': Automatic integer assignment based on sorted order
            - 'ordinal': Use custom order specified in 'ordinal_order'
            Default: 'label'
        ordinal_order (Dict[str, List], optional): For mode='ordinal', specify
            category order for each column. Example: {"size": ["S", "M", "L", "XL"]}
            Default: None
        handle_unknown (str): How to handle unknown categories during transform.
            - 'error': Raise error (default)
            - 'use_encoded_value': Assign a specific value (see unknown_value)
            Default: 'error'
        unknown_value (int): Value to assign to unknown categories when
            handle_unknown='use_encoded_value'. Default: -1
    
    Example:
        >>> # Label encoding (automatic)
        >>> preprocessor = OrdinalLabelEncodingPreprocessor(
        ...     name="label_encode",
        ...     params={"columns": ["city", "gender"], "mode": "label"}
        ... )
        >>> 
        >>> # Ordinal encoding (custom order)
        >>> preprocessor = OrdinalLabelEncodingPreprocessor(
        ...     name="ordinal_encode",
        ...     params={
        ...         "mode": "ordinal",
        ...         "ordinal_order": {"size": ["S", "M", "L", "XL"]}
        ...     }
        ... )
    """
    
    VALID_MODES = {'label', 'ordinal'}
    VALID_HANDLE_UNKNOWN = {'error', 'use_encoded_value'}
    
    def __init__(self, name: str = "ordinal_label_encoding", params: Optional[Dict[str, Any]] = None):
        """
        Initialize OrdinalLabelEncodingPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters
        """
        params = params or {}
        if 'columns' not in params:
            params['columns'] = None
        if 'mode' not in params:
            params['mode'] = 'label'
        if 'ordinal_order' not in params:
            params['ordinal_order'] = None
        if 'handle_unknown' not in params:
            params['handle_unknown'] = 'error'
        if 'unknown_value' not in params:
            params['unknown_value'] = -1
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """Validate configuration parameters."""
        columns = self.params.get('columns')
        if columns is not None and not isinstance(columns, list):
            raise ValueError(f"'columns' must be a list or None, got {type(columns).__name__}")
        
        mode = self.params.get('mode', 'label')
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of: {self.VALID_MODES}")
        
        ordinal_order = self.params.get('ordinal_order')
        if mode == 'ordinal' and ordinal_order is None:
            raise ValueError("'ordinal_order' is required when mode='ordinal'")
        
        if ordinal_order is not None and not isinstance(ordinal_order, dict):
            raise ValueError(f"'ordinal_order' must be a dict, got {type(ordinal_order).__name__}")
        
        handle_unknown = self.params.get('handle_unknown', 'error')
        if handle_unknown not in self.VALID_HANDLE_UNKNOWN:
            raise ValueError(
                f"Invalid 'handle_unknown': {handle_unknown}. "
                f"Must be one of: {self.VALID_HANDLE_UNKNOWN}"
            )
        
        unknown_value = self.params.get('unknown_value', -1)
        if not isinstance(unknown_value, int):
            raise ValueError(f"'unknown_value' must be an integer, got {type(unknown_value).__name__}")
    
    def fit(self, data: DataContainer) -> 'OrdinalLabelEncodingPreprocessor':
        """
        Learn encoding mappings from data.
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        columns = self.params.get('columns')
        mode = self.params.get('mode', 'label')
        ordinal_order = self.params.get('ordinal_order') or {}
        
        # Determine columns to encode
        if columns is None:
            if mode == 'ordinal':
                # For ordinal mode, only encode columns specified in ordinal_order
                categorical_cols = list(ordinal_order.keys())
            else:
                # For label mode, encode all categorical columns
                categorical_cols = data.get_categorical_columns()
        else:
            # Validate specified columns exist
            missing_cols = set(columns) - set(data.feature_names)
            if missing_cols:
                raise ValueError(f"Columns not found: {missing_cols}")
            categorical_cols = columns
        
        # Build encoding mappings
        encoding_maps = {}
        
        for col in categorical_cols:
            if mode == 'ordinal' and col in ordinal_order:
                # Use specified order
                categories = ordinal_order[col]
                encoding_maps[col] = {cat: idx for idx, cat in enumerate(categories)}
            else:
                # Label encoding: sort unique values
                unique_values = data.X[col].dropna().unique().tolist()
                try:
                    unique_values = sorted(unique_values)
                except TypeError:
                    pass  # Mixed types, keep original order
                encoding_maps[col] = {cat: idx for idx, cat in enumerate(unique_values)}
        
        # Build inverse mappings for decoding
        inverse_maps = {}
        for col, mapping in encoding_maps.items():
            inverse_maps[col] = {v: k for k, v in mapping.items()}
        
        self._fit_metadata = {
            "mode": mode,
            "columns_to_encode": list(encoding_maps.keys()),
            "encoding_maps": encoding_maps,
            "inverse_maps": inverse_maps
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply encoding to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with encoded columns
        """
        self._check_is_fitted()
        
        result = data.copy()
        encoding_maps = self._fit_metadata['encoding_maps']
        handle_unknown = self.params.get('handle_unknown', 'error')
        unknown_value = self.params.get('unknown_value', -1)
        
        columns_encoded = []
        unknown_categories_found = {}
        
        for col, mapping in encoding_maps.items():
            if col not in result.X.columns:
                continue
            
            # Check for unknown categories
            current_values = result.X[col].dropna().unique()
            unknown = set(current_values) - set(mapping.keys())
            
            if unknown:
                if handle_unknown == 'error':
                    raise ValueError(
                        f"Unknown categories found in column '{col}': {unknown}. "
                        f"Known categories: {list(mapping.keys())}"
                    )
                else:
                    unknown_categories_found[col] = list(unknown)
            
            # Apply encoding
            def encode_value(val):
                if pd.isna(val):
                    return np.nan
                if val in mapping:
                    return mapping[val]
                if handle_unknown == 'use_encoded_value':
                    return unknown_value
                return val  # Should not reach here
            
            result.X[col] = result.X[col].apply(encode_value)
            
            # Convert to nullable integer type to handle NaN
            result.X[col] = result.X[col].astype('Int64')
            
            columns_encoded.append(col)
        
        # Update feature names (columns unchanged, values changed)
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "columns_encoded": columns_encoded,
            "unknown_categories_found": unknown_categories_found,
            "encoding_maps_applied": {col: len(mapping) for col, mapping in encoding_maps.items()}
        }
        
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
    
    def inverse_transform(self, data: DataContainer) -> DataContainer:
        """
        Reverse the encoding transformation.
        
        Args:
            data: DataContainer to inverse transform
            
        Returns:
            New DataContainer with original category values restored
        """
        self._check_is_fitted()
        
        result = data.copy()
        inverse_maps = self._fit_metadata['inverse_maps']
        
        for col, mapping in inverse_maps.items():
            if col not in result.X.columns:
                continue
            
            def decode_value(val):
                if pd.isna(val):
                    return np.nan
                val_int = int(val) if not pd.isna(val) else val
                return mapping.get(val_int, val)
            
            result.X[col] = result.X[col].apply(decode_value)
        
        result.feature_names = result.X.columns.tolist()
        return result
