#apps/workers/worker/ml/trainers/decision_tree.py
"""
Decision Tree trainer for classification and regression.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from .base import BaseTrainer
from apps.workers.worker.constants import MODEL_TYPE_TREE, TASK_CLASSIFICATION, TASK_REGRESSION
from apps.workers.worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from apps.workers.worker.ml.utils.validation import validate_positive_integer


class DecisionTreeTrainer(BaseTrainer):
    """
    Decision Tree trainer (dual-task).
    
    Supports:
    - Classification (with predict_proba)
    - Regression
    - Feature importance extraction
    
    Task-aware: Instantiates DecisionTreeClassifier or DecisionTreeRegressor based on task.
    
    Default hyperparameters:
    - max_depth: None (unlimited depth)
    - min_samples_split: 2 (minimum samples to split)
    - min_samples_leaf: 1 (minimum samples in leaf)
    - criterion: "gini" for classification, "squared_error" for regression
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize Decision Tree trainer.
        
        Args:
            name: Model name
            task: "classification" or "regression"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set defaults based on task
        if task == TASK_CLASSIFICATION:
            defaults = {
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "criterion": "gini",
            }
        elif task == TASK_REGRESSION:
            defaults = {
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "criterion": "squared_error",
            }
        else:
            # Default for unknown task (will fail during fit)
            defaults = {
                "max_depth": None,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
            }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'DecisionTreeTrainer':
        """
        Train Decision Tree model.
        
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
            self.model = DecisionTreeClassifier(**self.hyperparameters)
        elif self.task == TASK_REGRESSION:
            self.model = DecisionTreeRegressor(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported task for DecisionTree: {self.task}")
        
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
        Get feature importances from the trained tree.
        
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
        Only checks obvious errors - sklearn handles specific value validation.
        """
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
        
        # Note: We don't validate criterion - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "tree" - Decision Tree is a tree-based model
        """
        return MODEL_TYPE_TREE