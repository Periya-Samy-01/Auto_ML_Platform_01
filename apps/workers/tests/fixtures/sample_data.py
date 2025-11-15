"""
Dataset loading utilities for tests.
Helper functions to load and prepare test datasets.
"""

import numpy as np
from sklearn.datasets import load_iris, load_diabetes, make_classification, make_regression
from sklearn.model_selection import train_test_split
from typing import Tuple


def load_iris_data(test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load iris dataset for classification tasks.
    
    Args:
        test_size: Fraction of data for test set
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def load_diabetes_data(test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load diabetes dataset for regression tasks.
    
    Args:
        test_size: Fraction of data for test set
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    X, y = load_diabetes(return_X_y=True)
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def load_iris_unsupervised(test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load iris dataset for unsupervised tasks (clustering, dimensionality reduction).
    
    Args:
        test_size: Fraction of data for test set
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test) - no labels
    """
    X, _ = load_iris(return_X_y=True)
    return train_test_split(X, test_size=test_size, random_state=random_state)


def create_binary_classification_data(n_samples: int = 100, n_features: int = 4, 
                                       test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Create synthetic binary classification dataset.
    
    Args:
        n_samples: Number of samples
        n_features: Number of features
        test_size: Fraction of data for test set
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_features - 1,
        n_redundant=0,
        n_classes=2,
        random_state=random_state
    )
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def create_regression_data(n_samples: int = 100, n_features: int = 4,
                           test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Create synthetic regression dataset.
    
    Args:
        n_samples: Number of samples
        n_features: Number of features
        test_size: Fraction of data for test set
        random_state: Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_features - 1,
        noise=10.0,
        random_state=random_state
    )
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def get_dataset_info(X: np.ndarray, y: np.ndarray = None) -> dict:
    """
    Get information about a dataset.
    
    Args:
        X: Feature matrix
        y: Target vector (optional)
        
    Returns:
        dict: Dataset information (n_samples, n_features, n_classes)
    """
    info = {
        "n_samples": X.shape[0],
        "n_features": X.shape[1],
    }
    
    if y is not None:
        unique_classes = np.unique(y)
        info["n_classes"] = len(unique_classes)
        info["class_distribution"] = {
            int(cls): int(np.sum(y == cls)) for cls in unique_classes
        }
    
    return info