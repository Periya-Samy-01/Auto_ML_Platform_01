"""
Random Forest model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class RandomForestPlugin(BaseModelPlugin):
    """
    Random Forest plugin - ensemble of decision trees.

    Works for both classification and regression tasks.
    """

    slug = "random_forest"
    name = "Random Forest"
    description = "Ensemble of decision trees with bootstrap aggregating"
    icon = "🌲"
    problem_types = [ProblemType.CLASSIFICATION, ProblemType.REGRESSION]
    category = ModelCategory.ENSEMBLE
    best_for = "Tabular data with complex non-linear relationships"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="n_estimators",
                    name="Number of Trees",
                    type=FieldType.INT,
                    default=100,
                    min=10,
                    max=500,
                    step=10,
                    description="Number of trees in the forest",
                ),
                HyperparameterField(
                    key="max_depth",
                    name="Max Depth",
                    type=FieldType.INT,
                    default=None,
                    min=1,
                    max=50,
                    nullable=True,
                    null_label="None (unlimited)",
                    description="Maximum depth of each tree",
                ),
                HyperparameterField(
                    key="criterion",
                    name="Split Criterion",
                    type=FieldType.SELECT,
                    default="gini",
                    options=[
                        {"value": "gini", "label": "Gini Impurity"},
                        {"value": "entropy", "label": "Entropy"},
                    ],
                    description="Function to measure split quality",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="min_samples_split",
                    name="Min Samples Split",
                    type=FieldType.INT,
                    default=2,
                    min=2,
                    max=20,
                    description="Minimum samples required to split a node",
                ),
                HyperparameterField(
                    key="min_samples_leaf",
                    name="Min Samples Leaf",
                    type=FieldType.INT,
                    default=1,
                    min=1,
                    max=20,
                    description="Minimum samples required at a leaf node",
                ),
                HyperparameterField(
                    key="max_features",
                    name="Max Features",
                    type=FieldType.SELECT,
                    default="sqrt",
                    options=[
                        {"value": "sqrt", "label": "Square Root"},
                        {"value": "log2", "label": "Log2"},
                        {"value": None, "label": "All Features"},
                    ],
                    description="Number of features to consider for best split",
                ),
                HyperparameterField(
                    key="bootstrap",
                    name="Bootstrap",
                    type=FieldType.BOOL,
                    default=True,
                    description="Whether to use bootstrap samples",
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
        else:  # REGRESSION
            return ["mse", "rmse", "mae", "r2_score", "mape"]

    @classmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["accuracy", "f1_score", "confusion_matrix"]
        else:
            return ["rmse", "r2_score", "mae"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return [
                "confusion_matrix", "roc_curve", "precision_recall_curve",
                "feature_importance", "learning_curve", "class_distribution"
            ]
        else:
            return [
                "prediction_vs_actual", "residual_plot", "residual_distribution",
                "feature_importance", "learning_curve"
            ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["confusion_matrix", "feature_importance"]
        else:
            return ["prediction_vs_actual", "feature_importance"]

    @classmethod
    def train(
        cls,
        X_train: np.ndarray,
        y_train: np.ndarray,
        hyperparameters: Dict[str, Any],
        problem_type: ProblemType,
    ) -> Any:
        # Prepare hyperparameters
        params = cls.get_default_hyperparameters()
        params.update(hyperparameters)

        # Handle criterion for regression (different options)
        if problem_type == ProblemType.REGRESSION:
            if params.get("criterion") in ["gini", "entropy"]:
                params["criterion"] = "squared_error"

        # Create and train model
        if problem_type == ProblemType.CLASSIFICATION:
            model = RandomForestClassifier(**params)
        else:
            model = RandomForestRegressor(**params)

        model.fit(X_train, y_train)
        return model
