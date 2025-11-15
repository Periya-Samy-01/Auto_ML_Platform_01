#apps/workers/worker/ml/trainers/knn.py
"""
K-Nearest Neighbors trainer for classification and regression.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

from .base import BaseTrainer
from worker.constants import MODEL_TYPE_DISTANCE, TASK_CLASSIFICATION, TASK_REGRESSION
from worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from worker.ml.utils.validation import validate_positive_integer


class KNNTrainer(BaseTrainer):
    """
    K-Nearest Neighbors trainer (dual-task).
    
    Supports:
    - Classification (with predict_proba)
    - Regression
    - Distance-based predictions
    
    Task-aware: Instantiates KNeighborsClassifier or KNeighborsRegressor based on task.
    
    Default hyperparameters:
    - n_neighbors: 5 (number of neighbors)
    - weights: "uniform" (or "distance" for distance-weighted)
    - metric: "euclidean" (distance metric)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize KNN trainer.
        
        Args:
            name: Model name
            task: "classification" or "regression"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set defaults
        defaults = {
            "n_neighbors": 5,
            "weights": "uniform",
            "metric": "euclidean",
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'KNNTrainer':
        """
        Train KNN model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training labels/targets (n_samples,)
            
        Returns:
            self: For method chaining
        """
        # Validate inputs
        validate_fit_input(X, y, self.task)
        
        # Task-aware model selection
        if self.task == TASK_CLASSIFICATION:
            self.model = KNeighborsClassifier(**self.hyperparameters)
        elif self.task == TASK_REGRESSION:
            self.model = KNeighborsRegressor(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported task for KNN: {self.task}")
        
        # Train model
        self.model.fit(X, y)
        
        # Update metadata
        self._update_metadata(X, y)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels or regression values.
        
        Args:
            X: Features to predict on (n_samples, n_features)
            
        Returns:
            Predicted class labels (classification) or values (regression)
        """
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities (classification only).
        
        Args:
            X: Features to predict on (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
            
        Raises:
            NotImplementedError: If task is regression
        """
        if self.task != TASK_CLASSIFICATION:
            raise NotImplementedError("predict_proba only available for classification task")
        
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        return self.model.predict_proba(X)
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - sklearn handles specific value validation.
        """
        # Validate n_neighbors (must be positive integer)
        if "n_neighbors" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["n_neighbors"], "n_neighbors")
        
        # Note: We don't validate weights or metric - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "distance" - KNN is a distance-based model
        """
        return MODEL_TYPE_DISTANCE