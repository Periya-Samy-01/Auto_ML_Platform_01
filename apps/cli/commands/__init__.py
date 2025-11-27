# cli/commands/__init__.py
"""
CLI commands package.
Contains command implementations for training and preprocessing.
"""

from .train import train_command
from .preprocess import preprocess_command

__all__ = [
    "train_command",
    "preprocess_command",
]
