"""
Linear Regression model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class LinearRegressionPlugin(BaseModelPlugin):
    """
    Linear Regression plugin - linear regression model.

    Fast, interpretable baseline for regression tasks.
    Supports regularization variants (Ridge, Lasso, ElasticNet).
    """

    slug = "linear_regression"
    name = "Linear Regression"
    description = "Linear model for regression with optional regularization"
    icon = "📉"
    problem_types = [ProblemType.REGRESSION]
    category = ModelCategory.LINEAR
    best_for = "Linear relationships and interpretable models"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="regularization",
                    name="Regularization Type",
                    type=FieldType.SELECT,
                    default="none",
                    options=[
                        {"value": "none", "label": "None (OLS)"},
                        {"value": "ridge", "label": "Ridge (L2)"},
                        {"value": "lasso", "label": "Lasso (L1)"},
                        {"value": "elasticnet", "label": "Elastic Net"},
                    ],
                    description="Type of regularization to apply",
                ),
                HyperparameterField(
                    key="alpha",
                    name="Regularization Strength",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.0001,
                    max=100.0,
                    step=0.1,
                    description="Strength of regularization (higher = stronger)",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="fit_intercept",
                    name="Fit Intercept",
                    type=FieldType.BOOL,
                    default=True,
                    description="Whether to calculate the intercept",
                ),
                HyperparameterField(
                    key="l1_ratio",
                    name="L1 Ratio (Elastic Net)",
                    type=FieldType.FLOAT,
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.1,
                    description="L1/L2 mixing ratio for Elastic Net (0=Ridge, 1=Lasso)",
                ),
                HyperparameterField(
                    key="max_iter",
                    name="Max Iterations",
                    type=FieldType.INT,
                    default=1000,
                    min=100,
                    max=10000,
                    description="Maximum iterations for iterative solvers",
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
        return ["mse", "rmse", "mae", "r2_score", "mape"]

    @classmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        return ["rmse", "r2_score", "mae"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        return [
            "prediction_vs_actual", "residual_plot", "residual_distribution",
            "coefficient_plot", "learning_curve"
        ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        return ["prediction_vs_actual", "coefficient_plot", "residual_plot"]

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

        regularization = params.pop("regularization", "none")
        alpha = params.pop("alpha", 1.0)
        l1_ratio = params.pop("l1_ratio", 0.5)
        fit_intercept = params.get("fit_intercept", True)
        max_iter = params.get("max_iter", 1000)
        random_state = params.get("random_state", 42)

        if regularization == "none":
            model = LinearRegression(fit_intercept=fit_intercept)
        elif regularization == "ridge":
            model = Ridge(alpha=alpha, fit_intercept=fit_intercept, random_state=random_state)
        elif regularization == "lasso":
            model = Lasso(
                alpha=alpha,
                fit_intercept=fit_intercept,
                max_iter=max_iter,
                random_state=random_state
            )
        elif regularization == "elasticnet":
            model = ElasticNet(
                alpha=alpha,
                l1_ratio=l1_ratio,
                fit_intercept=fit_intercept,
                max_iter=max_iter,
                random_state=random_state
            )
        else:
            model = LinearRegression(fit_intercept=fit_intercept)

        model.fit(X_train, y_train)
        return model
