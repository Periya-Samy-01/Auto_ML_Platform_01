"""
Metric and plot definitions for the plugin system.

This module provides centralized definitions for all available
evaluation metrics and visualization plots. Plugins reference
these by key rather than implementing their own.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class MetricCategory(str, Enum):
    """Categories for grouping metrics."""
    PERFORMANCE = "performance"
    ERROR = "error"
    PROBABILITY = "probability"
    MATRIX = "matrix"


class PlotCategory(str, Enum):
    """Categories for grouping plots."""
    PERFORMANCE = "performance"
    EXPLAINABILITY = "explainability"
    DIAGNOSTIC = "diagnostic"


@dataclass
class MetricDefinition:
    """Definition of an evaluation metric."""
    key: str
    name: str
    description: str
    category: MetricCategory
    higher_is_better: bool
    applies_to: List[str]  # ["classification", "regression", "clustering"]
    cost: int = 1  # Credit cost to compute

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "higherIsBetter": self.higher_is_better,
            "appliesTo": self.applies_to,
            "cost": self.cost,
        }


@dataclass
class PlotDefinition:
    """Definition of a visualization plot."""
    key: str
    name: str
    description: str
    category: PlotCategory
    applies_to: List[str]  # ["classification", "regression"]
    model_categories: List[str]  # ["tree", "linear", "ensemble", "neural", "all"]
    cost: int = 1  # Credit cost to generate

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "appliesTo": self.applies_to,
            "modelCategories": self.model_categories,
            "cost": self.cost,
        }


# =============================================================================
# CLASSIFICATION METRICS
# =============================================================================

METRIC_ACCURACY = MetricDefinition(
    key="accuracy",
    name="Accuracy",
    description="Proportion of correct predictions among total predictions",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["classification"],
)

METRIC_PRECISION = MetricDefinition(
    key="precision",
    name="Precision",
    description="Proportion of true positives among predicted positives",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["classification"],
)

METRIC_RECALL = MetricDefinition(
    key="recall",
    name="Recall",
    description="Proportion of true positives among actual positives",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["classification"],
)

METRIC_F1_SCORE = MetricDefinition(
    key="f1_score",
    name="F1 Score",
    description="Harmonic mean of precision and recall",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["classification"],
)

METRIC_ROC_AUC = MetricDefinition(
    key="roc_auc",
    name="ROC AUC",
    description="Area under the Receiver Operating Characteristic curve",
    category=MetricCategory.PROBABILITY,
    higher_is_better=True,
    applies_to=["classification"],
)

METRIC_CONFUSION_MATRIX = MetricDefinition(
    key="confusion_matrix",
    name="Confusion Matrix",
    description="Matrix showing true vs predicted class counts",
    category=MetricCategory.MATRIX,
    higher_is_better=True,  # N/A but needed
    applies_to=["classification"],
)

METRIC_CLASSIFICATION_REPORT = MetricDefinition(
    key="classification_report",
    name="Classification Report",
    description="Per-class precision, recall, F1, and support",
    category=MetricCategory.MATRIX,
    higher_is_better=True,
    applies_to=["classification"],
)

METRIC_LOG_LOSS = MetricDefinition(
    key="log_loss",
    name="Log Loss",
    description="Negative log-likelihood of predictions",
    category=MetricCategory.PROBABILITY,
    higher_is_better=False,
    applies_to=["classification"],
)

# =============================================================================
# REGRESSION METRICS
# =============================================================================

METRIC_MSE = MetricDefinition(
    key="mse",
    name="Mean Squared Error",
    description="Average of squared differences between predictions and actual values",
    category=MetricCategory.ERROR,
    higher_is_better=False,
    applies_to=["regression"],
)

METRIC_RMSE = MetricDefinition(
    key="rmse",
    name="Root Mean Squared Error",
    description="Square root of MSE, in same units as target",
    category=MetricCategory.ERROR,
    higher_is_better=False,
    applies_to=["regression"],
)

METRIC_MAE = MetricDefinition(
    key="mae",
    name="Mean Absolute Error",
    description="Average of absolute differences between predictions and actual values",
    category=MetricCategory.ERROR,
    higher_is_better=False,
    applies_to=["regression"],
)

METRIC_R2_SCORE = MetricDefinition(
    key="r2_score",
    name="R² Score",
    description="Proportion of variance explained by the model",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["regression"],
)

METRIC_MAPE = MetricDefinition(
    key="mape",
    name="Mean Absolute Percentage Error",
    description="Average of absolute percentage errors",
    category=MetricCategory.ERROR,
    higher_is_better=False,
    applies_to=["regression"],
)

# =============================================================================
# CLUSTERING METRICS
# =============================================================================

METRIC_SILHOUETTE = MetricDefinition(
    key="silhouette_score",
    name="Silhouette Score",
    description="Measure of cluster cohesion and separation (-1 to 1)",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["clustering"],
)

METRIC_DAVIES_BOULDIN = MetricDefinition(
    key="davies_bouldin_index",
    name="Davies-Bouldin Index",
    description="Average similarity ratio of each cluster with its most similar cluster",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=False,
    applies_to=["clustering"],
)

METRIC_CALINSKI_HARABASZ = MetricDefinition(
    key="calinski_harabasz_index",
    name="Calinski-Harabasz Index",
    description="Ratio of between-cluster to within-cluster dispersion",
    category=MetricCategory.PERFORMANCE,
    higher_is_better=True,
    applies_to=["clustering"],
)

METRIC_INERTIA = MetricDefinition(
    key="inertia",
    name="Inertia",
    description="Sum of squared distances to cluster centers",
    category=MetricCategory.ERROR,
    higher_is_better=False,
    applies_to=["clustering"],
)

# =============================================================================
# PLOTS - CLASSIFICATION
# =============================================================================

PLOT_CONFUSION_MATRIX = PlotDefinition(
    key="confusion_matrix",
    name="Confusion Matrix",
    description="Heatmap showing true vs predicted class counts",
    category=PlotCategory.PERFORMANCE,
    applies_to=["classification"],
    model_categories=["all"],
    cost=1,
)

PLOT_ROC_CURVE = PlotDefinition(
    key="roc_curve",
    name="ROC Curve",
    description="Receiver Operating Characteristic curve showing TPR vs FPR",
    category=PlotCategory.PERFORMANCE,
    applies_to=["classification"],
    model_categories=["all"],
    cost=1,
)

PLOT_PRECISION_RECALL_CURVE = PlotDefinition(
    key="precision_recall_curve",
    name="Precision-Recall Curve",
    description="Trade-off between precision and recall at various thresholds",
    category=PlotCategory.PERFORMANCE,
    applies_to=["classification"],
    model_categories=["all"],
    cost=1,
)

PLOT_CLASS_DISTRIBUTION = PlotDefinition(
    key="class_distribution",
    name="Class Distribution",
    description="Bar chart showing predicted vs actual class distribution",
    category=PlotCategory.DIAGNOSTIC,
    applies_to=["classification"],
    model_categories=["all"],
    cost=1,
)

# =============================================================================
# PLOTS - REGRESSION
# =============================================================================

PLOT_RESIDUAL = PlotDefinition(
    key="residual_plot",
    name="Residual Plot",
    description="Scatter plot of residuals vs predicted values",
    category=PlotCategory.DIAGNOSTIC,
    applies_to=["regression"],
    model_categories=["all"],
    cost=1,
)

PLOT_PREDICTION_VS_ACTUAL = PlotDefinition(
    key="prediction_vs_actual",
    name="Prediction vs Actual",
    description="Scatter plot comparing predictions to actual values",
    category=PlotCategory.PERFORMANCE,
    applies_to=["regression"],
    model_categories=["all"],
    cost=1,
)

PLOT_RESIDUAL_DISTRIBUTION = PlotDefinition(
    key="residual_distribution",
    name="Residual Distribution",
    description="Histogram of residual values",
    category=PlotCategory.DIAGNOSTIC,
    applies_to=["regression"],
    model_categories=["all"],
    cost=1,
)

# =============================================================================
# PLOTS - EXPLAINABILITY (ALL MODELS)
# =============================================================================

PLOT_FEATURE_IMPORTANCE = PlotDefinition(
    key="feature_importance",
    name="Feature Importance",
    description="Bar chart showing relative importance of each feature",
    category=PlotCategory.EXPLAINABILITY,
    applies_to=["classification", "regression"],
    model_categories=["tree", "ensemble", "linear"],
    cost=1,
)

PLOT_LEARNING_CURVE = PlotDefinition(
    key="learning_curve",
    name="Learning Curve",
    description="Training and validation scores vs training set size",
    category=PlotCategory.DIAGNOSTIC,
    applies_to=["classification", "regression"],
    model_categories=["all"],
    cost=2,
)

PLOT_SHAP_SUMMARY = PlotDefinition(
    key="shap_summary",
    name="SHAP Summary",
    description="SHAP values showing feature impact on predictions",
    category=PlotCategory.EXPLAINABILITY,
    applies_to=["classification", "regression"],
    model_categories=["all"],
    cost=3,
)

PLOT_SHAP_WATERFALL = PlotDefinition(
    key="shap_waterfall",
    name="SHAP Waterfall",
    description="SHAP values for a single prediction",
    category=PlotCategory.EXPLAINABILITY,
    applies_to=["classification", "regression"],
    model_categories=["all"],
    cost=2,
)

PLOT_PARTIAL_DEPENDENCE = PlotDefinition(
    key="partial_dependence",
    name="Partial Dependence",
    description="Effect of a feature on predictions",
    category=PlotCategory.EXPLAINABILITY,
    applies_to=["classification", "regression"],
    model_categories=["all"],
    cost=2,
)

PLOT_COEFFICIENT = PlotDefinition(
    key="coefficient_plot",
    name="Coefficient Plot",
    description="Bar chart showing model coefficients",
    category=PlotCategory.EXPLAINABILITY,
    applies_to=["classification", "regression"],
    model_categories=["linear"],
    cost=1,
)

# =============================================================================
# PLOTS - CLUSTERING
# =============================================================================

PLOT_CLUSTER_SCATTER = PlotDefinition(
    key="cluster_scatter",
    name="Cluster Scatter Plot",
    description="2D scatter plot of data points colored by cluster",
    category=PlotCategory.PERFORMANCE,
    applies_to=["clustering"],
    model_categories=["clustering"],
    cost=1,
)

PLOT_ELBOW = PlotDefinition(
    key="elbow_plot",
    name="Elbow Plot",
    description="Inertia vs number of clusters for optimal k selection",
    category=PlotCategory.DIAGNOSTIC,
    applies_to=["clustering"],
    model_categories=["clustering"],
    cost=2,
)

PLOT_SILHOUETTE = PlotDefinition(
    key="silhouette_plot",
    name="Silhouette Plot",
    description="Silhouette scores for each sample by cluster",
    category=PlotCategory.DIAGNOSTIC,
    applies_to=["clustering"],
    model_categories=["clustering"],
    cost=1,
)

# =============================================================================
# REGISTRIES
# =============================================================================

METRIC_DEFINITIONS: Dict[str, MetricDefinition] = {
    # Classification
    "accuracy": METRIC_ACCURACY,
    "precision": METRIC_PRECISION,
    "recall": METRIC_RECALL,
    "f1_score": METRIC_F1_SCORE,
    "roc_auc": METRIC_ROC_AUC,
    "confusion_matrix": METRIC_CONFUSION_MATRIX,
    "classification_report": METRIC_CLASSIFICATION_REPORT,
    "log_loss": METRIC_LOG_LOSS,
    # Regression
    "mse": METRIC_MSE,
    "rmse": METRIC_RMSE,
    "mae": METRIC_MAE,
    "r2_score": METRIC_R2_SCORE,
    "mape": METRIC_MAPE,
    # Clustering
    "silhouette_score": METRIC_SILHOUETTE,
    "davies_bouldin_index": METRIC_DAVIES_BOULDIN,
    "calinski_harabasz_index": METRIC_CALINSKI_HARABASZ,
    "inertia": METRIC_INERTIA,
}

PLOT_DEFINITIONS: Dict[str, PlotDefinition] = {
    # Classification
    "confusion_matrix": PLOT_CONFUSION_MATRIX,
    "roc_curve": PLOT_ROC_CURVE,
    "precision_recall_curve": PLOT_PRECISION_RECALL_CURVE,
    "class_distribution": PLOT_CLASS_DISTRIBUTION,
    # Regression
    "residual_plot": PLOT_RESIDUAL,
    "prediction_vs_actual": PLOT_PREDICTION_VS_ACTUAL,
    "residual_distribution": PLOT_RESIDUAL_DISTRIBUTION,
    # Explainability
    "feature_importance": PLOT_FEATURE_IMPORTANCE,
    "learning_curve": PLOT_LEARNING_CURVE,
    "shap_summary": PLOT_SHAP_SUMMARY,
    "shap_waterfall": PLOT_SHAP_WATERFALL,
    "partial_dependence": PLOT_PARTIAL_DEPENDENCE,
    "coefficient_plot": PLOT_COEFFICIENT,
    # Clustering
    "cluster_scatter": PLOT_CLUSTER_SCATTER,
    "elbow_plot": PLOT_ELBOW,
    "silhouette_plot": PLOT_SILHOUETTE,
}


def get_metric_definition(key: str) -> Optional[MetricDefinition]:
    """Get a metric definition by key."""
    return METRIC_DEFINITIONS.get(key)


def get_plot_definition(key: str) -> Optional[PlotDefinition]:
    """Get a plot definition by key."""
    return PLOT_DEFINITIONS.get(key)


def get_metrics_for_problem_type(problem_type: str) -> List[MetricDefinition]:
    """Get all metrics that apply to a problem type."""
    return [
        metric
        for metric in METRIC_DEFINITIONS.values()
        if problem_type in metric.applies_to
    ]


def get_plots_for_problem_type(
    problem_type: str,
    model_category: Optional[str] = None
) -> List[PlotDefinition]:
    """Get all plots that apply to a problem type and optionally model category."""
    plots = [
        plot
        for plot in PLOT_DEFINITIONS.values()
        if problem_type in plot.applies_to
    ]

    if model_category:
        plots = [
            plot
            for plot in plots
            if "all" in plot.model_categories or model_category in plot.model_categories
        ]

    return plots
