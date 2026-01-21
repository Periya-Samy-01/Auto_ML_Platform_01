"""
XGBoost model plugin.
"""

from typing import Any, Dict, List

import numpy as np

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class XGBoostPlugin(BaseModelPlugin):
    """
    XGBoost plugin - gradient boosting decision trees.

    High-performance model for both classification and regression.
    """

    slug = "xgboost"
    name = "XGBoost"
    description = "Gradient boosting with regularization for high performance"
    icon = "⚡"
    problem_types = [ProblemType.CLASSIFICATION, ProblemType.REGRESSION]
    category = ModelCategory.ENSEMBLE
    best_for = "Structured/tabular data with optimal performance"

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
                    max=1000,
                    step=10,
                    description="Number of boosting rounds",
                ),
                HyperparameterField(
                    key="max_depth",
                    name="Max Depth",
                    type=FieldType.INT,
                    default=6,
                    min=1,
                    max=20,
                    description="Maximum tree depth for base learners",
                ),
                HyperparameterField(
                    key="learning_rate",
                    name="Learning Rate",
                    type=FieldType.FLOAT,
                    default=0.1,
                    min=0.01,
                    max=1.0,
                    step=0.01,
                    description="Boosting learning rate (eta)",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="min_child_weight",
                    name="Min Child Weight",
                    type=FieldType.INT,
                    default=1,
                    min=1,
                    max=20,
                    description="Minimum sum of instance weight in a child",
                ),
                HyperparameterField(
                    key="subsample",
                    name="Subsample Ratio",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.5,
                    max=1.0,
                    step=0.1,
                    description="Subsample ratio of training instances",
                ),
                HyperparameterField(
                    key="colsample_bytree",
                    name="Column Sample Ratio",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.5,
                    max=1.0,
                    step=0.1,
                    description="Subsample ratio of columns per tree",
                ),
                HyperparameterField(
                    key="reg_alpha",
                    name="L1 Regularization",
                    type=FieldType.FLOAT,
                    default=0.0,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    description="L1 regularization on weights",
                ),
                HyperparameterField(
                    key="reg_lambda",
                    name="L2 Regularization",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    description="L2 regularization on weights",
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
            return ["rmse", "r2_score", "mae"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return [
                "confusion_matrix", "roc_curve", "precision_recall_curve",
                "feature_importance", "learning_curve", "class_distribution",
                "shap_summary"
            ]
        else:
            return [
                "prediction_vs_actual", "residual_plot", "residual_distribution",
                "feature_importance", "learning_curve", "shap_summary"
            ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        if problem_type == ProblemType.CLASSIFICATION:
            return ["confusion_matrix", "feature_importance", "roc_curve"]
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
        # Import here to avoid dependency issues if xgboost not installed
        try:
            from xgboost import XGBClassifier, XGBRegressor
        except ImportError:
            raise ImportError("XGBoost is not installed. Install with: pip install xgboost")

        params = cls.get_default_hyperparameters()
        params.update(hyperparameters)

        # Ensure verbosity is off
        params["verbosity"] = 0

        if problem_type == ProblemType.CLASSIFICATION:
            model = XGBClassifier(**params, use_label_encoder=False, eval_metric="logloss")
        else:
            model = XGBRegressor(**params)

        model.fit(X_train, y_train)
        return model
