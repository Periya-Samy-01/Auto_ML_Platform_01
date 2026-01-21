# cli/utils/trainer_factory.py
"""
Factory for instantiating trainers by algorithm name.
Maps algorithm names to trainer classes.
Supports supervised and unsupervised trainers.
"""

from typing import Dict, Type
from apps.api.app.ml.trainers.base import BaseTrainer
from apps.api.app.ml.trainers.decision_tree import DecisionTreeTrainer
from apps.api.app.ml.trainers.logistic_regression import LogisticRegressionTrainer
from apps.api.app.ml.trainers.random_forest import RandomForestTrainer
from apps.api.app.ml.trainers.xgboost import XGBoostTrainer
from apps.api.app.ml.trainers.knn import KNNTrainer
from apps.api.app.ml.trainers.naive_bayes import NaiveBayesTrainer
from apps.api.app.ml.trainers.linear_regression import LinearRegressionTrainer
from apps.api.app.ml.trainers.neural_network import NeuralNetworkTrainer
from apps.api.app.ml.trainers.pca import PCATrainer
from apps.api.app.ml.trainers.kmeans import KMeansTrainer


# Supervised trainers (classification & regression)
SUPERVISED_TRAINERS: Dict[str, Type[BaseTrainer]] = {
    "decision_tree": DecisionTreeTrainer,
    "logistic_regression": LogisticRegressionTrainer,
    "random_forest": RandomForestTrainer,
    "xgboost": XGBoostTrainer,
    "knn": KNNTrainer,
    "naive_bayes": NaiveBayesTrainer,
    "linear_regression": LinearRegressionTrainer,
    "neural_network": NeuralNetworkTrainer,
}

# Unsupervised trainers (clustering & dimensionality reduction)
UNSUPERVISED_TRAINERS: Dict[str, Type[BaseTrainer]] = {
    "kmeans": KMeansTrainer,
    "pca": PCATrainer,
}

# Combined mapping for convenience
TRAINERS_MAP: Dict[str, Type[BaseTrainer]] = {
    **SUPERVISED_TRAINERS,
    **UNSUPERVISED_TRAINERS,
}


def get_trainer(algorithm: str, task: str, hyperparameters: Dict = None) -> BaseTrainer:
    """
    Get a trainer instance by algorithm name and task.
    
    Args:
        algorithm: Algorithm name (e.g., "decision_tree", "kmeans")
        task: Task type (e.g., "classification", "regression", "clustering", "dimensionality_reduction")
        hyperparameters: Optional hyperparameters to override defaults
        
    Returns:
        Instantiated trainer ready for fit()
        
    Raises:
        ValueError: If algorithm not found or task is invalid
    """
    algorithm = algorithm.lower().strip()
    
    if algorithm not in TRAINERS_MAP:
        available = ", ".join(sorted(TRAINERS_MAP.keys()))
        raise ValueError(
            f"Algorithm '{algorithm}' not found.\n"
            f"Available algorithms: {available}"
        )
    
    trainer_class = TRAINERS_MAP[algorithm]
    
    # Instantiate with algorithm name, task, and optional hyperparameters
    if hyperparameters:
        trainer = trainer_class(
            name=algorithm,
            task=task,
            hyperparameters=hyperparameters
        )
    else:
        trainer = trainer_class(
            name=algorithm,
            task=task
        )
    
    return trainer


def is_supervised_trainer(algorithm: str) -> bool:
    """
    Check if algorithm is supervised or unsupervised.
    
    Args:
        algorithm: Algorithm name
        
    Returns:
        True if supervised (classification/regression), False if unsupervised
    """
    algorithm = algorithm.lower().strip()
    return algorithm in SUPERVISED_TRAINERS


def list_available_algorithms(task_type: str = None) -> list:
    """
    Get list of available algorithms, optionally filtered by task type.
    
    Args:
        task_type: Filter by task type ('supervised', 'unsupervised', or None for all)
        
    Returns:
        List of algorithm names
    """
    if task_type == "supervised":
        return sorted(SUPERVISED_TRAINERS.keys())
    elif task_type == "unsupervised":
        return sorted(UNSUPERVISED_TRAINERS.keys())
    else:
        return sorted(TRAINERS_MAP.keys())
