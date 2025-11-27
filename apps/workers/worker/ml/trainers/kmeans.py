#apps/workers/worker/ml/trainers/kmeans.py
"""
K-Means clustering trainer for unsupervised learning.
Groups data into k clusters based on distance.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.cluster import KMeans

from .base import BaseTrainer
from apps.workers.worker.constants import MODEL_TYPE_CLUSTERING, TASK_CLUSTERING
from apps.workers.worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from apps.workers.worker.ml.utils.validation import validate_positive_integer


class KMeansTrainer(BaseTrainer):
    """
    K-Means clustering trainer (unsupervised).
    
    Supports:
    - Unsupervised clustering
    - Distance-based grouping
    - Cluster ID predictions
    
    Note: This is unsupervised - y is ignored during fit().
    
    Default hyperparameters:
    - n_clusters: 3 (number of clusters, minimal)
    - max_iter: 100 (maximum iterations, minimal)
    - n_init: 5 (number of initializations, minimal for speed)
    - random_state: 42 (for reproducibility)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize K-Means trainer.
        
        Args:
            name: Model name
            task: Must be "clustering"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set minimal defaults (for compute cost)
        defaults = {
            "n_clusters": 3,
            "max_iter": 100,
            "n_init": 5,
            "random_state": 42,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'KMeansTrainer':
        """
        Train K-Means clustering model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Ignored (unsupervised learning)
            
        Returns:
            self: For method chaining
        """
        # Validate inputs (y is optional for unsupervised)
        validate_fit_input(X, y, self.task)
        
        # Create and train model (y is ignored)
        self.model = KMeans(**self.hyperparameters)
        self.model.fit(X)
        
        # Update metadata (y is None for unsupervised)
        self._update_metadata(X, None)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster IDs for samples.
        
        Args:
            X: Features to predict on (n_samples, n_features)
            
        Returns:
            Cluster IDs (n_samples,) - integers from 0 to n_clusters-1
        """
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        return self.model.predict(X)
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - sklearn handles specific value validation.
        """
        # Validate n_clusters
        if "n_clusters" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["n_clusters"], "n_clusters")
        
        # Validate max_iter
        if "max_iter" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["max_iter"], "max_iter")
        
        # Validate n_init
        if "n_init" in self.hyperparameters:
            n_init = self.hyperparameters["n_init"]
            if n_init != "auto":  # sklearn allows "auto" as well
                validate_positive_integer(n_init, "n_init")
        
        # Note: We don't validate algorithm, init method, etc. - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "clustering" - K-Means is a clustering algorithm
        """
        return MODEL_TYPE_CLUSTERING