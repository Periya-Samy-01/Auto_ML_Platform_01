"""
Neural Network model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.neural_network import MLPClassifier, MLPRegressor

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class NeuralNetworkPlugin(BaseModelPlugin):
    """
    Neural Network plugin - Multi-layer Perceptron.

    Flexible model capable of learning complex non-linear patterns.
    """

    slug = "neural_network"
    name = "Neural Network"
    description = "Multi-layer perceptron for complex pattern recognition"
    icon = "🧠"
    problem_types = [ProblemType.CLASSIFICATION, ProblemType.REGRESSION]
    category = ModelCategory.NEURAL
    best_for = "Complex non-linear patterns and large datasets"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="hidden_layer_sizes",
                    name="Hidden Layer Sizes",
                    type=FieldType.SELECT,
                    default="(100,)",
                    options=[
                        {"value": "(50,)", "label": "Small (50)"},
                        {"value": "(100,)", "label": "Medium (100)"},
                        {"value": "(100, 50)", "label": "Two Layers (100, 50)"},
                        {"value": "(100, 100)", "label": "Two Layers (100, 100)"},
                        {"value": "(128, 64, 32)", "label": "Three Layers (128, 64, 32)"},
                    ],
                    description="Number and size of hidden layers",
                ),
                HyperparameterField(
                    key="activation",
                    name="Activation Function",
                    type=FieldType.SELECT,
                    default="relu",
                    options=[
                        {"value": "relu", "label": "ReLU"},
                        {"value": "tanh", "label": "Tanh"},
                        {"value": "logistic", "label": "Sigmoid"},
                    ],
                    description="Activation function for hidden layers",
                ),
                HyperparameterField(
                    key="learning_rate_init",
                    name="Initial Learning Rate",
                    type=FieldType.FLOAT,
                    default=0.001,
                    min=0.0001,
                    max=0.1,
                    step=0.0001,
                    description="Initial learning rate for weight updates",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="solver",
                    name="Optimizer",
                    type=FieldType.SELECT,
                    default="adam",
                    options=[
                        {"value": "adam", "label": "Adam"},
                        {"value": "sgd", "label": "SGD"},
                        {"value": "lbfgs", "label": "L-BFGS"},
                    ],
                    description="Weight optimization algorithm",
                ),
                HyperparameterField(
                    key="alpha",
                    name="L2 Regularization",
                    type=FieldType.FLOAT,
                    default=0.0001,
                    min=0.0,
                    max=1.0,
                    step=0.0001,
                    description="L2 penalty (regularization) parameter",
                ),
                HyperparameterField(
                    key="batch_size",
                    name="Batch Size",
                    type=FieldType.SELECT,
                    default="auto",
                    options=[
                        {"value": "auto", "label": "Auto"},
                        {"value": "32", "label": "32"},
                        {"value": "64", "label": "64"},
                        {"value": "128", "label": "128"},
                        {"value": "256", "label": "256"},
                    ],
                    description="Size of minibatches for SGD/Adam",
                ),
                HyperparameterField(
                    key="max_iter",
                    name="Max Iterations",
                    type=FieldType.INT,
                    default=200,
                    min=50,
                    max=2000,
                    description="Maximum number of iterations",
                ),
                HyperparameterField(
                    key="early_stopping",
                    name="Early Stopping",
                    type=FieldType.BOOL,
                    default=True,
                    description="Stop training when validation score stops improving",
                ),
                HyperparameterField(
                    key="random_state",
                    name="Random Seed",
                    type=FieldType.INT,
                    default=42,
                    min=0,
                    max=9999,
                    description="Random seed for reproducibility",
                ),
            ],
        )

    @classmethod
    def get_supported_metrics(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return [
                "accuracy", "precision", "recall", "f1_score",
                "roc_auc", "log_loss", "confusion_matrix", "classification_report"
            ]
        else:
            return ["mse", "rmse", "mae", "r2_score", "mape"]

    @classmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["accuracy", "f1_score", "roc_auc", "confusion_matrix"]
        else:
            return ["rmse", "r2_score"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return [
                "confusion_matrix", "roc_curve", "precision_recall_curve",
                "learning_curve", "class_distribution"
            ]
        else:
            return [
                "prediction_vs_actual", "residual_plot", "residual_distribution",
                "learning_curve"
            ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["confusion_matrix", "roc_curve"]
        else:
            return ["prediction_vs_actual", "residual_plot"]

    @classmethod
    def train(
        cls,
        X_train: np.ndarray,
        y_train: np.ndarray,
        hyperparameters: Dict[str, Any],
        problem_type: ProblemType,
    ) -> Any:
        params = cls.get_default_hyperparameters()
        params.update(hyperparameters)

        # Convert hidden_layer_sizes from string to tuple
        hidden_layers = params.get("hidden_layer_sizes", "(100,)")
        if isinstance(hidden_layers, str):
            params["hidden_layer_sizes"] = eval(hidden_layers)

        # Convert batch_size from string to int or 'auto'
        batch_size = params.get("batch_size", "auto")
        if batch_size != "auto":
            try:
                params["batch_size"] = int(batch_size)
            except (ValueError, TypeError):
                params["batch_size"] = "auto"

        if problem_type == ProblemType.CLASSIFICATION:
            model = MLPClassifier(**params)
        else:
            model = MLPRegressor(**params)

        model.fit(X_train, y_train)
        return model
