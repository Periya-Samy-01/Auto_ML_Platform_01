#apps/workers/worker/ml/trainers/logistic_regression.py
"""
Logistic Regression trainer for binary and multiclass classification.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.linear_model import LogisticRegression

from .base import BaseTrainer
from apps.workers.worker.constants import MODEL_TYPE_LINEAR, TASK_CLASSIFICATION
from apps.workers.worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from apps.workers.worker.ml.utils.validation import (
    validate_positive_number,
    validate_positive_integer,
)


class LogisticRegressionTrainer(BaseTrainer):
    """
    Logistic Regression trainer for classification tasks.
    
    Supports:
    - Binary and multiclass classification
    - Probability predictions via predict_proba()
    - All sklearn LogisticRegression parameters
    
    Default hyperparameters:
    - C: 1.0 (regularization strength)
    - max_iter: 100 (maximum iterations)
    - solver: "lbfgs" (optimization algorithm)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize Logistic Regression trainer.
        
        Args:
            name: Model name
            task: Must be "classification"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set defaults
        defaults = {
            "C": 1.0,
            "max_iter": 100,
            "solver": "lbfgs",
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'LogisticRegressionTrainer':
        """
        Train logistic regression model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training labels (n_samples,)
            
        Returns:
            self: For method chaining
        """
        # Validate inputs
        validate_fit_input(X, y, self.task)
        
        # Create and train model
        self.model = LogisticRegression(**self.hyperparameters)
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
        # Validate C (regularization strength)
        if "C" in self.hyperparameters:
            validate_positive_number(self.hyperparameters["C"], "C")
        
        # Validate max_iter
        if "max_iter" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["max_iter"], "max_iter")
        
        # Note: We don't validate solver, penalty, etc. - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "linear" - Logistic regression is a linear model
        """
        return MODEL_TYPE_LINEAR