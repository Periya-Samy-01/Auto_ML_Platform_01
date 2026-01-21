"""
Shared visualization functions.

This module provides the actual plot generation logic for all visualizations.
Plugins declare which plots they support, and this module handles execution.
"""

import base64
import io
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
)
from sklearn.model_selection import learning_curve

from app.plugins.shared.constants import PLOT_DEFINITIONS, get_plot_definition


# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100


def get_available_plots(problem_type: str, model_category: Optional[str] = None) -> List[str]:
    """Get list of available plot keys for a problem type and model category."""
    plots = []
    for key, plot_def in PLOT_DEFINITIONS.items():
        if problem_type not in plot_def.applies_to:
            continue
        if model_category:
            if "all" not in plot_def.model_categories and model_category not in plot_def.model_categories:
                continue
        plots.append(key)
    return plots


def generate_plot(
    key: str,
    model: Any,
    X_train: Optional[np.ndarray] = None,
    X_test: Optional[np.ndarray] = None,
    y_train: Optional[np.ndarray] = None,
    y_test: Optional[np.ndarray] = None,
    y_pred: Optional[np.ndarray] = None,
    y_pred_proba: Optional[np.ndarray] = None,
    feature_names: Optional[List[str]] = None,
    class_names: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate a single plot by key.

    Args:
        key: Plot key from constants
        model: Trained model object
        X_train: Training features
        X_test: Test features
        y_train: Training labels
        y_test: Test labels
        y_pred: Predictions on test set
        y_pred_proba: Prediction probabilities
        feature_names: Names of features
        class_names: Names of classes (classification)
        **kwargs: Additional plot-specific arguments

    Returns:
        Dictionary with 'image' (base64) and 'metadata'
    """
    plot_def = get_plot_definition(key)
    if plot_def is None:
        raise ValueError(f"Unknown plot: {key}")

    fig, ax = plt.subplots(figsize=(10, 6))

    try:
        # Classification plots
        if key == "confusion_matrix":
            _plot_confusion_matrix(ax, y_test, y_pred, class_names)

        elif key == "roc_curve":
            _plot_roc_curve(ax, y_test, y_pred_proba, class_names)

        elif key == "precision_recall_curve":
            _plot_precision_recall_curve(ax, y_test, y_pred_proba)

        elif key == "class_distribution":
            _plot_class_distribution(ax, y_test, y_pred, class_names)

        # Regression plots
        elif key == "residual_plot":
            _plot_residuals(ax, y_test, y_pred)

        elif key == "prediction_vs_actual":
            _plot_prediction_vs_actual(ax, y_test, y_pred)

        elif key == "residual_distribution":
            _plot_residual_distribution(ax, y_test, y_pred)

        # Explainability plots
        elif key == "feature_importance":
            _plot_feature_importance(ax, model, feature_names)

        elif key == "learning_curve":
            plt.close(fig)
            fig, ax = _plot_learning_curve(model, X_train, y_train)

        elif key == "coefficient_plot":
            _plot_coefficients(ax, model, feature_names)

        # SHAP plots (simplified version)
        elif key == "shap_summary":
            _plot_shap_summary_placeholder(ax, model, X_test, feature_names)

        elif key == "shap_waterfall":
            _plot_shap_waterfall_placeholder(ax)

        elif key == "partial_dependence":
            _plot_partial_dependence_placeholder(ax)

        # Clustering plots
        elif key == "cluster_scatter":
            _plot_cluster_scatter(ax, X_test, y_pred)

        elif key == "elbow_plot":
            _plot_elbow_placeholder(ax)

        elif key == "silhouette_plot":
            _plot_silhouette_placeholder(ax, X_test, y_pred)

        else:
            raise ValueError(f"Plot '{key}' generation not implemented")

        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return {
            "key": key,
            "name": plot_def.name,
            "image": image_base64,
            "format": "png",
        }

    finally:
        plt.close(fig)


def generate_plots(
    plot_keys: List[str],
    model: Any,
    **kwargs
) -> List[Dict[str, Any]]:
    """Generate multiple plots."""
    results = []
    for key in plot_keys:
        try:
            result = generate_plot(key, model, **kwargs)
            results.append(result)
        except Exception as e:
            results.append({
                "key": key,
                "error": str(e),
            })
    return results


# =============================================================================
# CLASSIFICATION PLOT IMPLEMENTATIONS
# =============================================================================

def _plot_confusion_matrix(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: Optional[List[str]] = None
) -> None:
    """Plot confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)

    if class_names is None:
        class_names = [str(i) for i in range(cm.shape[0])]

    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax
    )
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title('Confusion Matrix')


def _plot_roc_curve(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred_proba: Optional[np.ndarray],
    class_names: Optional[List[str]] = None
) -> None:
    """Plot ROC curve."""
    if y_pred_proba is None:
        ax.text(0.5, 0.5, 'ROC curve requires probability predictions',
                ha='center', va='center', transform=ax.transAxes)
        return

    n_classes = len(np.unique(y_true))

    if n_classes == 2:
        # Binary classification
        if y_pred_proba.ndim == 2:
            proba = y_pred_proba[:, 1]
        else:
            proba = y_pred_proba
        fpr, tpr, _ = roc_curve(y_true, proba)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
    else:
        # Multiclass - one vs rest
        from sklearn.preprocessing import label_binarize
        y_true_bin = label_binarize(y_true, classes=np.unique(y_true))

        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_pred_proba[:, i])
            roc_auc = auc(fpr, tpr)
            label = class_names[i] if class_names else f'Class {i}'
            ax.plot(fpr, tpr, lw=2, label=f'{label} (AUC = {roc_auc:.3f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    ax.legend(loc='lower right')


def _plot_precision_recall_curve(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred_proba: Optional[np.ndarray]
) -> None:
    """Plot precision-recall curve."""
    if y_pred_proba is None:
        ax.text(0.5, 0.5, 'P-R curve requires probability predictions',
                ha='center', va='center', transform=ax.transAxes)
        return

    n_classes = len(np.unique(y_true))

    if n_classes == 2:
        if y_pred_proba.ndim == 2:
            proba = y_pred_proba[:, 1]
        else:
            proba = y_pred_proba
        precision, recall, _ = precision_recall_curve(y_true, proba)
        ap = average_precision_score(y_true, proba)
        ax.plot(recall, precision, lw=2, label=f'AP = {ap:.3f}')

    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_title('Precision-Recall Curve')
    ax.legend(loc='lower left')


def _plot_class_distribution(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: Optional[List[str]] = None
) -> None:
    """Plot class distribution comparison."""
    classes = np.unique(np.concatenate([y_true, y_pred]))
    if class_names is None:
        class_names = [str(c) for c in classes]

    true_counts = [np.sum(y_true == c) for c in classes]
    pred_counts = [np.sum(y_pred == c) for c in classes]

    x = np.arange(len(classes))
    width = 0.35

    ax.bar(x - width/2, true_counts, width, label='Actual', color='steelblue')
    ax.bar(x + width/2, pred_counts, width, label='Predicted', color='coral')

    ax.set_xlabel('Class')
    ax.set_ylabel('Count')
    ax.set_title('Class Distribution: Actual vs Predicted')
    ax.set_xticks(x)
    ax.set_xticklabels(class_names)
    ax.legend()


# =============================================================================
# REGRESSION PLOT IMPLEMENTATIONS
# =============================================================================

def _plot_residuals(ax: plt.Axes, y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """Plot residuals vs predicted values."""
    residuals = y_true - y_pred

    ax.scatter(y_pred, residuals, alpha=0.5, edgecolors='none')
    ax.axhline(y=0, color='r', linestyle='--', lw=1)
    ax.set_xlabel('Predicted Values')
    ax.set_ylabel('Residuals')
    ax.set_title('Residual Plot')


def _plot_prediction_vs_actual(ax: plt.Axes, y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """Plot prediction vs actual scatter."""
    ax.scatter(y_true, y_pred, alpha=0.5, edgecolors='none')

    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=1, label='Perfect Prediction')

    ax.set_xlabel('Actual Values')
    ax.set_ylabel('Predicted Values')
    ax.set_title('Prediction vs Actual')
    ax.legend()


def _plot_residual_distribution(ax: plt.Axes, y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """Plot residual distribution histogram."""
    residuals = y_true - y_pred

    ax.hist(residuals, bins=30, edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='r', linestyle='--', lw=1)
    ax.set_xlabel('Residual')
    ax.set_ylabel('Frequency')
    ax.set_title('Residual Distribution')


# =============================================================================
# EXPLAINABILITY PLOT IMPLEMENTATIONS
# =============================================================================

def _plot_feature_importance(
    ax: plt.Axes,
    model: Any,
    feature_names: Optional[List[str]] = None
) -> None:
    """Plot feature importance bar chart."""
    # Try different attributes for feature importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_).flatten()
    else:
        ax.text(0.5, 0.5, 'Feature importance not available for this model',
                ha='center', va='center', transform=ax.transAxes)
        return

    if feature_names is None:
        feature_names = [f'Feature {i}' for i in range(len(importances))]

    # Sort by importance
    indices = np.argsort(importances)[::-1]
    sorted_importances = importances[indices]
    sorted_names = [feature_names[i] for i in indices]

    # Limit to top 20
    if len(sorted_names) > 20:
        sorted_names = sorted_names[:20]
        sorted_importances = sorted_importances[:20]

    y_pos = np.arange(len(sorted_names))
    ax.barh(y_pos, sorted_importances, align='center', color='steelblue')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_names)
    ax.invert_yaxis()
    ax.set_xlabel('Importance')
    ax.set_title('Feature Importance')


def _plot_learning_curve(
    model: Any,
    X: np.ndarray,
    y: np.ndarray
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot learning curve."""
    fig, ax = plt.subplots(figsize=(10, 6))

    try:
        train_sizes, train_scores, test_scores = learning_curve(
            model, X, y,
            cv=5,
            n_jobs=-1,
            train_sizes=np.linspace(0.1, 1.0, 10),
            scoring='accuracy' if hasattr(model, 'predict_proba') else 'neg_mean_squared_error'
        )

        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)

        ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='blue')
        ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color='orange')
        ax.plot(train_sizes, train_mean, 'o-', color='blue', label='Training score')
        ax.plot(train_sizes, test_mean, 'o-', color='orange', label='Cross-validation score')

        ax.set_xlabel('Training Set Size')
        ax.set_ylabel('Score')
        ax.set_title('Learning Curve')
        ax.legend(loc='best')

    except Exception as e:
        ax.text(0.5, 0.5, f'Could not generate learning curve:\n{str(e)}',
                ha='center', va='center', transform=ax.transAxes)

    return fig, ax


def _plot_coefficients(
    ax: plt.Axes,
    model: Any,
    feature_names: Optional[List[str]] = None
) -> None:
    """Plot model coefficients (for linear models)."""
    if not hasattr(model, 'coef_'):
        ax.text(0.5, 0.5, 'Coefficient plot only available for linear models',
                ha='center', va='center', transform=ax.transAxes)
        return

    coefs = model.coef_.flatten()

    if feature_names is None:
        feature_names = [f'Feature {i}' for i in range(len(coefs))]

    # Sort by absolute value
    indices = np.argsort(np.abs(coefs))[::-1]
    sorted_coefs = coefs[indices]
    sorted_names = [feature_names[i] for i in indices]

    # Limit to top 20
    if len(sorted_names) > 20:
        sorted_names = sorted_names[:20]
        sorted_coefs = sorted_coefs[:20]

    colors = ['green' if c > 0 else 'red' for c in sorted_coefs]

    y_pos = np.arange(len(sorted_names))
    ax.barh(y_pos, sorted_coefs, align='center', color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_names)
    ax.invert_yaxis()
    ax.axvline(x=0, color='black', linestyle='-', lw=0.5)
    ax.set_xlabel('Coefficient')
    ax.set_title('Model Coefficients')


# =============================================================================
# SHAP PLACEHOLDERS (Full implementation would require shap library)
# =============================================================================

def _plot_shap_summary_placeholder(
    ax: plt.Axes,
    model: Any,
    X: Optional[np.ndarray],
    feature_names: Optional[List[str]]
) -> None:
    """Placeholder for SHAP summary plot."""
    ax.text(0.5, 0.5,
            'SHAP Summary Plot\n\nFull implementation requires shap library.\n'
            'Install with: pip install shap',
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    ax.set_title('SHAP Summary (Placeholder)')


def _plot_shap_waterfall_placeholder(ax: plt.Axes) -> None:
    """Placeholder for SHAP waterfall plot."""
    ax.text(0.5, 0.5,
            'SHAP Waterfall Plot\n\nFull implementation requires shap library.',
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    ax.set_title('SHAP Waterfall (Placeholder)')


def _plot_partial_dependence_placeholder(ax: plt.Axes) -> None:
    """Placeholder for partial dependence plot."""
    ax.text(0.5, 0.5,
            'Partial Dependence Plot\n\nSelect a feature to visualize.',
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    ax.set_title('Partial Dependence (Placeholder)')


# =============================================================================
# CLUSTERING PLOT IMPLEMENTATIONS
# =============================================================================

def _plot_cluster_scatter(
    ax: plt.Axes,
    X: np.ndarray,
    labels: np.ndarray
) -> None:
    """Plot cluster scatter (2D projection)."""
    if X is None or labels is None:
        ax.text(0.5, 0.5, 'Data required for cluster scatter plot',
                ha='center', va='center', transform=ax.transAxes)
        return

    # Use first 2 dimensions or PCA if more
    if X.shape[1] > 2:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        X_2d = pca.fit_transform(X)
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    else:
        X_2d = X
        ax.set_xlabel('Feature 1')
        ax.set_ylabel('Feature 2')

    scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis', alpha=0.6)
    ax.set_title('Cluster Visualization')
    plt.colorbar(scatter, ax=ax, label='Cluster')


def _plot_elbow_placeholder(ax: plt.Axes) -> None:
    """Placeholder for elbow plot."""
    ax.text(0.5, 0.5,
            'Elbow Plot\n\nRequires running multiple k-means fits.',
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    ax.set_title('Elbow Plot (Placeholder)')


def _plot_silhouette_placeholder(
    ax: plt.Axes,
    X: Optional[np.ndarray],
    labels: Optional[np.ndarray]
) -> None:
    """Placeholder for silhouette plot."""
    ax.text(0.5, 0.5,
            'Silhouette Plot\n\nShows silhouette coefficient for each sample.',
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    ax.set_title('Silhouette Plot (Placeholder)')
