#apps/workers/worker/ml/trainers/neural_network.py
"""
Neural Network (Multi-Layer Perceptron) trainer for classification and regression.
Deep learning with backpropagation.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.neural_network import MLPClassifier, MLPRegressor

from .base import BaseTrainer
from worker.constants import MODEL_TYPE_NEURAL, TASK_CLASSIFICATION, TASK_REGRESSION
from worker.ml.utils.trainer_utils import (
    validate_fit_input,
    validate_predict_input,
    check_model_fitted,
)
from worker.ml.utils.validation import (
    validate_positive_integer,
    validate_positive_number,
    validate_type,
)


class NeuralNetworkTrainer(BaseTrainer):
    """
    Neural Network (MLP) trainer (dual-task).
    
    Supports:
    - Classification (with predict_proba)
    - Regression
    - Multi-layer perceptron with backpropagation
    - Early stopping to save compute
    
    Task-aware: Instantiates MLPClassifier or MLPRegressor based on task.
    
    Default hyperparameters:
    - hidden_layer_sizes: (50,) (single layer, 50 neurons, minimal)
    - activation: "relu" (ReLU activation)
    - solver: "adam" (Adam optimizer)
    - learning_rate_init: 0.001 (initial learning rate)
    - max_iter: 100 (maximum iterations, minimal)
    - early_stopping: True (stop early to save compute, user can disable)
    - random_state: 42 (for reproducibility)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize Neural Network trainer.
        
        Args:
            name: Model name
            task: "classification" or "regression"
            hyperparameters: Optional hyperparameters (uses defaults if not provided)
        """
        # Set minimal defaults (for compute cost)
        defaults = {
            "hidden_layer_sizes": (50,),
            "activation": "relu",
            "solver": "adam",
            "learning_rate_init": 0.001,
            "max_iter": 100,
            "early_stopping": True,  # Save compute by stopping early
            "random_state": 42,
        }
        
        # Merge with user params
        if hyperparameters is None:
            hyperparameters = {}
        merged_params = {**defaults, **hyperparameters}
        
        super().__init__(name=name, task=task, hyperparameters=merged_params)
    
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'NeuralNetworkTrainer':
        """
        Train neural network model.
        
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
            self.model = MLPClassifier(**self.hyperparameters)
        elif self.task == TASK_REGRESSION:
            self.model = MLPRegressor(**self.hyperparameters)
        else:
            raise ValueError(f"Unsupported task for NeuralNetwork: {self.task}")
        
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
        # Validate hidden_layer_sizes (must be tuple)
        if "hidden_layer_sizes" in self.hyperparameters:
            validate_type(
                self.hyperparameters["hidden_layer_sizes"],
                "hidden_layer_sizes",
                tuple
            )
        
        # Validate max_iter
        if "max_iter" in self.hyperparameters:
            validate_positive_integer(self.hyperparameters["max_iter"], "max_iter")
        
        # Validate learning_rate_init
        if "learning_rate_init" in self.hyperparameters:
            validate_positive_number(self.hyperparameters["learning_rate_init"], "learning_rate_init")
        
        # Note: We don't validate activation, solver, etc. - sklearn will handle those
    
    def get_model_type(self) -> str:
        """
        Return model family type.
        
        Returns:
            "neural" - Neural network (MLP) is a neural model
        """
        return MODEL_TYPE_NEURAL