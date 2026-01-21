# apps/workers/worker/ml/preprocessors/base.py
"""
Base classes for preprocessing module.
Contains DataContainer for standardized data format and BasePreprocessor abstract class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import json
import joblib
import copy


class DataContainer:
    """
    Standardized data container for passing data between preprocessors.
    
    Keeps data as DataFrame to preserve column names for preprocessing operations.
    Trainers can convert to ndarray internally as needed.
    
    Attributes:
        X (pd.DataFrame): Feature matrix with column names preserved
        y (Optional[pd.Series]): Target series (None for unsupervised)
        feature_names (List[str]): List of feature column names
        target_name (Optional[str]): Name of target column
        metadata (Dict): Tracks preprocessing history and transformations applied
    """
    
    def __init__(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
        target_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize DataContainer.
        
        Args:
            X: Feature DataFrame
            y: Target Series (optional)
            target_name: Name of target column (optional)
            metadata: Initial metadata dict (optional)
        """
        # Validate X is DataFrame
        if not isinstance(X, pd.DataFrame):
            raise TypeError(f"X must be pd.DataFrame, got {type(X).__name__}")
        
        # Validate y if provided
        if y is not None and not isinstance(y, pd.Series):
            # Convert to Series if ndarray
            if isinstance(y, np.ndarray):
                y = pd.Series(y, name=target_name)
            else:
                raise TypeError(f"y must be pd.Series or np.ndarray, got {type(y).__name__}")
        
        self.X = X.copy()
        self.y = y.copy() if y is not None else None
        self.feature_names = X.columns.tolist()
        self.target_name = target_name
        self.metadata = metadata or {
            "created_at": datetime.now().isoformat(),
            "preprocessing_history": [],
            "original_shape": X.shape,
            "current_shape": X.shape
        }
    
    @property
    def shape(self) -> tuple:
        """Return shape of feature matrix."""
        return self.X.shape
    
    @property
    def n_samples(self) -> int:
        """Return number of samples."""
        return self.X.shape[0]
    
    @property
    def n_features(self) -> int:
        """Return number of features."""
        return self.X.shape[1]
    
    def copy(self) -> 'DataContainer':
        """
        Create a deep copy of the DataContainer.
        
        Returns:
            New DataContainer with copied data
        """
        return DataContainer(
            X=self.X.copy(),
            y=self.y.copy() if self.y is not None else None,
            target_name=self.target_name,
            metadata=copy.deepcopy(self.metadata)
        )
    
    def add_preprocessing_record(
        self,
        preprocessor_name: str,
        params: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> None:
        """
        Record a preprocessing step in metadata.
        
        Args:
            preprocessor_name: Name of the preprocessor applied
            params: Parameters used
            changes: What was changed (e.g., rows dropped, columns added)
        """
        record = {
            "preprocessor": preprocessor_name,
            "params": params,
            "changes": changes,
            "applied_at": datetime.now().isoformat(),
            "shape_after": self.X.shape
        }
        self.metadata["preprocessing_history"].append(record)
        self.metadata["current_shape"] = self.X.shape
    
    def to_csv(
        self,
        path: str,
        include_target: bool = True,
        save_metadata: bool = True
    ) -> str:
        """
        Save data to CSV file and optionally metadata to JSON.
        
        Args:
            path: Output path (without extension)
            include_target: Whether to include target column in CSV
            save_metadata: Whether to save metadata JSON alongside
            
        Returns:
            Path to saved CSV file
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare DataFrame for saving
        if include_target and self.y is not None:
            df = self.X.copy()
            df[self.target_name] = self.y
        else:
            df = self.X
        
        # Save CSV
        csv_path = output_path.with_suffix('.csv')
        df.to_csv(csv_path, index=False)
        
        # Save metadata
        if save_metadata:
            metadata_path = output_path.with_suffix('.meta.json')
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        
        return str(csv_path)
    
    @classmethod
    def from_csv(
        cls,
        path: str,
        target_col: Optional[str] = None,
        load_metadata: bool = True
    ) -> 'DataContainer':
        """
        Load DataContainer from CSV file.
        
        Args:
            path: Path to CSV file
            target_col: Name of target column (None for unsupervised)
            load_metadata: Whether to load metadata JSON if exists
            
        Returns:
            DataContainer instance
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If target column not found
        """
        csv_path = Path(path)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        
        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Extract target if specified
        if target_col is not None:
            if target_col not in df.columns:
                available = ", ".join(df.columns.tolist())
                raise ValueError(
                    f"Target column '{target_col}' not found.\n"
                    f"Available columns: {available}"
                )
            y = df[target_col]
            X = df.drop(columns=[target_col])
        else:
            X = df
            y = None
        
        # Load metadata if exists
        metadata = None
        if load_metadata:
            metadata_path = csv_path.with_suffix('.meta.json')
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
        
        return cls(X=X, y=y, target_name=target_col, metadata=metadata)
    
    def get_numeric_columns(self) -> List[str]:
        """Return list of numeric column names."""
        return self.X.select_dtypes(include=[np.number]).columns.tolist()
    
    def get_categorical_columns(self) -> List[str]:
        """Return list of categorical/object column names."""
        return self.X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def get_datetime_columns(self) -> List[str]:
        """Return list of datetime column names."""
        return self.X.select_dtypes(include=['datetime64']).columns.tolist()
    
    def __repr__(self) -> str:
        """String representation."""
        target_info = f", target='{self.target_name}'" if self.target_name else ""
        return f"DataContainer(shape={self.shape}, features={len(self.feature_names)}{target_info})"


class BasePreprocessor(ABC):
    """
    Abstract base class for all preprocessors.
    
    All preprocessors must inherit from this class and implement:
    - fit(): Learn parameters from data
    - transform(): Apply transformation
    - _validate_params(): Validate configuration parameters
    
    Follows scikit-learn fit/transform pattern for consistency.
    
    Attributes:
        name (str): Preprocessor name
        params (Dict[str, Any]): Configuration parameters
        is_fitted (bool): Whether fit() has been called
        _fit_metadata (Dict): Parameters learned during fit (e.g., mean values)
        _transform_metadata (Dict): Changes made during last transform
    """
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize preprocessor.
        
        Args:
            name: Preprocessor name
            params: Configuration parameters (default: {})
        """
        self.name = name
        self.params = params or {}
        self.is_fitted = False
        self._fit_metadata: Dict[str, Any] = {}
        self._transform_metadata: Dict[str, Any] = {}
        
        # Validate parameters on initialization
        self._validate_params()
    
    @abstractmethod
    def fit(self, data: DataContainer) -> 'BasePreprocessor':
        """
        Learn parameters from data (e.g., mean for imputation).
        
        Args:
            data: DataContainer to fit on
            
        Returns:
            self: For method chaining
        """
        pass
    
    @abstractmethod
    def transform(self, data: DataContainer) -> DataContainer:
        """
        Apply transformation to data.
        
        Args:
            data: DataContainer to transform
            
        Returns:
            Transformed DataContainer (new instance)
            
        Raises:
            RuntimeError: If fit() not called first
        """
        pass
    
    @abstractmethod
    def _validate_params(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If parameters are invalid
        """
        pass
    
    def fit_transform(self, data: DataContainer) -> DataContainer:
        """
        Fit and transform in one step.
        
        Args:
            data: DataContainer to fit and transform
            
        Returns:
            Transformed DataContainer
        """
        self.fit(data)
        return self.transform(data)
    
    def get_fit_metadata(self) -> Dict[str, Any]:
        """
        Get parameters learned during fit.
        
        Returns:
            Dictionary of fit metadata
        """
        return self._fit_metadata.copy()
    
    def get_transform_metadata(self) -> Dict[str, Any]:
        """
        Get changes made during last transform.
        
        Returns:
            Dictionary of transform metadata
        """
        return self._transform_metadata.copy()
    
    def update_params(self, new_params: Dict[str, Any]) -> None:
        """
        Update configuration parameters (requires refit).
        
        Args:
            new_params: New parameter values
            
        Raises:
            ValueError: If new parameters are invalid
        """
        self.params.update(new_params)
        self._validate_params()
        self.is_fitted = False  # Require refit after param change
    
    def save(self, path: str) -> None:
        """
        Save fitted preprocessor to disk.
        
        Args:
            path: Directory path to save (creates if doesn't exist)
        """
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save fit metadata with joblib (may contain numpy arrays)
        fit_path = save_path / "fit_state.joblib"
        joblib.dump(self._fit_metadata, fit_path)
        
        # Save config as JSON
        config_path = save_path / "config.json"
        config = {
            "name": self.name,
            "params": self.params,
            "is_fitted": self.is_fitted
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)
    
    @classmethod
    def load(cls, path: str) -> 'BasePreprocessor':
        """
        Load fitted preprocessor from disk.
        
        Args:
            path: Directory path containing saved preprocessor
            
        Returns:
            Loaded preprocessor instance
        """
        load_path = Path(path)
        
        # Load config
        config_path = load_path / "config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create instance
        instance = cls(name=config["name"], params=config["params"])
        instance.is_fitted = config["is_fitted"]
        
        # Load fit metadata
        fit_path = load_path / "fit_state.joblib"
        if fit_path.exists():
            instance._fit_metadata = joblib.load(fit_path)
        
        return instance
    
    def _check_is_fitted(self) -> None:
        """
        Check if preprocessor is fitted.
        
        Raises:
            RuntimeError: If not fitted
        """
        if not self.is_fitted:
            raise RuntimeError(
                f"{self.name} is not fitted. Call fit() before transform()."
            )
    
    def __repr__(self) -> str:
        """String representation."""
        fitted_str = "fitted" if self.is_fitted else "not fitted"
        return f"{self.__class__.__name__}(name='{self.name}', {fitted_str})"
