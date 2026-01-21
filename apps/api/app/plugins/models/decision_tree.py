"""
Decision Tree model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class DecisionTreePlugin(BaseModelPlugin):
    """
    Decision Tree plugin - single tree classifier/regressor.

    Simple, interpretable model that works for both classification and regression.
    """

    slug = "decision_tree"
    name = "Decision Tree"
    description = "Simple, interpretable tree-based model"
    icon = "🌳"
    problem_types = [ProblemType.CLASSIFICATION, ProblemType.REGRESSION]
    category = ModelCategory.TREE
    best_for = "Interpretable models and understanding feature interactions"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="max_depth",
                    name="Max Depth",
                    type=FieldType.INT,
                    default=5,
                    min=1,
                    max=30,
                    nullable=True,
                    null_label="None (unlimited)",
                    description="Maximum depth of the tree",
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
                HyperparameterField(
                    key="min_samples_split",
                    name="Min Samples Split",
                    type=FieldType.INT,
                    default=2,
                    min=2,
                    max=50,
                    description="Minimum samples required to split a node",
                ),
            ],
            advanced=[
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
                    default=None,
                    options=[
                        {"value": None, "label": "All Features"},
                        {"value": "sqrt", "label": "Square Root"},
                        {"value": "log2", "label": "Log2"},
                    ],
                    description="Number of features to consider for best split",
                ),
                HyperparameterField(
                    key="max_leaf_nodes",
                    name="Max Leaf Nodes",
                    type=FieldType.INT,
                    default=None,
                    min=2,
                    max=100,
                    nullable=True,
                    null_label="None (unlimited)",
                    description="Maximum number of leaf nodes",
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
            return ["mse", "rmse", "mae", "r2_score", "mape"]

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
                "confusion_matrix", "roc_curve", "feature_importance",
                "learning_curve", "class_distribution"
            ]
        else:
            return [
                "prediction_vs_actual", "residual_plot",
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
        params = cls.get_default_hyperparameters()
        params.update(hyperparameters)

        # Sanitize parameters: convert string 'none' to Python None
        for key, value in list(params.items()):
            if isinstance(value, str) and value.lower() == 'none':
                params[key] = None

        # Handle deprecated max_features='auto' (removed in sklearn 1.1+)
        if params.get('max_features') == 'auto':
            params['max_features'] = None

        # Handle criterion for regression
        if problem_type == ProblemType.REGRESSION:
            if params.get("criterion") in ["gini", "entropy"]:
                params["criterion"] = "squared_error"

        # Filter to only valid sklearn parameters
        valid_params = [
            'criterion', 'splitter', 'max_depth', 'min_samples_split',
            'min_samples_leaf', 'min_weight_fraction_leaf', 'max_features',
            'random_state', 'max_leaf_nodes', 'min_impurity_decrease',
            'class_weight', 'ccp_alpha'
        ]
        filtered_params = {k: v for k, v in params.items() if k in valid_params}

        if problem_type == ProblemType.CLASSIFICATION:
            model = DecisionTreeClassifier(**filtered_params)
        else:
            # Remove class_weight for regression
            filtered_params.pop('class_weight', None)
            model = DecisionTreeRegressor(**filtered_params)

        model.fit(X_train, y_train)
        return model
