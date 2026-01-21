#apps/workers/worker/ml/trainers/base.py
"""
Base trainer class for all ML models.
All trainers must inherit from BaseTrainer and implement abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import joblib
import json
import numpy as np


class BaseTrainer(ABC):
    """
    Abstract base class for all ML trainers.
    
    Attributes:
        name (str): Model name
        task (str): Task type - "classification", "regression", "clustering", "dimensionality_reduction"
        hyperparameters (Dict[str, Any]): Mutable hyperparameters
        model (Optional[Any]): The trained sklearn/xgboost model
        _metadata (Dict): Training metadata (created_at, last_trained_at, training_samples, feature_count, model_version)
    """
    
    def __init__(self, name: str, task: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize the trainer.
        
        Args:
            name: Model name
            task: Task type
            hyperparameters: Initial hyperparameters (default: {})
        """
        self.name = name
        self.task = task
        self.hyperparameters = hyperparameters or {}
        self.model: Optional[Any] = None
        self._metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "last_trained_at": None,
            "training_samples": 0,
            "feature_count": 0,
            "model_version": None
        }
        
        # Validate hyperparameters on initialization
        self._validate_hyperparameters()
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> 'BaseTrainer':
        """
        Train the model.
        
        Args:
            X: Training features
            y: Training targets (None for unsupervised tasks)
            
        Returns:
            self: For method chaining
        """
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features to predict on
            
        Returns:
            Predictions (class labels, regression values, cluster IDs, or transformed features)
        """
        pass
    
    @abstractmethod
    def _validate_hyperparameters(self) -> None:
        """
        Validate algorithm-specific hyperparameter constraints.
        
        Raises:
            ValueError: If hyperparameters are invalid
        """
        pass
    
    @abstractmethod
    def get_model_type(self) -> str:
        """
        Return model family: 'linear', 'tree', 'neural', 'distance', 'clustering', 'dimensionality'.
        
        Returns:
            Model type constant from worker.constants
        """
        pass
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities (classification only).
        
        Args:
            X: Features to predict on
            
        Returns:
            Class probabilities
            
        Raises:
            NotImplementedError: If classifier doesn't support probabilities
        """
        raise NotImplementedError("Only classifiers that support probabilities implement this.")
    
    def suggest_optuna_params(self, trial) -> Dict[str, Any]:
        """
        Define hyperparameter search space for Optuna (optional - pro feature).
        
        Args:
            trial: Optuna trial object
            
        Returns:
            Dictionary of suggested hyperparameters
            
        Raises:
            NotImplementedError: If not implemented for this trainer
        """
        raise NotImplementedError("Optuna hyperparameter optimization not implemented for this trainer.")
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """
        Get feature importances for tree/linear models (optional).
        
        Returns:
            Feature importance array or None
            
        Raises:
            NotImplementedError: If not implemented for this trainer
        """
        raise NotImplementedError("Feature importance not available for this model type.")
    
    def update_hyperparameters(self, new_params: Dict[str, Any]) -> None:
        """
        Update hyperparameters (requires refit to apply changes).
        
        Args:
            new_params: New hyperparameter values
            
        Raises:
            ValueError: If new hyperparameters are invalid
        """
        # Merge new params with existing
        self.hyperparameters.update(new_params)
        
        # Validate merged hyperparameters
        self._validate_hyperparameters()
    
    def save(self, path: str) -> None:
        """
        Save model to disk using joblib + metadata.json.
        
        Args:
            path: Directory path to save model (creates if doesn't exist)
        """
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save model with joblib
        model_path = save_path / "model.joblib"
        joblib.dump(self.model, model_path)
        
        # Save metadata as JSON
        metadata_path = save_path / "metadata.json"
        metadata = {
            "name": self.name,
            "task": self.task,
            "hyperparameters": self.hyperparameters,
            "metadata": self._metadata
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'BaseTrainer':
        """
        Load model from disk.
        
        Args:
            path: Directory path containing model.joblib and metadata.json
            
        Returns:
            Loaded trainer instance
            
        Raises:
            ValueError: If loaded task doesn't match trainer's expected task
            FileNotFoundError: If model files don't exist
        """
        load_path = Path(path)
        
        # Load metadata
        metadata_path = load_path / "metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Create instance with loaded hyperparameters
        instance = cls(
            name=metadata["name"],
            task=metadata["task"],
            hyperparameters=metadata["hyperparameters"]
        )
        
        # Load model
        model_path = load_path / "model.joblib"
        instance.model = joblib.load(model_path)
        
        # Restore metadata
        instance._metadata = metadata["metadata"]
        
        return instance
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get training metadata for debugging/logging.
        
        Returns:
            Dictionary with created_at, last_trained_at, training_samples, feature_count, model_version
        """
        return self._metadata.copy()
    
    def _update_metadata(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> None:
        """
        Update metadata after training.
        
        Args:
            X: Training features
            y: Training targets (optional)
        """
        self._metadata["last_trained_at"] = datetime.now().isoformat()
        self._metadata["training_samples"] = X.shape[0]
        self._metadata["feature_count"] = X.shape[1]
        
        # Store model version if available
        if hasattr(self.model, '__version__'):
            self._metadata["model_version"] = self.model.__version__
        elif hasattr(self.model, 'get_params'):
            # For sklearn models, try to get version from module
            model_class = self.model.__class__
            if hasattr(model_class.__module__, '__version__'):
                self._metadata["model_version"] = model_class.__module__.__version__