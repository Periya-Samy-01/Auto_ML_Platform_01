#apps/workers/worker/ml/__init__.py
"""
ML module public API.
Exports all trainers, evaluators, and utility functions.
"""

# Trainers (will be implemented in phases 2-4)
from .trainers.logistic_regression import LogisticRegressionTrainer
from .trainers.naive_bayes import NaiveBayesTrainer
from .trainers.knn import KNNTrainer
from .trainers.decision_tree import DecisionTreeTrainer
from .trainers.random_forest import RandomForestTrainer
from .trainers.xgboost import XGBoostTrainer
from .trainers.linear_regression import LinearRegressionTrainer
from .trainers.kmeans import KMeansTrainer
from .trainers.pca import PCATrainer
from .trainers.neural_network import NeuralNetworkTrainer

# Evaluators
from .evaluators.classification_evaluator import ClassificationEvaluator
from .evaluators.regression_evaluator import RegressionEvaluator


# Trainer registry mapping
_TRAINER_REGISTRY = {
    "logistic_regression": LogisticRegressionTrainer,
    "naive_bayes": NaiveBayesTrainer,
    "knn": KNNTrainer,
    "decision_tree": DecisionTreeTrainer,
    "random_forest": RandomForestTrainer,
    "xgboost": XGBoostTrainer,
    "linear_regression": LinearRegressionTrainer,
    "kmeans": KMeansTrainer,
    "pca": PCATrainer,
    "neural_network": NeuralNetworkTrainer,
}


def get_trainer_class(trainer_type: str) -> type:
    """
    Get trainer class by string name.
    
    Args:
        trainer_type: String name of trainer (e.g., "logistic_regression", "random_forest")
        
    Returns:
        Trainer class
        
    Raises:
        ValueError: If trainer_type is not recognized
        
    Example:
        >>> TrainerClass = get_trainer_class("random_forest")
        >>> trainer = TrainerClass(name="rf_model", task="classification")
    """
    if trainer_type not in _TRAINER_REGISTRY:
        valid_types = ", ".join(_TRAINER_REGISTRY.keys())
        raise ValueError(f"Unknown trainer type: '{trainer_type}'. Valid types: {valid_types}")
    
    return _TRAINER_REGISTRY[trainer_type]


__all__ = [
    # Trainers
    "LogisticRegressionTrainer",
    "NaiveBayesTrainer",
    "KNNTrainer",
    "DecisionTreeTrainer",
    "RandomForestTrainer",
    "XGBoostTrainer",
    "LinearRegressionTrainer",
    "KMeansTrainer",
    "PCATrainer",
    "NeuralNetworkTrainer",
    # Evaluators
    "ClassificationEvaluator",
    "RegressionEvaluator",
    # Utilities
    "get_trainer_class",
]