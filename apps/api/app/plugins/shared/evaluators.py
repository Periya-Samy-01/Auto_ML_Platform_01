"""
Shared evaluation metric functions.

This module provides the actual computation logic for all evaluation metrics.
Plugins declare which metrics they support, and this module handles execution.
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    log_loss,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)

from app.plugins.shared.constants import METRIC_DEFINITIONS, get_metric_definition


def get_available_metrics(problem_type: str) -> List[str]:
    """Get list of available metric keys for a problem type."""
    return [
        key
        for key, metric in METRIC_DEFINITIONS.items()
        if problem_type in metric.applies_to
    ]


def compute_metric(
    key: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    X: Optional[np.ndarray] = None,
    **kwargs
) -> Any:
    """
    Compute a single metric by key.

    Args:
        key: Metric key from constants
        y_true: True labels/values
        y_pred: Predicted labels/values
        y_pred_proba: Prediction probabilities (classification)
        X: Feature matrix (for clustering metrics)
        **kwargs: Additional metric-specific arguments

    Returns:
        Computed metric value
    """
    # Normalize metric key aliases
    key_aliases = {
        "f1": "f1_score",
        "r2": "r2_score",
        "auc": "roc_auc",
        "auc_roc": "roc_auc",
    }
    key = key_aliases.get(key, key)

    metric_def = get_metric_definition(key)
    if metric_def is None:
        raise ValueError(f"Unknown metric: {key}")

    # Classification metrics
    if key == "accuracy":
        return float(accuracy_score(y_true, y_pred))

    elif key == "precision":
        average = _get_average(y_true)
        return float(precision_score(y_true, y_pred, average=average, zero_division=0))

    elif key == "recall":
        average = _get_average(y_true)
        return float(recall_score(y_true, y_pred, average=average, zero_division=0))

    elif key == "f1_score":
        average = _get_average(y_true)
        return float(f1_score(y_true, y_pred, average=average, zero_division=0))

    elif key == "roc_auc":
        if y_pred_proba is None:
            return None
        try:
            n_classes = len(np.unique(y_true))
            if n_classes == 2:
                # Binary classification
                if y_pred_proba.ndim == 2:
                    proba = y_pred_proba[:, 1]
                else:
                    proba = y_pred_proba
                return float(roc_auc_score(y_true, proba))
            else:
                # Multiclass
                return float(roc_auc_score(
                    y_true, y_pred_proba, multi_class="ovr", average="weighted"
                ))
        except Exception:
            return None

    elif key == "confusion_matrix":
        cm = confusion_matrix(y_true, y_pred)
        return cm.tolist()

    elif key == "classification_report":
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        return report

    elif key == "log_loss":
        if y_pred_proba is None:
            return None
        try:
            return float(log_loss(y_true, y_pred_proba))
        except Exception:
            return None

    # Regression metrics
    elif key == "mse":
        return float(mean_squared_error(y_true, y_pred))

    elif key == "rmse":
        return float(np.sqrt(mean_squared_error(y_true, y_pred)))

    elif key == "mae":
        return float(mean_absolute_error(y_true, y_pred))

    elif key == "r2_score":
        return float(r2_score(y_true, y_pred))

    elif key == "mape":
        # Avoid division by zero
        mask = y_true != 0
        if not np.any(mask):
            return None
        return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)

    # Clustering metrics
    elif key == "silhouette_score":
        if X is None:
            return None
        n_labels = len(np.unique(y_pred))
        if n_labels < 2:
            return None
        try:
            return float(silhouette_score(X, y_pred))
        except Exception:
            return None

    elif key == "davies_bouldin_index":
        if X is None:
            return None
        n_labels = len(np.unique(y_pred))
        if n_labels < 2:
            return None
        try:
            return float(davies_bouldin_score(X, y_pred))
        except Exception:
            return None

    elif key == "calinski_harabasz_index":
        if X is None:
            return None
        n_labels = len(np.unique(y_pred))
        if n_labels < 2:
            return None
        try:
            return float(calinski_harabasz_score(X, y_pred))
        except Exception:
            return None

    elif key == "inertia":
        # Inertia is typically passed from the model directly
        return kwargs.get("inertia")

    else:
        raise ValueError(f"Metric '{key}' computation not implemented")


def compute_metrics(
    metric_keys: List[str],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    X: Optional[np.ndarray] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Compute multiple metrics.

    Args:
        metric_keys: List of metric keys to compute
        y_true: True labels/values
        y_pred: Predicted labels/values
        y_pred_proba: Prediction probabilities (classification)
        X: Feature matrix (for clustering metrics)
        **kwargs: Additional metric-specific arguments

    Returns:
        Dictionary of metric key -> value
    """
    results = {}
    for key in metric_keys:
        try:
            value = compute_metric(
                key,
                y_true,
                y_pred,
                y_pred_proba=y_pred_proba,
                X=X,
                **kwargs
            )
            results[key] = value
        except Exception as e:
            results[key] = None
            # Optionally log the error
            print(f"Error computing metric '{key}': {e}")

    return results


def _get_average(y_true: np.ndarray) -> str:
    """Determine averaging strategy based on number of classes."""
    n_classes = len(np.unique(y_true))
    return "binary" if n_classes == 2 else "weighted"
