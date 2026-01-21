#apps/workers/worker/ml/evaluators/classification_evaluator.py
"""
Classification metrics evaluator.
Computes accuracy, precision, recall, F1, and confusion matrix.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)
from .base import BaseEvaluator


class ClassificationEvaluator(BaseEvaluator):
    """
    Evaluator for classification tasks.
    
    Computes:
    - Accuracy
    - Precision (weighted average for multiclass)
    - Recall (weighted average for multiclass)
    - F1 Score (weighted average for multiclass)
    - Confusion Matrix
    - ROC-AUC (if probabilities provided)
    """
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray, 
                 y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Compute classification metrics.
        
        Args:
            y_true: True class labels
            y_pred: Predicted class labels
            y_pred_proba: Predicted class probabilities (optional, for ROC-AUC)
            
        Returns:
            Dictionary with metrics:
            - accuracy: Overall accuracy
            - precision: Weighted precision
            - recall: Weighted recall
            - f1_score: Weighted F1 score
            - confusion_matrix: Confusion matrix as 2D array
            - roc_auc: ROC-AUC score (if probabilities provided and binary classification)
        """
        metrics = {}
        
        # Basic metrics
        metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
        
        # Handle binary vs multiclass
        # For binary, use 'binary', for multiclass use 'weighted'
        unique_classes = len(np.unique(y_true))
        average = 'binary' if unique_classes == 2 else 'weighted'
        
        metrics["precision"] = float(precision_score(y_true, y_pred, average=average, zero_division=0))
        metrics["recall"] = float(recall_score(y_true, y_pred, average=average, zero_division=0))
        metrics["f1_score"] = float(f1_score(y_true, y_pred, average=average, zero_division=0))
        
        # Confusion matrix (convert to list for JSON serialization)
        metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
        
        # ROC-AUC (only for binary classification with probabilities)
        if y_pred_proba is not None and unique_classes == 2:
            try:
                # For binary classification, use probabilities of positive class
                if y_pred_proba.ndim == 2:
                    # Probabilities shape: (n_samples, 2) -> use positive class (index 1)
                    proba_positive = y_pred_proba[:, 1]
                else:
                    # Probabilities shape: (n_samples,) -> already positive class
                    proba_positive = y_pred_proba
                
                metrics["roc_auc"] = float(roc_auc_score(y_true, proba_positive))
            except Exception:
                # Skip ROC-AUC if calculation fails
                metrics["roc_auc"] = None
        else:
            metrics["roc_auc"] = None
        
        return metrics