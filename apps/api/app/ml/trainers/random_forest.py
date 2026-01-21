#apps/workers/worker/ml/trainers/random_forest.py
"""
Random Forest trainer for classification and regression.
Ensemble of decision trees with bootstrap aggregating.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from .base import BaseTrainer
from ..constants import MODEL_TYPE_TREE, TASK_CLASSIFICATION, TASK_REGRESSION
from ..utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from ..utils.validation import (
    validate_positive_integer,
    validate_probability,
)


class RandomForestTrainer(BaseTrainer):
    """
    Random Forest trainer (dual-task ensemble).
    
    Supports:
    - Classification (with predict_proba)
    - Regression
    - Feature importance extraction
    - Bootstrap aggregating with multiple decision trees
    
    Task-aware: Instantiates RandomForestClassifier or RandomForestRegressor based on task.
    
    Default hyperparameters:
    - n_estimators: 100 (number of trees)
    - max_depth: 10 (maximum tree depth, limited to control compute)
    - min_samples_split: 2 (minimum samples to split)
    - min_samples_leaf: 1 (minimum samples in leaf)
    - random_state: 42 (for reproducibility)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize Random Forest trainer.
        
        Args:
            name: Model name
            task: "classification" or "regression"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set minimal defaults (avoid unlimited depth to control compute cost)
        defaults = {
            "n_estimators": 10,       # ✅ Much faster (10 trees instead of 100)
            "max_depth": 5,           # ✅ Shallower trees = faster
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'RandomForestTrainer':
        """
        Train Random Forest model.
        
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
            self.model = RandomForestClassifier(**self.hyperparameters)
        elif self.task == TASK_REGRESSION:
            self.model = RandomForestRegressor(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported task for RandomForest: {self.task}")
        
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
        Get feature importances from the trained random forest.
        
        Returns:
            Feature importance array (n_features,) - averaged across all trees
            
        Raises:
            ValueError: If model hasn't been fitted yet
        """
        check_model_fitted(self.model)
        
        return self.model.feature_importances_
    
    def _validate_hyperparameters(self) -> None:
        """
        Validate hyperparameters (loose validation).
        Only checks obvious errors - sklearn handles specific value validation.
        """
        # Validate n_estimators
        if "n_estimators" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["n_estimators"], "n_estimators")
        
        # Validate max_depth (must be positive integer or None)
        if "max_depth" in self.hyperparameters:
            max_depth = self.hyperparameters["max_depth"]
            if max_depth is not None:
                validate_positive_integer(max_depth, "max_depth")
        
        # Validate min_samples_split
        if "min_samples_split" in self.hyperparameters:
            min_samples_split = self.hyperparameters["min_samples_split"]
            if isinstance(min_samples_split, int):
                validate_positive_integer(min_samples_split, "min_samples_split")
            # If float (fraction), sklearn will validate
        
        # Validate min_samples_leaf
        if "min_samples_leaf" in self.hyperparameters:
            min_samples_leaf = self.hyperparameters["min_samples_leaf"]
            if isinstance(min_samples_leaf, int):
                validate_positive_integer(min_samples_leaf, "min_samples_leaf")
            # If float (fraction), sklearn will validate
        
        # Note: We don't validate max_features, criterion, etc. - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "tree" - Random Forest is an ensemble of decision trees
        """
        return MODEL_TYPE_TREE