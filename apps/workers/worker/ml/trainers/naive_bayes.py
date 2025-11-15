"""
Naive Bayes trainer for classification.
Uses Gaussian Naive Bayes (assumes features follow normal distribution).
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.naive_bayes import GaussianNB

from .base import BaseTrainer
from worker.constants import MODEL_TYPE_LINEAR, TASK_CLASSIFICATION
from worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from worker.ml.utils.validation import validate_positive_number


class NaiveBayesTrainer(BaseTrainer):
    """
    Gaussian Naive Bayes trainer for classification tasks.
    
    Supports:
    - Binary and multiclass classification
    - Probability predictions via predict_proba()
    - Minimal hyperparameters (simple algorithm)
    
    Default hyperparameters:
    - var_smoothing: 1e-9 (portion of largest variance added to variances for stability)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize Naive Bayes trainer.
        
        Args:
            name: Model name
            task: Must be "classification"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set defaults
        defaults = {
            "var_smoothing": 1e-9,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'NaiveBayesTrainer':
        """
        Train Naive Bayes model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training labels (n_samples,)
            
        Returns:
            self: For method chaining
        """
        # Validate inputs
        validate_fit_input(X, y, self.task)
        
        # Create and train model
        self.model = GaussianNB(**self.hyperparameters)
        self.model.fit(X, y)
        
        # Update metadata
        self._update_metadata(X, y)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels.
        
        Args:
            X: Features to predict on (n_samples, n_features)
            
        Returns:
            Predicted class labels (n_samples,)
        """
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Features to predict on (n_samples, n_features)
            
        Returns:
            Class probabilities (n_samples, n_classes)
        """
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        return self.model.predict_proba(X)
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - sklearn handles specific value validation.
        """
        # Validate var_smoothing (must be positive)
        if "var_smoothing" in self.hyperparameters:
            validate_positive_number(self.hyperparameters["var_smoothing"], "var_smoothing")
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "linear" - Naive Bayes is a probabilistic linear classifier
        """
        return MODEL_TYPE_LINEAR