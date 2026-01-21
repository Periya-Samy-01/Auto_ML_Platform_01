# cli/utils/output_handler.py
"""
Output handling utilities for CLI.
Saves trained models, results, and creates visualizations.
Supports supervised (classification, regression) and unsupervised (clustering, dimensionality_reduction) tasks.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

from apps.api.app.ml.trainers.base import BaseTrainer
from apps.api.app.ml.constants import (
    TASK_CLASSIFICATION, 
    TASK_REGRESSION,
    TASK_CLUSTERING,
    TASK_DIMENSIONALITY_REDUCTION
)


def create_output_directory(algorithm: str, task: str) -> Path:
    """
    Create timestamped output directory for results.
    
    Args:
        algorithm: Algorithm name
        task: Task type
        
    Returns:
        Path object to output directory
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_name = f"{timestamp}_{algorithm}_{task}"
    
    output_dir = Path("outputs") / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def save_model(trainer: BaseTrainer, output_dir: Path) -> None:
    """
    Save trained model to output directory.
    
    Args:
        trainer: Trained trainer instance
        output_dir: Path to output directory
    """
    trainer.save(str(output_dir))


def save_results_json(
    results: Dict[str, Any],
    algorithm: str,
    task: str,
    metrics: Dict[str, Any],
    output_dir: Path
) -> None:
    """
    Save results and metrics to JSON file.
    
    Args:
        results: Additional result metadata
        algorithm: Algorithm name
        task: Task type
        metrics: Evaluation metrics dictionary
        output_dir: Path to output directory
    """
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "algorithm": algorithm,
        "task": task,
        "metrics": metrics,
        **results
    }
    
    results_path = output_dir / "results.json"
    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)


def save_confusion_matrix_plot(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_dir: Path
) -> None:
    """
    Create and save confusion matrix visualization (classification only).
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        output_dir: Path to output directory
    """
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    plot_path = output_dir / "confusion_matrix.png"
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()


def save_predictions_plot(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_dir: Path
) -> None:
    """
    Create and save predictions vs actual plot (regression only).
    
    Args:
        y_true: True values
        y_pred: Predicted values
        output_dir: Path to output directory
    """
    plt.figure(figsize=(10, 6))
    
    # Scatter plot
    plt.scatter(y_true, y_pred, alpha=0.6, edgecolors='k')
    
    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    plt.xlabel('True Values')
    plt.ylabel('Predicted Values')
    plt.title('Actual vs Predicted Values')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_path = output_dir / "predictions_plot.png"
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()


def save_clusters_plot(
    X: np.ndarray,
    y_pred: np.ndarray,
    output_dir: Path
) -> None:
    """
    Create and save clustering visualization (clustering only).
    
    For 2D data: scatter plot with cluster colors
    For >2D data: PCA projection to 2D then scatter plot
    
    Args:
        X: Feature matrix
        y_pred: Cluster IDs
        output_dir: Path to output directory
    """
    if X.shape[1] > 2:
        # Project to 2D using PCA
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=42)
        X_2d = pca.fit_transform(X)
        xlabel = f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)"
        ylabel = f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)"
    else:
        X_2d = X
        xlabel = f"Feature 1"
        ylabel = f"Feature 2"
    
    plt.figure(figsize=(10, 8))
    
    # Plot each cluster with different color
    unique_clusters = np.unique(y_pred)
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_clusters)))
    
    for cluster_id, color in zip(unique_clusters, colors):
        mask = y_pred == cluster_id
        plt.scatter(
            X_2d[mask, 0], 
            X_2d[mask, 1],
            c=[color],
            label=f'Cluster {cluster_id}',
            s=50,
            alpha=0.7,
            edgecolors='black',
            linewidth=0.5
        )
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'Clustering Results ({len(unique_clusters)} clusters)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_path = output_dir / "clusters_plot.png"
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()


def save_pca_plot(
    X_transformed: np.ndarray,
    trainer,
    output_dir: Path
) -> None:
    """
    Create and save PCA visualization.
    
    Shows explained variance ratio per component.
    
    Args:
        X_transformed: Transformed feature matrix
        trainer: Trained PCA trainer (for explained_variance_ratio_)
        output_dir: Path to output directory
    """
    if hasattr(trainer.model, 'explained_variance_ratio_'):
        variance_ratio = trainer.model.explained_variance_ratio_
        cumsum_variance = np.cumsum(variance_ratio)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Variance per component
        axes[0].bar(range(1, len(variance_ratio) + 1), variance_ratio, alpha=0.7, color='blue')
        axes[0].set_xlabel('Principal Component')
        axes[0].set_ylabel('Explained Variance Ratio')
        axes[0].set_title('Variance Explained by Each Component')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Cumulative variance
        axes[1].plot(range(1, len(cumsum_variance) + 1), cumsum_variance, 'bo-', linewidth=2)
        axes[1].axhline(y=0.95, color='r', linestyle='--', label='95% threshold')
        axes[1].set_xlabel('Number of Components')
        axes[1].set_ylabel('Cumulative Explained Variance')
        axes[1].set_title('Cumulative Variance Explained')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = output_dir / "pca_variance.png"
        plt.savefig(plot_path, dpi=100, bbox_inches='tight')
        plt.close()


def save_all_outputs(
    trainer: BaseTrainer,
    y_test: Optional[np.ndarray],
    y_pred: np.ndarray,
    metrics: Dict[str, Any],
    algorithm: str,
    task: str,
    y_pred_proba: Optional[np.ndarray] = None,
    X: Optional[np.ndarray] = None,
    X_test: Optional[np.ndarray] = None
) -> Path:
    """
    Orchestrate saving model, results, and visualizations.
    
    Supports supervised (classification, regression) and unsupervised (clustering, 
    dimensionality_reduction) tasks.
    
    Args:
        trainer: Trained trainer instance
        y_test: True test labels/values (None for unsupervised)
        y_pred: Predicted labels/values/transformed features
        metrics: Evaluation metrics dictionary
        algorithm: Algorithm name
        task: Task type
        y_pred_proba: Predicted probabilities (optional, for classification)
        X: Full feature matrix (required for clustering visualization)
        X_test: Test feature matrix (optional)
        
    Returns:
        Path to output directory
    """
    # Create output directory
    output_dir = create_output_directory(algorithm, task)
    
    # Save model
    save_model(trainer, output_dir)
    
    # Save results
    if task in {TASK_CLUSTERING, TASK_DIMENSIONALITY_REDUCTION}:
        # For unsupervised, don't save test_samples
        save_results_json(
            results={"training_samples": X.shape[0] if X is not None else 0},
            algorithm=algorithm,
            task=task,
            metrics=metrics,
            output_dir=output_dir
        )
    else:
        # For supervised
        save_results_json(
            results={"test_samples": len(y_test) if y_test is not None else 0},
            algorithm=algorithm,
            task=task,
            metrics=metrics,
            output_dir=output_dir
        )
    
    # Save visualization based on task
    if task == TASK_CLASSIFICATION:
        if y_test is not None:
            save_confusion_matrix_plot(y_test, y_pred, output_dir)
    
    elif task == TASK_REGRESSION:
        if y_test is not None:
            save_predictions_plot(y_test, y_pred, output_dir)
    
    elif task == TASK_CLUSTERING:
        if X is not None:
            save_clusters_plot(X, y_pred, output_dir)
    
    elif task == TASK_DIMENSIONALITY_REDUCTION:
        save_pca_plot(y_pred, trainer, output_dir)
    
    return output_dir
