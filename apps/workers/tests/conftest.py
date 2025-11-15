"""
Shared pytest fixtures for ML trainer tests.
Provides datasets and common test utilities.
"""

import pytest
import numpy as np
from sklearn.datasets import load_iris, load_diabetes
from sklearn.model_selection import train_test_split


@pytest.fixture
def iris_data():
    """
    Classification dataset fixture.
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
        - 150 samples, 4 features, 3 classes
        - 80/20 train/test split
    """
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


@pytest.fixture
def diabetes_data():
    """
    Regression dataset fixture.
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
        - 442 samples, 10 features
        - 80/20 train/test split
    """
    X, y = load_diabetes(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


@pytest.fixture
def iris_unsupervised():
    """
    Unsupervised learning dataset fixture (clustering, dimensionality reduction).
    
    Returns:
        tuple: (X_train, X_test)
        - 150 samples, 4 features
        - No labels provided
        - 80/20 train/test split
    """
    X, _ = load_iris(return_X_y=True)
    X_train, X_test = train_test_split(
        X, test_size=0.2, random_state=42
    )
    return X_train, X_test


@pytest.fixture
def temp_model_dir(tmp_path):
    """
    Temporary directory fixture for model save/load tests.
    
    Args:
        tmp_path: Pytest's built-in temporary directory fixture
        
    Returns:
        Path: Temporary directory path
    """
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return model_dir