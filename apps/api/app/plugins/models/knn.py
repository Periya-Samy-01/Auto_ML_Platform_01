"""
K-Nearest Neighbors model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class KNNPlugin(BaseModelPlugin):
    """
    K-Nearest Neighbors plugin - instance-based learning.

    Simple, non-parametric model that makes predictions based on
    the k closest training examples.
    """

    slug = "knn"
    name = "K-Nearest Neighbors"
    description = "Instance-based learning using nearest neighbors"
    icon = "🎯"
    problem_types = [ProblemType.CLASSIFICATION, ProblemType.REGRESSION]
    category = ModelCategory.DISTANCE
    best_for = "Small to medium datasets with local patterns"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="n_neighbors",
                    name="Number of Neighbors (K)",
                    type=FieldType.INT,
                    default=5,
                    min=1,
                    max=50,
                    description="Number of neighbors to use for prediction",
                ),
                HyperparameterField(
                    key="weights",
                    name="Weight Function",
                    type=FieldType.SELECT,
                    default="uniform",
                    options=[
                        {"value": "uniform", "label": "Uniform (all equal)"},
                        {"value": "distance", "label": "Distance (closer = more weight)"},
                    ],
                    description="How to weight neighbor contributions",
                ),
                HyperparameterField(
                    key="metric",
                    name="Distance Metric",
                    type=FieldType.SELECT,
                    default="minkowski",
                    options=[
                        {"value": "minkowski", "label": "Minkowski"},
                        {"value": "euclidean", "label": "Euclidean"},
                        {"value": "manhattan", "label": "Manhattan"},
                        {"value": "cosine", "label": "Cosine"},
                    ],
                    description="Distance metric for neighbor calculation",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="p",
                    name="Minkowski Power (p)",
                    type=FieldType.INT,
                    default=2,
                    min=1,
                    max=5,
                    description="Power parameter for Minkowski metric (1=Manhattan, 2=Euclidean)",
                ),
                HyperparameterField(
                    key="algorithm",
                    name="Algorithm",
                    type=FieldType.SELECT,
                    default="auto",
                    options=[
                        {"value": "auto", "label": "Auto"},
                        {"value": "ball_tree", "label": "Ball Tree"},
                        {"value": "kd_tree", "label": "KD Tree"},
                        {"value": "brute", "label": "Brute Force"},
                    ],
                    description="Algorithm for computing nearest neighbors",
                ),
                HyperparameterField(
                    key="leaf_size",
                    name="Leaf Size",
                    type=FieldType.INT,
                    default=30,
                    min=10,
                    max=100,
                    description="Leaf size for tree-based algorithms",
                ),
            ],
        )

    @classmethod
    def get_supported_metrics(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return [
                "accuracy", "precision", "recall", "f1_score",
                "confusion_matrix", "classification_report"
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
                "confusion_matrix", "class_distribution", "learning_curve"
            ]
        else:
            return [
                "prediction_vs_actual", "residual_plot", "learning_curve"
            ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["confusion_matrix"]
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

        if problem_type == ProblemType.CLASSIFICATION:
            model = KNeighborsClassifier(**params)
        else:
            model = KNeighborsRegressor(**params)

        model.fit(X_train, y_train)
        return model
