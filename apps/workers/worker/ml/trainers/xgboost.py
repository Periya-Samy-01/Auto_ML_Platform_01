#apps/workers/worker/ml/trainers/xgboost.py
"""
XGBoost trainer for classification and regression.
Gradient boosting ensemble with advanced regularization.
"""

from typing import Dict, Any, Optional
import numpy as np
from xgboost import XGBClassifier, XGBRegressor

from .base import BaseTrainer
from apps.workers.worker.constants import MODEL_TYPE_TREE, TASK_CLASSIFICATION, TASK_REGRESSION
from apps.workers.worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from apps.workers.worker.ml.utils.validation import (
    validate_positive_integer,
    validate_positive_number,
    validate_probability,
)


class XGBoostTrainer(BaseTrainer):
    """
    XGBoost trainer (dual-task ensemble).
    
    Supports:
    - Classification (with predict_proba)
    - Regression
    - Feature importance extraction
    - Gradient boosting with advanced regularization
    - GPU acceleration (pro users only, platform-controlled)
    
    Task-aware: Instantiates XGBClassifier or XGBRegressor based on task.
    
    Default hyperparameters:
    - n_estimators: 50 (number of boosting rounds)
    - max_depth: 3 (maximum tree depth)
    - learning_rate: 0.3 (step size shrinkage)
    - subsample: 0.8 (fraction of samples per tree)
    - colsample_bytree: 0.8 (fraction of features per tree)
    - random_state: 42 (for reproducibility)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None, 
                 use_gpu: bool = False):
        """
        Initialize XGBoost trainer.
        
        Args:
            name: Model name
            task: "classification" or "regression"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
            use_gpu: Enable GPU acceleration (pro users only, controlled by backend)
        """
        # Set minimal defaults
        defaults = {
            "n_estimators": 50,
            "max_depth": 3,
            "learning_rate": 0.3,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        # GPU support (platform-controlled)
        # Pro users: Backend passes use_gpu=True
        # Free users: Backend passes use_gpu=False (default)
        if use_gpu:
            # Enable GPU for pro users (XGBoost 2.0+ API)
            merged_params.setdefault("device", "cuda")
            merged_params.setdefault("tree_method", "hist")
        else:
            # Force CPU for free users - block any GPU attempts
            merged_params.setdefault("device", "cpu")
            # Override if user tried to enable GPU
            if "device" in merged_params and "cuda" in str(merged_params["device"]).lower():
                merged_params["device"] = "cpu"
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'XGBoostTrainer':
        """
        Train XGBoost model.
        
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
            self.model = XGBClassifier(**self.hyperparameters)
        elif self.task == TASK_REGRESSION:
            self.model = XGBRegressor(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported task for XGBoost: {self.task}")
        
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
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """
        Get feature importances from the trained XGBoost model.
        
        Returns:
            Feature importance array (n_features,)
            
        Raises:
            ValueError: If model hasn't been fitted yet
        """
        check_model_fitted(self.model)
        
        return self.model.feature_importances_
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - XGBoost handles specific value validation.
        """
        # Validate n_estimators
        if "n_estimators" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["n_estimators"], "n_estimators")
        
        # Validate max_depth
        if "max_depth" in self.hyperparameters:
            max_depth = self.hyperparameters["max_depth"]
            if max_depth is not None:
                validate_positive_integer(max_depth, "max_depth")
        
        # Validate learning_rate
        if "learning_rate" in self.hyperparameters:
            validate_positive_number(self.hyperparameters["learning_rate"], "learning_rate")
        
        # Validate subsample (must be between 0 and 1)
        if "subsample" in self.hyperparameters:
            validate_probability(self.hyperparameters["subsample"], "subsample")
        
        # Validate colsample_bytree (must be between 0 and 1)
        if "colsample_bytree" in self.hyperparameters:
            validate_probability(self.hyperparameters["colsample_bytree"], "colsample_bytree")
        
        # Note: We don't validate objective, booster, etc. - XGBoost will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "tree" - XGBoost is an ensemble of gradient boosted decision trees
        """
        return MODEL_TYPE_TREE