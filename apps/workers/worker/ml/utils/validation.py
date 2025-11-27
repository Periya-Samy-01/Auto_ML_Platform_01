#apps/workers/worker/ml/utils/validation.py
"""
Validation utilities for hyperparameters and inputs.
Reusable validation functions for trainers.
"""

from typing import Any, List, Optional, Set, Union


def validate_positive_integer(value: Any, param_name: str, allow_none: bool = False) -> None:
    """
    Validate that value is a positive integer.
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        allow_none: Whether None is allowed
        
    Raises:
        ValueError: If validation fails
    """
    if allow_none and value is None:
        return
    
    if not isinstance(value, int):
        raise ValueError(f"{param_name} must be an integer, got {type(value).__name__}")
    
    if value <= 0:
        raise ValueError(f"{param_name} must be positive, got {value}")


def validate_positive_number(value: Any, param_name: str, allow_none: bool = False) -> None:
    """
    Validate that value is a positive number (int or float).
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        allow_none: Whether None is allowed
        
    Raises:
        ValueError: If validation fails
    """
    if allow_none and value is None:
        return
    
    if not isinstance(value, (int, float)):
        raise ValueError(f"{param_name} must be a number, got {type(value).__name__}")
    
    if value <= 0:
        raise ValueError(f"{param_name} must be positive, got {value}")


def validate_range(value: Any, param_name: str, min_val: Optional[float] = None, 
                   max_val: Optional[float] = None, allow_none: bool = False) -> None:
    """
    Validate that value is within a range.
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        allow_none: Whether None is allowed
        
    Raises:
        ValueError: If validation fails
    """
    if allow_none and value is None:
        return
    
    if not isinstance(value, (int, float)):
        raise ValueError(f"{param_name} must be a number, got {type(value).__name__}")
    
    if min_val is not None and value < min_val:
        raise ValueError(f"{param_name} must be >= {min_val}, got {value}")
    
    if max_val is not None and value > max_val:
        raise ValueError(f"{param_name} must be <= {max_val}, got {value}")


def validate_choice(value: Any, param_name: str, choices: Union[List, Set, tuple], 
                    allow_none: bool = False) -> None:
    """
    Validate that value is one of the allowed choices.
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        choices: List/set/tuple of allowed values
        allow_none: Whether None is allowed
        
    Raises:
        ValueError: If validation fails
    """
    if allow_none and value is None:
        return
    
    if value not in choices:
        raise ValueError(f"{param_name} must be one of {choices}, got '{value}'")


def validate_boolean(value: Any, param_name: str) -> None:
    """
    Validate that value is a boolean.
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, bool):
        raise ValueError(f"{param_name} must be a boolean, got {type(value).__name__}")


def validate_type(value: Any, param_name: str, expected_type: type, allow_none: bool = False) -> None:
    """
    Validate that value is of expected type.
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        expected_type: Expected type
        allow_none: Whether None is allowed
        
    Raises:
        ValueError: If validation fails
    """
    if allow_none and value is None:
        return
    
    if not isinstance(value, expected_type):
        raise ValueError(
            f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}"
        )


def validate_probability(value: Any, param_name: str, allow_none: bool = False) -> None:
    """
    Validate that value is a probability (between 0 and 1).
    
    Args:
        value: Value to validate
        param_name: Parameter name for error messages
        allow_none: Whether None is allowed
        
    Raises:
        ValueError: If validation fails
    """
    if allow_none and value is None:
        return
    
    if not isinstance(value, (int, float)):
        raise ValueError(f"{param_name} must be a number, got {type(value).__name__}")
    
    if value < 0 or value > 1:
        raise ValueError(f"{param_name} must be between 0 and 1, got {value}")