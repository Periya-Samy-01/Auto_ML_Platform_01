# cli/utils/data_loader.py
"""
Data loading and preprocessing utilities for CLI.
Handles CSV loading, target extraction, and train/test splitting.
Supports both supervised (with target) and unsupervised (no target) tasks.
"""

from typing import Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def load_and_split_data(
    csv_path: str,
    target_col: Optional[str] = None,
    test_size: float = 0.2,
    random_state: int = 42,
    use_full_dataset: bool = False
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Load CSV file and prepare data for training.
    
    Supports:
    - Supervised learning: With target column, split or full dataset
    - Unsupervised learning: Without target column, split or full dataset
    
    Args:
        csv_path: Path to CSV file
        target_col: Name of target column (required for supervised, None for unsupervised)
        test_size: Fraction for test set (default 0.2 for 80/20 split), ignored if use_full_dataset=True
        random_state: Random seed for reproducibility
        use_full_dataset: If True, return full dataset without splitting (for unsupervised or HPO)
        
    Returns:
        If use_full_dataset=True:
            Tuple of (X, None, y or None, None)
            - X: Full feature matrix (n_samples, n_features)
            - y: Full target (if target_col provided), None otherwise
        
        If use_full_dataset=False:
            Tuple of (X_train, X_test, y_train or None, y_test or None)
            - X_train, X_test: Split features (80/20 by default)
            - y_train, y_test: Split targets (if target_col provided), None otherwise
            
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If target column not found in CSV or if features cannot be converted to numeric
        
    Examples:
        # Supervised classification with split
        X_train, X_test, y_train, y_test = load_and_split_data(
            'data.csv', target_col='target', use_full_dataset=False
        )
        
        # Unsupervised clustering with full dataset
        X, _, _, _ = load_and_split_data(
            'data.csv', target_col=None, use_full_dataset=True
        )
        
        # Supervised regression with full dataset (for HPO)
        X, _, y, _ = load_and_split_data(
            'data.csv', target_col='price', use_full_dataset=True
        )
    """
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")
    
    # Extract features and target
    X, y = _extract_features_and_target(df, target_col)
    
    # Convert features to numeric
    X = _convert_features_to_numeric(X)
    
    # Convert target to numeric if provided
    if y is not None:
        y = _convert_target_to_numeric(y)
    
    # Return based on mode
    if use_full_dataset:
        # Return full dataset without splitting
        return X, None, y, None
    else:
        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state
        )
        return X_train, X_test, y_train, y_test


def _extract_features_and_target(
    df: pd.DataFrame,
    target_col: Optional[str]
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Extract features and target from dataframe.
    
    Args:
        df: Pandas DataFrame
        target_col: Target column name (None for unsupervised)
        
    Returns:
        Tuple of (X, y) where y is None if target_col is None
        
    Raises:
        ValueError: If target column not found
    """
    # Check target column exists if provided
    if target_col is not None:
        if target_col not in df.columns:
            available_cols = ", ".join(df.columns.tolist())
            raise ValueError(
                f"Target column '{target_col}' not found in CSV.\n"
                f"Available columns: {available_cols}"
            )
        
        # Extract target
        y = df[target_col].values
        
        # Extract features (all columns except target)
        X = df.drop(columns=[target_col]).values
    else:
        # No target - use all columns as features (unsupervised)
        X = df.values
        y = None
    
    return X, y


def _convert_features_to_numeric(X: np.ndarray) -> np.ndarray:
    """
    Convert feature matrix to numeric type.
    
    Args:
        X: Feature matrix
        
    Returns:
        Numeric feature matrix
        
    Raises:
        ValueError: If features cannot be converted
    """
    try:
        X = X.astype(np.float64)
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Could not convert features to numeric. "
            f"Ensure all columns are numeric. Error: {str(e)}"
        )
    return X


def _convert_target_to_numeric(y: np.ndarray) -> np.ndarray:
    """
    Convert target to numeric if possible, keep original if not.
    
    Args:
        y: Target array
        
    Returns:
        Numeric or original target array
    """
    try:
        y_numeric = pd.to_numeric(y, errors='coerce')
        if y_numeric.isna().any():
            # If conversion failed for some values, keep as is (might be categorical)
            return y
        else:
            return y_numeric.values
    except:
        # Keep original y if conversion fails (might be string labels)
        return y
