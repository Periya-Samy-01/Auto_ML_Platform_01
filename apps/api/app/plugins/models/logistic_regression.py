"""
Logistic Regression model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.linear_model import LogisticRegression

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class LogisticRegressionPlugin(BaseModelPlugin):
    """
    Logistic Regression plugin - linear classification model.

    Fast, interpretable baseline for classification tasks.
    """

    slug = "logistic_regression"
    name = "Logistic Regression"
    description = "Linear model for classification with probability estimates"
    icon = "📈"
    problem_types = [ProblemType.CLASSIFICATION]
    category = ModelCategory.LINEAR
    best_for = "Binary classification and linear decision boundaries"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="C",
                    name="Regularization Strength",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.001,
                    max=100.0,
                    step=0.1,
                    description="Inverse of regularization strength (smaller = stronger)",
                ),
                HyperparameterField(
                    key="penalty",
                    name="Penalty",
                    type=FieldType.SELECT,
                    default="l2",
                    options=[
                        {"value": "l2", "label": "L2 (Ridge)"},
                        {"value": "l1", "label": "L1 (Lasso)"},
                        {"value": "elasticnet", "label": "Elastic Net"},
                        {"value": None, "label": "None"},
                    ],
                    description="Type of regularization penalty",
                ),
                HyperparameterField(
                    key="solver",
                    name="Solver",
                    type=FieldType.SELECT,
                    default="lbfgs",
                    options=[
                        {"value": "lbfgs", "label": "LBFGS"},
                        {"value": "liblinear", "label": "Liblinear"},
                        {"value": "saga", "label": "SAGA"},
                    ],
                    description="Algorithm for optimization",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="max_iter",
                    name="Max Iterations",
                    type=FieldType.INT,
                    default=100,
                    min=50,
                    max=1000,
                    step=50,
                    description="Maximum iterations for solver convergence",
                ),
                HyperparameterField(
                    key="class_weight",
                    name="Class Weight",
                    type=FieldType.SELECT,
                    default=None,
                    options=[
                        {"value": None, "label": "None"},
                        {"value": "balanced", "label": "Balanced"},
                    ],
                    description="Weight adjustment for imbalanced classes",
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
        return [
            "accuracy", "precision", "recall", "f1_score",
            "roc_auc", "log_loss", "confusion_matrix", "classification_report"
        ]

    @classmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        return ["accuracy", "f1_score", "roc_auc", "confusion_matrix"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        return [
            "confusion_matrix", "roc_curve", "precision_recall_curve",
            "coefficient_plot", "learning_curve", "class_distribution"
        ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        return ["confusion_matrix", "roc_curve", "coefficient_plot"]

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

        # Convert string "none" to Python None for parameters that accept None
        # This handles JSON serialization where null becomes "none" string
        if params.get("class_weight") in ("none", "None", "null"):
            params["class_weight"] = None
        if params.get("penalty") in ("none", "None", "null"):
            params["penalty"] = None

        # Handle solver/penalty compatibility
        penalty = params.get("penalty")
        solver = params.get("solver", "lbfgs")

        # Adjust solver if needed for certain penalties
        if penalty == "l1" and solver not in ["liblinear", "saga"]:
            params["solver"] = "saga"
        if penalty == "elasticnet":
            params["solver"] = "saga"
            params["l1_ratio"] = 0.5  # Default for elastic net

        model = LogisticRegression(**params)
        model.fit(X_train, y_train)
        return model
