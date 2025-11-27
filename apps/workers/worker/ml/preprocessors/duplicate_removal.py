# apps/workers/worker/ml/preprocessors/duplicate_removal.py
"""
Duplicate Removal Preprocessor.
Removes duplicate rows from the dataset.
"""

from typing import Dict, Any, Optional, List
from .base import BasePreprocessor, DataContainer


class DuplicateRemovalPreprocessor(BasePreprocessor):
    """
    Remove duplicate rows from the dataset.
    
    Parameters:
        subset (List[str], optional): Column names to consider for identifying duplicates.
            If None, all columns are used. Default: None
        keep (str): Which duplicates to keep.
            - 'first': Keep first occurrence (default)
            - 'last': Keep last occurrence
            - False: Drop all duplicates
            Default: 'first'
    
    Example:
        >>> preprocessor = DuplicateRemovalPreprocessor(
        ...     name="remove_duplicates",
        ...     params={"subset": ["id", "name"], "keep": "first"}
        ... )
        >>> result = preprocessor.fit_transform(data)
    """
    
    # Valid values for 'keep' parameter
    VALID_KEEP_VALUES = {'first', 'last', False}
    
    def __init__(self, name: str = "duplicate_removal", params: Optional[Dict[str, Any]] = None):
        """
        Initialize DuplicateRemovalPreprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration with 'subset' and 'keep' options
        """
        # Set defaults before validation
        params = params or {}
        if 'subset' not in params:
            params['subset'] = None
        if 'keep' not in params:
            params['keep'] = 'first'
        
        super().__init__(name=name, params=params)
    
    def _validate_params(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate 'keep' parameter
        keep = self.params.get('keep', 'first')
        if keep not in self.VALID_KEEP_VALUES:
            raise ValueError(
                f"Invalid 'keep' value: {keep}. "
                f"Must be one of: {self.VALID_KEEP_VALUES}"
            )
        
        # Validate 'subset' parameter
        subset = self.params.get('subset')
        if subset is not None:
            if not isinstance(subset, list):
                raise ValueError(
                    f"'subset' must be a list of column names or None, "
                    f"got {type(subset).__name__}"
                )
            if len(subset) == 0:
                raise ValueError("'subset' cannot be an empty list. Use None for all columns.")
    
    def fit(self, data: DataContainer) -> 'DuplicateRemovalPreprocessor':
        """
        Fit preprocessor (validates subset columns exist).
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        # Validate subset columns exist in data
        subset = self.params.get('subset')
        if subset is not None:
            missing_cols = set(subset) - set(data.feature_names)
            if missing_cols:
                raise ValueError(
                    f"Columns not found in data: {missing_cols}. "
                    f"Available columns: {data.feature_names}"
                )
        
        # Store fit metadata
        self._fit_metadata = {
            "columns_checked": subset or data.feature_names,
            "original_row_count": data.n_samples
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Remove duplicate rows from data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            New DataContainer with duplicates removed
            
        Raises:
            RuntimeError: If fit() not called first
        """
        self._check_is_fitted()
        
        # Create copy to avoid modifying original
        result = data.copy()
        
        # Get parameters
        subset = self.params.get('subset')
        keep = self.params.get('keep')
        
        # Count duplicates before removal
        original_count = len(result.X)
        
        # Find duplicate indices
        duplicate_mask = result.X.duplicated(subset=subset, keep=keep)
        duplicates_count = duplicate_mask.sum()
        
        # Remove duplicates from X
        result.X = result.X[~duplicate_mask].reset_index(drop=True)
        
        # Remove corresponding rows from y if present
        if result.y is not None:
            result.y = result.y[~duplicate_mask].reset_index(drop=True)
        
        # Update feature names (columns unchanged, just rows removed)
        result.feature_names = result.X.columns.tolist()
        
        # Store transform metadata
        self._transform_metadata = {
            "rows_before": original_count,
            "rows_after": len(result.X),
            "duplicates_removed": int(duplicates_count),
            "columns_checked": subset or "all"
        }
        
        # Add record to data's preprocessing history
        result.add_preprocessing_record(
            preprocessor_name=self.name,
            params=self.params,
            changes=self._transform_metadata
        )
        
        return result
