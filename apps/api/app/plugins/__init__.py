"""
Plugin system for AutoML Playground.

This module provides a plugin-based architecture for ML algorithms,
preprocessing methods, evaluation metrics, and visualizations.
"""

from app.plugins.registry import (
    PluginRegistry,
    get_model_plugin,
    get_all_model_plugins,
    get_model_plugins_by_problem_type,
    get_preprocessing_method,
    get_all_preprocessing_methods,
    get_preprocessing_methods_by_category,
)
from app.plugins.base import BaseModelPlugin, HyperparameterField, HyperparameterSchema

__all__ = [
    # Registry
    "PluginRegistry",
    "get_model_plugin",
    "get_all_model_plugins",
    "get_model_plugins_by_problem_type",
    "get_preprocessing_method",
    "get_all_preprocessing_methods",
    "get_preprocessing_methods_by_category",
    # Base classes
    "BaseModelPlugin",
    "HyperparameterField",
    "HyperparameterSchema",
]
