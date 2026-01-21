#apps/workers/worker/ml/trainers/linear_regression.py
"""
Linear Regression trainer for regression tasks.
Simple linear model - fastest trainer.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.linear_model import LinearRegression

from .base import BaseTrainer
from ..constants import MODEL_TYPE_LINEAR, TASK_REGRESSION
from ..utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from ..utils.validation import validate_boolean


class LinearRegressionTrainer(BaseTrainer):
    """
    Linear Regression trainer for regression tasks.
    
    Supports:
    - Simple linear regression
    - Feature importance via coefficient weights
    - Fastest training algorithm
    
    Default hyperparameters:
    - fit_intercept: True (include intercept term)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize Linear Regression trainer.
        
        Args:
            name: Model name
            task: Must be "regression"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set minimal defaults
        defaults = {
            "fit_intercept": True,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'LinearRegressionTrainer':
        """
        Train linear regression model.
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            
        Returns:
            self: For method chaining
        """
        # Validate inputs
        validate_fit_input(X, y, self.task)
        
        # Create and train model
        self.model = LinearRegression(**self.hyperparameters)
        self.model.fit(X, y)
        
        # Update metadata
        self._update_metadata(X, y)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict regression values.
        
        Args:
            X: Features to predict on (n_samples, n_features)
            
        Returns:
            Predicted values (n_samples,)
        """
        check_model_fitted(self.model)
        validate_predict_input(X, self._metadata["feature_count"])
        
        return self.model.predict(X)
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """
        Get feature importances from linear regression coefficients.
        
        Returns:
            Absolute values of coefficients as feature importance (n_features,)
            
        Raises:
            ValueError: If model hasn't been fitted yet
        """
        check_model_fitted(self.model)
        
        # Use absolute values of coefficients as importance
        return np.abs(self.model.coef_)
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - sklearn handles specific value validation.
        """
        # Validate fit_intercept (must be boolean)
        if "fit_intercept" in self.hyperparameters:
            validate_boolean(self.hyperparameters["fit_intercept"], "fit_intercept")
        
        # Note: We don't validate normalize, copy_X, etc. - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "linear" - Linear regression is a linear model
        """
        return MODEL_TYPE_LINEAR