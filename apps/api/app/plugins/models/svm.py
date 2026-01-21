"""
Support Vector Machine model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.svm import SVC, SVR

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class SVMPlugin(BaseModelPlugin):
    """
    Support Vector Machine plugin.

    Powerful model for both classification and regression using kernel methods.
    """

    slug = "svm"
    name = "Support Vector Machine"
    description = "Kernel-based model for classification and regression"
    icon = "🔷"
    problem_types = [ProblemType.CLASSIFICATION, ProblemType.REGRESSION]
    category = ModelCategory.LINEAR
    best_for = "High-dimensional data and clear margin of separation"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="kernel",
                    name="Kernel",
                    type=FieldType.SELECT,
                    default="rbf",
                    options=[
                        {"value": "rbf", "label": "RBF (Gaussian)"},
                        {"value": "linear", "label": "Linear"},
                        {"value": "poly", "label": "Polynomial"},
                        {"value": "sigmoid", "label": "Sigmoid"},
                    ],
                    description="Kernel type for the algorithm",
                ),
                HyperparameterField(
                    key="C",
                    name="Regularization (C)",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.001,
                    max=100.0,
                    step=0.1,
                    description="Regularization parameter (smaller = more regularization)",
                ),
                HyperparameterField(
                    key="gamma",
                    name="Gamma",
                    type=FieldType.SELECT,
                    default="scale",
                    options=[
                        {"value": "scale", "label": "Scale (1 / (n_features * X.var()))"},
                        {"value": "auto", "label": "Auto (1 / n_features)"},
                    ],
                    description="Kernel coefficient for RBF, poly, and sigmoid",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="degree",
                    name="Polynomial Degree",
                    type=FieldType.INT,
                    default=3,
                    min=1,
                    max=10,
                    description="Degree for polynomial kernel",
                ),
                HyperparameterField(
                    key="probability",
                    name="Probability Estimates",
                    type=FieldType.BOOL,
                    default=True,
                    description="Enable probability estimates (slower)",
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
                    key="max_iter",
                    name="Max Iterations",
                    type=FieldType.INT,
                    default=-1,
                    min=-1,
                    max=10000,
                    description="Hard limit on iterations (-1 = no limit)",
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
                "roc_auc", "confusion_matrix", "classification_report"
            ]
        else:
            return ["mse", "rmse", "mae", "r2_score"]

    @classmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["accuracy", "f1_score", "confusion_matrix"]
        else:
            return ["rmse", "r2_score"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return [
                "confusion_matrix", "roc_curve", "precision_recall_curve",
                "class_distribution", "learning_curve"
            ]
        else:
            return [
                "prediction_vs_actual", "residual_plot", "learning_curve"
            ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["confusion_matrix", "roc_curve"]
        else:
            return ["prediction_vs_actual"]

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

        # Remove classification-only params for regression
        if problem_type == ProblemType.REGRESSION:
            params.pop("probability", None)
            params.pop("class_weight", None)

        if problem_type == ProblemType.CLASSIFICATION:
            model = SVC(**params)
        else:
            # SVR doesn't use probability or class_weight
            svr_params = {k: v for k, v in params.items()
                         if k not in ["probability", "class_weight"]}
            model = SVR(**svr_params)

        model.fit(X_train, y_train)
        return model
