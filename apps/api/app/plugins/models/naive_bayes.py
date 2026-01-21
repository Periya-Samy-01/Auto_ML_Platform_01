"""
Naive Bayes model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class NaiveBayesPlugin(BaseModelPlugin):
    """
    Naive Bayes plugin - probabilistic classifier.

    Fast, simple classifier based on Bayes' theorem with
    independence assumptions between features.
    """

    slug = "naive_bayes"
    name = "Naive Bayes"
    description = "Probabilistic classifier based on Bayes' theorem"
    icon = "🎲"
    problem_types = [ProblemType.CLASSIFICATION]
    category = ModelCategory.LINEAR
    best_for = "Text classification and when features are independent"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="variant",
                    name="Naive Bayes Variant",
                    type=FieldType.SELECT,
                    default="gaussian",
                    options=[
                        {"value": "gaussian", "label": "Gaussian (continuous features)"},
                        {"value": "multinomial", "label": "Multinomial (count features)"},
                        {"value": "bernoulli", "label": "Bernoulli (binary features)"},
                    ],
                    description="Type of Naive Bayes algorithm",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="var_smoothing",
                    name="Variance Smoothing",
                    type=FieldType.FLOAT,
                    default=1e-9,
                    min=1e-12,
                    max=1e-3,
                    description="Portion of largest variance added to variances (Gaussian only)",
                ),
                HyperparameterField(
                    key="alpha",
                    name="Smoothing Parameter",
                    type=FieldType.FLOAT,
                    default=1.0,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    description="Additive smoothing parameter (Multinomial/Bernoulli)",
                ),
                HyperparameterField(
                    key="fit_prior",
                    name="Fit Prior",
                    type=FieldType.BOOL,
                    default=True,
                    description="Whether to learn class prior probabilities",
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
        return ["accuracy", "f1_score", "confusion_matrix"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        return [
            "confusion_matrix", "roc_curve", "precision_recall_curve",
            "class_distribution", "learning_curve"
        ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        return ["confusion_matrix", "roc_curve"]

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

        variant = params.pop("variant", "gaussian")
        var_smoothing = params.pop("var_smoothing", 1e-9)
        alpha = params.pop("alpha", 1.0)
        fit_prior = params.get("fit_prior", True)

        if variant == "gaussian":
            model = GaussianNB(var_smoothing=var_smoothing)
        elif variant == "multinomial":
            # Multinomial requires non-negative features
            model = MultinomialNB(alpha=alpha, fit_prior=fit_prior)
        elif variant == "bernoulli":
            model = BernoulliNB(alpha=alpha, fit_prior=fit_prior)
        else:
            model = GaussianNB(var_smoothing=var_smoothing)

        model.fit(X_train, y_train)
        return model
