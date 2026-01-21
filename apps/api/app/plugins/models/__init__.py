"""
Model plugins for the AutoML Playground.

Each plugin wraps an existing trainer and provides:
- Metadata (name, description, icon, category)
- Hyperparameter schema for UI rendering
- Supported metrics and plots
- Training logic
"""

from app.plugins.models.random_forest import RandomForestPlugin
from app.plugins.models.decision_tree import DecisionTreePlugin
from app.plugins.models.logistic_regression import LogisticRegressionPlugin
from app.plugins.models.linear_regression import LinearRegressionPlugin
from app.plugins.models.xgboost import XGBoostPlugin
from app.plugins.models.knn import KNNPlugin
from app.plugins.models.naive_bayes import NaiveBayesPlugin
from app.plugins.models.neural_network import NeuralNetworkPlugin
from app.plugins.models.svm import SVMPlugin
from app.plugins.models.kmeans import KMeansPlugin

__all__ = [
    "RandomForestPlugin",
    "DecisionTreePlugin",
    "LogisticRegressionPlugin",
    "LinearRegressionPlugin",
    "XGBoostPlugin",
    "KNNPlugin",
    "NaiveBayesPlugin",
    "NeuralNetworkPlugin",
    "SVMPlugin",
    "KMeansPlugin",
]
