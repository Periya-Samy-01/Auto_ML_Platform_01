#apps/workers/worker/ml/evaluators/regression_evaluator.py
"""
Regression metrics evaluator.
Computes MSE, RMSE, MAE, and R² score.
"""

from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)
from .base import BaseEvaluator


class RegressionEvaluator(BaseEvaluator):
    """
    Evaluator for regression tasks.
    
    Computes:
    - MSE (Mean Squared Error)
    - RMSE (Root Mean Squared Error)
    - MAE (Mean Absolute Error)
    - R² Score (Coefficient of Determination)
    """
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Compute regression metrics.
        
        Args:
            y_true: True target values
            y_pred: Predicted target values
            
        Returns:
            Dictionary with metrics:
            - mse: Mean Squared Error
            - rmse: Root Mean Squared Error
            - mae: Mean Absolute Error
            - r2_score: R² score
        """
        metrics = {}
        
        # Mean Squared Error
        mse = mean_squared_error(y_true, y_pred)
        metrics["mse"] = float(mse)
        
        # Root Mean Squared Error
        metrics["rmse"] = float(np.sqrt(mse))
        
        # Mean Absolute Error
        metrics["mae"] = float(mean_absolute_error(y_true, y_pred))
        
        # R² Score
        metrics["r2_score"] = float(r2_score(y_true, y_pred))
        
        return metrics