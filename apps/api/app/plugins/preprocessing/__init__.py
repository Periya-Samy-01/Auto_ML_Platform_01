"""
Preprocessing methods registry for the AutoML Playground.

Provides a registry of all available preprocessing operations
that can be used in the workflow preprocessing node.
"""

from app.plugins.preprocessing.registry import (
    PREPROCESSING_METHODS,
    PREPROCESSING_CATEGORIES,
    get_method,
    get_all_methods,
    get_methods_by_category,
    apply_preprocessing,
)

__all__ = [
    "PREPROCESSING_METHODS",
    "PREPROCESSING_CATEGORIES",
    "get_method",
    "get_all_methods",
    "get_methods_by_category",
    "apply_preprocessing",
]
