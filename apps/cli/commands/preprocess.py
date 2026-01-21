# cli/commands/preprocess.py
"""
Preprocess command implementation for CLI.
Orchestrates data loading, preprocessing, and output handling.
"""

from typing import Optional, Dict, Any
import json
from pathlib import Path

from apps.api.app.ml.preprocessors.base import DataContainer
from apps.cli.utils.preprocessor_factory import get_preprocessor, get_preprocessor_info


def preprocess_command(
    method: str,
    dataset: str,
    output: str,
    target: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
) -> None:
    """
    Execute the preprocessing workflow for a given method and dataset.
    
    Args:
        method: Preprocessor name (e.g., "missing_value_imputation", "impute")
        dataset: Path to input CSV dataset
        output: Path for output CSV (without extension)
        target: Target column name (optional, preserved but not modified)
        params: Preprocessor configuration parameters
        
    Raises:
        Various errors from data loading, preprocessing, or saving
    """
    try:
        # Step 1: Load data into DataContainer
        print(f"\n📦 Loading data from {dataset}...")
        data = DataContainer.from_csv(
            path=dataset,
            target_col=target,
            load_metadata=True
        )
        print(f"✓ Data loaded: {data.n_samples} samples, {data.n_features} features")
        if target:
            print(f"✓ Target column: {target}")
        
        # Step 2: Get preprocessor
        print(f"\n🔧 Initializing preprocessor: {method}...")
        preprocessor = get_preprocessor(method, params)
        print(f"✓ Preprocessor: {preprocessor.__class__.__name__}")
        if params:
            print(f"✓ Parameters: {json.dumps(params, indent=2)}")
        
        # Step 3: Fit preprocessor
        print(f"\n📊 Fitting preprocessor on data...")
        preprocessor.fit(data)
        print(f"✓ Preprocessor fitted")
        
        # Show fit metadata
        fit_metadata = preprocessor.get_fit_metadata()
        if fit_metadata:
            _print_fit_summary(method, fit_metadata)
        
        # Step 4: Transform data
        print(f"\n⚙️ Transforming data...")
        result = preprocessor.transform(data)
        print(f"✓ Transformation complete")
        
        # Show transform metadata
        transform_metadata = preprocessor.get_transform_metadata()
        if transform_metadata:
            _print_transform_summary(method, transform_metadata)
        
        # Step 5: Save output
        print(f"\n💾 Saving results...")
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        csv_path = result.to_csv(
            path=str(output_path),
            include_target=target is not None,
            save_metadata=True
        )
        print(f"✓ Data saved to: {csv_path}")
        print(f"✓ Metadata saved to: {output_path.with_suffix('.meta.json')}")
        
        # Step 6: Print summary
        print("\n" + "=" * 50)
        print("PREPROCESSING RESULTS")
        print("=" * 50)
        print(f"Preprocessor: {method}")
        print(f"Input: {dataset}")
        print(f"Output: {csv_path}")
        print("-" * 50)
        print(f"Rows: {data.n_samples} → {result.n_samples}")
        print(f"Columns: {data.n_features} → {result.n_features}")
        print("-" * 50)
        
        # Show key changes
        if transform_metadata:
            _print_key_changes(method, transform_metadata)
        
        print("=" * 50 + "\n")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        raise
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise


def _print_fit_summary(method: str, metadata: Dict[str, Any]) -> None:
    """Print summary of fit operation."""
    if method in ("missing_value_imputation", "missing", "impute", "fillna"):
        if "imputation_values" in metadata:
            values = metadata["imputation_values"]
            if values:
                print(f"  Imputation values learned for {len(values)} columns")
    
    elif method in ("outlier_handling", "outliers", "outlier"):
        if "boundaries" in metadata:
            boundaries = metadata["boundaries"]
            print(f"  Outlier boundaries calculated for {len(boundaries)} columns")
    
    elif method in ("feature_scaling", "scale", "scaling", "normalize"):
        if "scaling_params" in metadata:
            params = metadata["scaling_params"]
            print(f"  Scaling parameters learned for {len(params)} columns")
    
    elif method in ("one_hot_encoding", "onehot", "one_hot", "dummies"):
        if "categories" in metadata:
            categories = metadata["categories"]
            total_cats = sum(len(cats) for cats in categories.values())
            print(f"  {total_cats} categories found across {len(categories)} columns")
    
    elif method in ("ordinal_label_encoding", "label", "ordinal", "label_encoding"):
        if "encoding_maps" in metadata:
            maps = metadata["encoding_maps"]
            print(f"  Encoding mappings created for {len(maps)} columns")


def _print_transform_summary(method: str, metadata: Dict[str, Any]) -> None:
    """Print summary of transform operation."""
    pass  # Summary is printed in _print_key_changes


def _print_key_changes(method: str, metadata: Dict[str, Any]) -> None:
    """Print key changes from transformation."""
    
    # Duplicate removal
    if "duplicates_removed" in metadata:
        removed = metadata["duplicates_removed"]
        if removed > 0:
            print(f"Duplicates removed: {removed}")
        else:
            print("No duplicates found")
    
    # Missing value imputation
    if "values_imputed" in metadata:
        imputed = metadata["values_imputed"]
        if imputed:
            total = sum(v["count"] for v in imputed.values())
            print(f"Values imputed: {total} across {len(imputed)} columns")
        if metadata.get("rows_dropped", 0) > 0:
            print(f"Rows dropped: {metadata['rows_dropped']}")
        if metadata.get("cols_dropped", 0) > 0:
            print(f"Columns dropped: {metadata['cols_dropped']}")
    
    # Outlier handling
    if "total_outliers_detected" in metadata:
        total = metadata["total_outliers_detected"]
        action = metadata.get("action", "unknown")
        print(f"Outliers detected: {total}")
        print(f"Action taken: {action}")
        if metadata.get("rows_removed", 0) > 0:
            print(f"Rows removed: {metadata['rows_removed']}")
    
    # Feature scaling
    if "columns_scaled" in metadata:
        cols = metadata["columns_scaled"]
        print(f"Columns scaled: {len(cols)}")
    
    # One-hot encoding
    if "new_columns_created" in metadata and "columns_encoded" in metadata:
        encoded = metadata.get("columns_encoded", [])
        created = metadata.get("new_columns_created", [])
        print(f"Columns encoded: {len(encoded)}")
        print(f"New columns created: {len(created)}")
    
    # Label/ordinal encoding
    if "encoding_maps_applied" in metadata:
        maps = metadata["encoding_maps_applied"]
        print(f"Columns encoded: {len(maps)}")
    
    # Datetime extraction
    if "features_extracted" in metadata:
        features = metadata.get("features_extracted", [])
        created = metadata.get("new_columns_created", [])
        dropped = metadata.get("columns_dropped", [])
        print(f"Features extracted: {features}")
        print(f"New columns: {len(created)}")
        if dropped:
            print(f"Original columns dropped: {len(dropped)}")
    
    # Data type conversion
    if "successful_conversions" in metadata:
        success = metadata.get("successful_conversions", [])
        failed = metadata.get("failed_conversions", [])
        print(f"Conversions successful: {len(success)}")
        if failed:
            print(f"Conversions failed: {len(failed)}")
