#apps/workers/worker/ml/utils/trainer_utils.py
"""
Utility functions for ML trainers.
Common helper functions used across multiple trainers.
"""

from typing import Dict, Any, Optional
import numpy as np
from apps.workers.worker.constants import (
    SUPERVISED_TASKS,
    UNSUPERVISED_TASKS,
    TASK_CLASSIFICATION,
    TASK_REGRESSION,
)


def is_supervised_task(task: str) -> bool:
    """
    Check if task is supervised (classification or regression).
    
    Args:
        task: Task type string
        
    Returns:
        True if supervised, False otherwise
    """
    return task in SUPERVISED_TASKS


def is_unsupervised_task(task: str) -> bool:
    """
    Check if task is unsupervised (clustering or dimensionality reduction).
    
    Args:
        task: Task type string
        
    Returns:
        True if unsupervised, False otherwise
    """
    return task in UNSUPERVISED_TASKS


def is_classification_task(task: str) -> bool:
    """
    Check if task is classification.
    
    Args:
        task: Task type string
        
    Returns:
        True if classification, False otherwise
    """
    return task == TASK_CLASSIFICATION


def is_regression_task(task: str) -> bool:
    """
    Check if task is regression.
    
    Args:
        task: Task type string
        
    Returns:
        True if regression, False otherwise
    """
    return task == TASK_REGRESSION


def merge_hyperparameters(defaults: Dict[str, Any], user_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge user hyperparameters with defaults.
    
    Args:
        defaults: Default hyperparameter values
        user_params: User-provided hyperparameters (can be None)
        
    Returns:
        Merged hyperparameters (user values override defaults)
    """
    if user_params is None:
        return defaults.copy()
    
    merged = defaults.copy()
    merged.update(user_params)
    return merged


def validate_fit_input(X: np.ndarray, y: Optional[np.ndarray], task: str) -> None:
    """
    Validate input data for fit() method.
    
    Args:
        X: Training features
        y: Training targets (can be None for unsupervised)
        task: Task type
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Check X is 2D
    if X.ndim != 2:
        raise ValueError(f"X must be 2D array, got shape {X.shape}")
    
    # Check y requirements for supervised tasks
    if is_supervised_task(task):
        if y is None:
            raise ValueError(f"Supervised task '{task}' requires target values (y cannot be None)")
        
        if len(y) != len(X):
            raise ValueError(f"X and y must have same number of samples. Got X: {len(X)}, y: {len(y)}")
    
    # Check for empty data
    if len(X) == 0:
        raise ValueError("X cannot be empty")


def validate_predict_input(X: np.ndarray, expected_features: int) -> None:
    """
    Validate input data for predict() method.
    
    Args:
        X: Features to predict on
        expected_features: Expected number of features from training
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Check X is 2D
    if X.ndim != 2:
        raise ValueError(f"X must be 2D array, got shape {X.shape}")
    
    # Check feature count matches training
    if X.shape[1] != expected_features:
        raise ValueError(
            f"X has {X.shape[1]} features, but model was trained with {expected_features} features"
        )
    
    # Check for empty data
    if len(X) == 0:
        raise ValueError("X cannot be empty")


def check_model_fitted(model: Any) -> None:
    """
    Check if model has been fitted.
    
    Args:
        model: Trainer's model attribute
        
    Raises:
        ValueError: If model is None (not fitted)
    """
    if model is None:
        raise ValueError("Model has not been fitted yet. Call fit() before predict().")