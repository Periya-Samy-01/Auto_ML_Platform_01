#apps/workers/worker/ml/trainers/__init__.py
"""
ML trainer implementations.
"""

# Base trainer is always available
from .base import BaseTrainer

# Concrete trainers (will be implemented in Phases 2-4)
from .logistic_regression import LogisticRegressionTrainer
from .naive_bayes import NaiveBayesTrainer
from .knn import KNNTrainer
from .decision_tree import DecisionTreeTrainer
from .random_forest import RandomForestTrainer
from .xgboost import XGBoostTrainer
from .linear_regression import LinearRegressionTrainer
from .kmeans import KMeansTrainer
from .pca import PCATrainer
from .neural_network import NeuralNetworkTrainer

__all__ = [
    "BaseTrainer",
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
]