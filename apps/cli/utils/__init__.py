# cli/utils/__init__.py
"""
CLI utilities package.
Contains factories and helpers for trainers and preprocessors.
"""

from .trainer_factory import get_trainer, list_available_algorithms
from .preprocessor_factory import get_preprocessor, list_available_preprocessors
from .data_loader import load_and_split_data
from .output_handler import save_all_outputs

__all__ = [
    # Trainer utilities
    "get_trainer",
    "list_available_algorithms",
    # Preprocessor utilities
    "get_preprocessor",
    "list_available_preprocessors",
    # Data utilities
    "load_and_split_data",
    "save_all_outputs",
]
