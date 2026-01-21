"""
Base classes for the plugin system.

Defines the abstract interfaces that all model plugins must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np


class ProblemType(str, Enum):
    """Supported ML problem types."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"


class ModelCategory(str, Enum):
    """Model algorithm categories."""
    TREE = "tree"
    ENSEMBLE = "ensemble"
    LINEAR = "linear"
    NEURAL = "neural"
    DISTANCE = "distance"
    CLUSTERING = "clustering"


class FieldType(str, Enum):
    """Hyperparameter field types for UI rendering."""
    INT = "int"
    FLOAT = "float"
    SELECT = "select"
    BOOL = "bool"
    RANGE = "range"


@dataclass
class HyperparameterField:
    """
    Definition of a single hyperparameter field.

    This schema is sent to the frontend to dynamically render
    the appropriate input control for each hyperparameter.
    """
    key: str
    name: str
    type: FieldType
    default: Any
    description: str = ""

    # Numeric constraints
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None

    # For nullable fields (e.g., max_depth=None means unlimited)
    nullable: bool = False
    null_label: str = "Auto"

    # For select fields
    options: Optional[List[Dict[str, Any]]] = None  # [{value: str, label: str}]

    # Validation
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        result = {
            "key": self.key,
            "name": self.name,
            "type": self.type.value,
            "default": self.default,
            "description": self.description,
            "required": self.required,
        }

        if self.min is not None:
            result["min"] = self.min
        if self.max is not None:
            result["max"] = self.max
        if self.step is not None:
            result["step"] = self.step
        if self.nullable:
            result["nullable"] = self.nullable
            result["nullLabel"] = self.null_label
        if self.options:
            result["options"] = self.options

        return result


@dataclass
class HyperparameterSchema:
    """
    Complete hyperparameter schema for a model plugin.

    Separates parameters into main (always visible) and
    advanced (collapsible) sections for better UX.
    """
    main: List[HyperparameterField] = field(default_factory=list)
    advanced: List[HyperparameterField] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "main": [f.to_dict() for f in self.main],
            "advanced": [f.to_dict() for f in self.advanced],
        }

    def get_defaults(self) -> Dict[str, Any]:
        """Get default values for all hyperparameters."""
        defaults = {}
        for field in self.main + self.advanced:
            defaults[field.key] = field.default
        return defaults


@dataclass
class ModelCapabilities:
    """
    Capabilities declared by a model plugin.

    This object flows downstream from Model node to Evaluate/Visualize
    nodes to determine what metrics and plots are available.
    """
    supported_metrics: List[str]
    default_metrics: List[str]
    supported_plots: List[str]
    default_plots: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "supportedMetrics": self.supported_metrics,
            "defaultMetrics": self.default_metrics,
            "supportedPlots": self.supported_plots,
            "defaultPlots": self.default_plots,
        }


class BaseModelPlugin(ABC):
    """
    Abstract base class for model plugins.

    Each ML algorithm should have a plugin that extends this class.
    The plugin defines metadata, hyperparameters, training logic,
    and declares which evaluation metrics and visualizations it supports.

    Example:
        class RandomForestPlugin(BaseModelPlugin):
            slug = "random_forest"
            name = "Random Forest"
            ...
    """

    # Metadata - must be defined by subclass
    slug: str  # Unique identifier (e.g., "random_forest")
    name: str  # Display name (e.g., "Random Forest")
    description: str  # Short description
    icon: str  # Emoji or icon identifier
    problem_types: List[ProblemType]  # Supported problem types
    category: ModelCategory  # Algorithm category

    # Optional metadata
    best_for: str = ""  # What this algorithm is best for

    @classmethod
    @abstractmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        """
        Return the hyperparameter schema for this model.

        The schema defines all configurable parameters, their types,
        defaults, and constraints. This is used by the frontend to
        render the appropriate input controls.
        """
        pass

    @classmethod
    def get_default_hyperparameters(cls) -> Dict[str, Any]:
        """Return default values for all hyperparameters."""
        return cls.get_hyperparameters().get_defaults()

    @classmethod
    @abstractmethod
    def get_supported_metrics(cls, problem_type: ProblemType) -> List[str]:
        """
        Return list of supported metric keys for the given problem type.

        These keys must match entries in the shared evaluators library.
        """
        pass

    @classmethod
    @abstractmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        """Return default metrics to select for the given problem type."""
        pass

    @classmethod
    @abstractmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        """
        Return list of supported plot keys for the given problem type.

        These keys must match entries in the shared visualizers library.
        """
        pass

    @classmethod
    @abstractmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        """Return default plots to select for the given problem type."""
        pass

    @classmethod
    def get_capabilities(cls, problem_type: ProblemType) -> ModelCapabilities:
        """
        Get the full capabilities object for downstream nodes.

        This is what flows from Model node to Evaluate/Visualize nodes.
        """
        return ModelCapabilities(
            supported_metrics=cls.get_supported_metrics(problem_type),
            default_metrics=cls.get_default_metrics(problem_type),
            supported_plots=cls.get_supported_plots(problem_type),
            default_plots=cls.get_default_plots(problem_type),
        )

    @classmethod
    @abstractmethod
    def train(
        cls,
        X_train: np.ndarray,
        y_train: np.ndarray,
        hyperparameters: Dict[str, Any],
        problem_type: ProblemType,
    ) -> Any:
        """
        Train the model and return the trained model object.

        Args:
            X_train: Training features
            y_train: Training labels/targets
            hyperparameters: User-configured hyperparameters
            problem_type: The problem type being solved

        Returns:
            Trained model object (sklearn-compatible)
        """
        pass

    @classmethod
    def predict(cls, model: Any, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with a trained model.

        Default implementation assumes sklearn-compatible model.
        Override if custom prediction logic is needed.
        """
        return model.predict(X)

    @classmethod
    def predict_proba(cls, model: Any, X: np.ndarray) -> Optional[np.ndarray]:
        """
        Get prediction probabilities (classification only).

        Returns None if not supported by the model.
        """
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)
        return None

    @classmethod
    def get_feature_importance(cls, model: Any) -> Optional[np.ndarray]:
        """
        Get feature importance scores if available.

        Returns None if not supported by the model.
        """
        if hasattr(model, "feature_importances_"):
            return model.feature_importances_
        if hasattr(model, "coef_"):
            return np.abs(model.coef_).flatten()
        return None

    @classmethod
    def to_dict(cls, include_hyperparameters: bool = False) -> Dict[str, Any]:
        """
        Convert plugin metadata to dictionary for API response.

        Args:
            include_hyperparameters: Whether to include full hyperparameter schema
        """
        result = {
            "slug": cls.slug,
            "name": cls.name,
            "description": cls.description,
            "icon": cls.icon,
            "problemTypes": [pt.value for pt in cls.problem_types],
            "category": cls.category.value,
        }

        if cls.best_for:
            result["bestFor"] = cls.best_for

        if include_hyperparameters:
            result["hyperparameters"] = cls.get_hyperparameters().to_dict()

        return result

    @classmethod
    def to_detail_dict(cls, problem_type: Optional[ProblemType] = None) -> Dict[str, Any]:
        """
        Convert plugin to detailed dictionary including capabilities.

        Args:
            problem_type: If provided, includes capabilities for this problem type
        """
        result = cls.to_dict(include_hyperparameters=True)

        if problem_type:
            capabilities = cls.get_capabilities(problem_type)
            result["capabilities"] = capabilities.to_dict()
        else:
            # Include capabilities for first supported problem type
            if cls.problem_types:
                capabilities = cls.get_capabilities(cls.problem_types[0])
                result["capabilities"] = capabilities.to_dict()

        return result
