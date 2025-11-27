#apps/workers/worker/ml/trainers/pca.py
"""
PCA (Principal Component Analysis) trainer for dimensionality reduction.
Transforms features into lower-dimensional space.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.decomposition import PCA

from .base import BaseTrainer
from apps.workers.worker.constants import MODEL_TYPE_DIMENSIONALITY, TASK_DIMENSIONALITY_REDUCTION
from apps.workers.worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from apps.workers.worker.ml.utils.validation import validate_positive_integer


class PCATrainer(BaseTrainer):
    """
    PCA (Principal Component Analysis) trainer (unsupervised).
    
    Supports:
    - Dimensionality reduction
    - Feature transformation to lower dimensions
    - Variance-based feature extraction
    
    Note: 
    - This is unsupervised - y is ignored during fit()
    - predict() returns transformed features (wraps transform())
    
    Default hyperparameters:
    - n_components: 2 (reduce to 2 dimensions, minimal)
    - random_state: 42 (for reproducibility)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize PCA trainer.
        
        Args:
            name: Model name
            task: Must be "dimensionality_reduction"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set minimal defaults (for compute cost)
        defaults = {
            "n_components": 2,
            "random_state": 42,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'PCATrainer':
        """
        Train PCA model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Ignored (unsupervised learning)
            
        Returns:
            self: For method chaining
        """
        # Validate inputs (y is optional for unsupervised)
        validate_fit_input(X, y, self.task)
        
        # Create and train model (y is ignored)
        self.model = PCA(**self.hyperparameters)
        self.model.fit(X)
        
        # Update metadata (y is None for unsupervised)
        self._update_metadata(X, None)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Transform features to reduced dimensionality.
        
        Note: PCA doesn't have predict() - this wraps transform().
        
        Args:
            X: Features to transform (n_samples, n_features)
            
        Returns:
            Transformed features (n_samples, n_components)
        """
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        # predict() wraps transform() for PCA
        return self.model.transform(X)
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - sklearn handles specific value validation.
        """
        # Validate n_components
        if "n_components" in self.hyperparameters:
            n_components = self.hyperparameters["n_components"]
            # Can be int, float (fraction), or None
            if isinstance(n_components, int):
                validate_positive_integer(n_components, "n_components")
            # If float (fraction of variance) or None, sklearn will validate
        
        # Note: We don't validate svd_solver, whiten, etc. - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "dimensionality" - PCA is a dimensionality reduction algorithm
        """
        return MODEL_TYPE_DIMENSIONALITY