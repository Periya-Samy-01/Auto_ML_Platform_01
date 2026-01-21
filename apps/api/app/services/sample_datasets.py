"""
Sample Datasets Service

Provides access to built-in sample/toy datasets for learning and experimentation.
Users can only use these datasets in workflows - they cannot upload, modify, or delete them.

Hybrid loading approach:
- Small sklearn datasets: Loaded at runtime
- Large external datasets: Loaded from CSV files in sample_data folder
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

import pandas as pd

logger = logging.getLogger(__name__)

# Path to CSV sample data folder
SAMPLE_DATA_DIR = Path(__file__).parent.parent / "sample_data"


class DatasetSource(str, Enum):
    """Source type for sample datasets."""
    SKLEARN = "sklearn"
    CSV = "csv"
    GENERATED = "generated"


class ProblemCategory(str, Enum):
    """Problem type category."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    IMAGE = "image"


@dataclass
class ColumnInfo:
    """Column metadata for a sample dataset."""
    name: str
    dtype: str  # "int", "float", "string", "boolean", "datetime"
    missing_percent: float = 0.0


@dataclass
class SampleDatasetMeta:
    """Metadata for a sample dataset."""
    id: str
    name: str
    description: str
    source: DatasetSource
    problem_type: ProblemCategory
    default_target: str
    rows: int
    columns: int
    size_bytes: int
    column_info: List[ColumnInfo] = field(default_factory=list)
    file_name: Optional[str] = None  # For CSV sources
    sklearn_loader: Optional[str] = None  # For sklearn sources
    tags: List[str] = field(default_factory=list)


# =============================================================================
# SAMPLE DATASET CATALOG
# =============================================================================

SAMPLE_CATALOG: Dict[str, SampleDatasetMeta] = {
    # -------------------------------------------------------------------------
    # SKLEARN DATASETS (loaded at runtime)
    # -------------------------------------------------------------------------
    "iris": SampleDatasetMeta(
        id="iris",
        name="Iris",
        description="Classic iris flower classification dataset with 3 species and 4 features.",
        source=DatasetSource.SKLEARN,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="target",
        rows=150,
        columns=5,
        size_bytes=4608,
        sklearn_loader="load_iris",
        column_info=[
            ColumnInfo("sepal length (cm)", "float"),
            ColumnInfo("sepal width (cm)", "float"),
            ColumnInfo("petal length (cm)", "float"),
            ColumnInfo("petal width (cm)", "float"),
            ColumnInfo("target", "int"),
        ],
        tags=["beginner", "classification", "multiclass"],
    ),
    
    "breast_cancer": SampleDatasetMeta(
        id="breast_cancer",
        name="Breast Cancer Wisconsin",
        description="Breast cancer diagnostic dataset with 30 features for binary classification.",
        source=DatasetSource.SKLEARN,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="target",
        rows=569,
        columns=31,
        size_bytes=98000,
        sklearn_loader="load_breast_cancer",
        column_info=[
            ColumnInfo("mean radius", "float"),
            ColumnInfo("mean texture", "float"),
            ColumnInfo("mean perimeter", "float"),
            ColumnInfo("mean area", "float"),
            ColumnInfo("mean smoothness", "float"),
            # ... more features
            ColumnInfo("target", "int"),
        ],
        tags=["healthcare", "binary", "classification"],
    ),
    
    "diabetes": SampleDatasetMeta(
        id="diabetes",
        name="Diabetes Progression",
        description="Diabetes disease progression prediction with 10 baseline variables.",
        source=DatasetSource.SKLEARN,
        problem_type=ProblemCategory.REGRESSION,
        default_target="target",
        rows=442,
        columns=11,
        size_bytes=51200,
        sklearn_loader="load_diabetes",
        column_info=[
            ColumnInfo("age", "float"),
            ColumnInfo("sex", "float"),
            ColumnInfo("bmi", "float"),
            ColumnInfo("bp", "float"),
            ColumnInfo("s1", "float"),
            ColumnInfo("s2", "float"),
            ColumnInfo("s3", "float"),
            ColumnInfo("s4", "float"),
            ColumnInfo("s5", "float"),
            ColumnInfo("s6", "float"),
            ColumnInfo("target", "float"),
        ],
        tags=["healthcare", "regression", "beginner"],
    ),
    
    "california_housing": SampleDatasetMeta(
        id="california_housing",
        name="California Housing",
        description="California housing prices based on census data with 8 features.",
        source=DatasetSource.SKLEARN,
        problem_type=ProblemCategory.REGRESSION,
        default_target="target",
        rows=20640,
        columns=9,
        size_bytes=1500000,
        sklearn_loader="fetch_california_housing",
        column_info=[
            ColumnInfo("MedInc", "float"),
            ColumnInfo("HouseAge", "float"),
            ColumnInfo("AveRooms", "float"),
            ColumnInfo("AveBedrms", "float"),
            ColumnInfo("Population", "float"),
            ColumnInfo("AveOccup", "float"),
            ColumnInfo("Latitude", "float"),
            ColumnInfo("Longitude", "float"),
            ColumnInfo("target", "float"),
        ],
        tags=["regression", "real-estate", "intermediate"],
    ),
    
    "wine": SampleDatasetMeta(
        id="wine",
        name="Wine",
        description="Wine recognition dataset with 13 chemical analysis features for 3 cultivars.",
        source=DatasetSource.SKLEARN,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="target",
        rows=178,
        columns=14,
        size_bytes=15000,
        sklearn_loader="load_wine",
        column_info=[
            ColumnInfo("alcohol", "float"),
            ColumnInfo("malic_acid", "float"),
            ColumnInfo("ash", "float"),
            ColumnInfo("alcalinity_of_ash", "float"),
            ColumnInfo("magnesium", "float"),
            ColumnInfo("total_phenols", "float"),
            ColumnInfo("flavanoids", "float"),
            ColumnInfo("nonflavanoid_phenols", "float"),
            ColumnInfo("proanthocyanins", "float"),
            ColumnInfo("color_intensity", "float"),
            ColumnInfo("hue", "float"),
            ColumnInfo("od280/od315_of_diluted_wines", "float"),
            ColumnInfo("proline", "float"),
            ColumnInfo("target", "int"),
        ],
        tags=["classification", "multiclass", "beginner"],
    ),
    
    "digits": SampleDatasetMeta(
        id="digits",
        name="Digits (Mini-MNIST)",
        description="8x8 handwritten digit images (0-9) for image classification.",
        source=DatasetSource.SKLEARN,
        problem_type=ProblemCategory.IMAGE,
        default_target="target",
        rows=1797,
        columns=65,
        size_bytes=120000,
        sklearn_loader="load_digits",
        column_info=[
            ColumnInfo("pixel_0", "float"),
            # 64 pixel features
            ColumnInfo("target", "int"),
        ],
        tags=["image", "classification", "multiclass", "intermediate"],
    ),

    # -------------------------------------------------------------------------
    # CSV DATASETS (loaded from file)
    # -------------------------------------------------------------------------
    "titanic": SampleDatasetMeta(
        id="titanic",
        name="Titanic",
        description="Titanic passenger survival prediction with demographic and ticket info.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="Survived",
        rows=891,
        columns=12,
        size_bytes=61440,
        file_name="titanic.csv",
        column_info=[
            ColumnInfo("PassengerId", "int"),
            ColumnInfo("Survived", "int"),
            ColumnInfo("Pclass", "int"),
            ColumnInfo("Name", "string"),
            ColumnInfo("Sex", "string"),
            ColumnInfo("Age", "float", missing_percent=19.87),
            ColumnInfo("SibSp", "int"),
            ColumnInfo("Parch", "int"),
            ColumnInfo("Ticket", "string"),
            ColumnInfo("Fare", "float"),
            ColumnInfo("Cabin", "string", missing_percent=77.1),
            ColumnInfo("Embarked", "string", missing_percent=0.22),
        ],
        tags=["classification", "binary", "missing-values", "beginner"],
    ),
    
    "boston_housing": SampleDatasetMeta(
        id="boston_housing",
        name="Boston Housing",
        description="Boston house prices dataset with 13 features (deprecated in sklearn).",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.REGRESSION,
        default_target="MEDV",
        rows=506,
        columns=14,
        size_bytes=51200,
        file_name="boston_housing.csv",
        column_info=[
            ColumnInfo("CRIM", "float"),
            ColumnInfo("ZN", "float"),
            ColumnInfo("INDUS", "float"),
            ColumnInfo("CHAS", "int"),
            ColumnInfo("NOX", "float"),
            ColumnInfo("RM", "float"),
            ColumnInfo("AGE", "float"),
            ColumnInfo("DIS", "float"),
            ColumnInfo("RAD", "int"),
            ColumnInfo("TAX", "float"),
            ColumnInfo("PTRATIO", "float"),
            ColumnInfo("B", "float"),
            ColumnInfo("LSTAT", "float"),
            ColumnInfo("MEDV", "float"),
        ],
        tags=["regression", "real-estate", "beginner"],
    ),
    
    "air_passengers": SampleDatasetMeta(
        id="air_passengers",
        name="Air Passengers",
        description="Monthly airline passenger numbers (1949-1960) for time series analysis.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.TIME_SERIES,
        default_target="Passengers",
        rows=144,
        columns=3,
        size_bytes=2048,
        file_name="air_passengers.csv",
        column_info=[
            ColumnInfo("Month", "datetime"),
            ColumnInfo("Year", "int"),
            ColumnInfo("Passengers", "int"),
        ],
        tags=["time-series", "forecasting", "beginner"],
    ),
    
    "sms_spam": SampleDatasetMeta(
        id="sms_spam",
        name="SMS Spam Collection",
        description="SMS messages labeled as spam or ham for text classification.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.NLP,
        default_target="label",
        rows=5572,
        columns=2,
        size_bytes=500000,
        file_name="sms_spam.csv",
        column_info=[
            ColumnInfo("label", "string"),  # "spam" or "ham"
            ColumnInfo("message", "string"),
        ],
        tags=["nlp", "text", "classification", "binary", "intermediate"],
    ),
    
    "imdb_reviews": SampleDatasetMeta(
        id="imdb_reviews",
        name="IMDb Movie Reviews (Small)",
        description="Movie reviews with sentiment labels (positive/negative) - 1000 sample subset.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.NLP,
        default_target="sentiment",
        rows=1000,
        columns=2,
        size_bytes=1200000,
        file_name="imdb_reviews.csv",
        column_info=[
            ColumnInfo("review", "string"),
            ColumnInfo("sentiment", "string"),  # "positive" or "negative"
        ],
        tags=["nlp", "sentiment", "text", "binary", "intermediate"],
    ),
    
    "credit_fraud": SampleDatasetMeta(
        id="credit_fraud",
        name="Credit Card Fraud (Downsampled)",
        description="Imbalanced fraud detection dataset with anonymized transaction features.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="Class",
        rows=10000,
        columns=31,
        size_bytes=4500000,
        file_name="credit_fraud.csv",
        column_info=[
            ColumnInfo("Time", "float"),
            ColumnInfo("V1", "float"),
            # V2 - V28
            ColumnInfo("Amount", "float"),
            ColumnInfo("Class", "int"),  # 0 = normal, 1 = fraud
        ],
        tags=["imbalanced", "fraud", "classification", "advanced"],
    ),
    
    "synthetic_imbalanced": SampleDatasetMeta(
        id="synthetic_imbalanced",
        name="Synthetic Imbalanced Classification",
        description="Synthetic dataset with 95:5 class imbalance for testing imbalanced learning.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="target",
        rows=10000,
        columns=21,
        size_bytes=2000000,
        file_name="synthetic_imbalanced.csv",
        column_info=[
            ColumnInfo("feature_0", "float"),
            # feature_1 - feature_19
            ColumnInfo("target", "int"),  # 0 or 1 (imbalanced)
        ],
        tags=["imbalanced", "synthetic", "classification", "intermediate"],
    ),
    
    "transactions_categorical": SampleDatasetMeta(
        id="transactions_categorical",
        name="High-Cardinality Transactions",
        description="Transaction dataset with high-cardinality categorical features for testing encoders.",
        source=DatasetSource.CSV,
        problem_type=ProblemCategory.CLASSIFICATION,
        default_target="is_fraud",
        rows=10000,
        columns=10,
        size_bytes=1500000,
        file_name="transactions_categorical.csv",
        column_info=[
            ColumnInfo("transaction_id", "string"),
            ColumnInfo("merchant_id", "string"),  # High cardinality
            ColumnInfo("category", "string"),  # ~50 categories
            ColumnInfo("city", "string"),  # High cardinality
            ColumnInfo("state", "string"),
            ColumnInfo("amount", "float"),
            ColumnInfo("hour", "int"),
            ColumnInfo("day_of_week", "int"),
            ColumnInfo("is_weekend", "int"),
            ColumnInfo("is_fraud", "int"),
        ],
        tags=["categorical", "high-cardinality", "fraud", "advanced"],
    ),
}


class SampleDatasetService:
    """
    Service for loading and listing sample datasets.
    
    Sample datasets are read-only and available to all users.
    """
    
    def __init__(self):
        self.catalog = SAMPLE_CATALOG
        self._sklearn_loaders = {}
    
    def list_samples(self) -> List[Dict[str, Any]]:
        """
        List all available sample datasets with metadata.
        
        Returns:
            List of sample dataset metadata dictionaries
        """
        result = []
        for dataset_id, meta in self.catalog.items():
            result.append({
                "id": meta.id,
                "name": meta.name,
                "description": meta.description,
                "source": meta.source.value,
                "problem_type": meta.problem_type.value,
                "default_target": meta.default_target,
                "rows": meta.rows,
                "columns": meta.columns,
                "size_bytes": meta.size_bytes,
                "tags": meta.tags,
                "column_info": [
                    {
                        "name": col.name,
                        "dtype": col.dtype,
                        "missing_percent": col.missing_percent,
                    }
                    for col in meta.column_info
                ],
            })
        return result
    
    def get_sample_by_id(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific sample dataset."""
        meta = self.catalog.get(dataset_id)
        if not meta:
            return None
        
        return {
            "id": meta.id,
            "name": meta.name,
            "description": meta.description,
            "source": meta.source.value,
            "problem_type": meta.problem_type.value,
            "default_target": meta.default_target,
            "rows": meta.rows,
            "columns": meta.columns,
            "size_bytes": meta.size_bytes,
            "tags": meta.tags,
            "column_info": [
                {
                    "name": col.name,
                    "dtype": col.dtype,
                    "missing_percent": col.missing_percent,
                }
                for col in meta.column_info
            ],
        }
    
    def load_dataset(self, dataset_id: str) -> pd.DataFrame:
        """
        Load a sample dataset by ID.
        
        Args:
            dataset_id: The unique identifier of the sample dataset
            
        Returns:
            pandas DataFrame with the dataset
            
        Raises:
            ValueError: If dataset not found or failed to load
        """
        meta = self.catalog.get(dataset_id)
        if not meta:
            raise ValueError(f"Unknown sample dataset: {dataset_id}")
        
        if meta.source == DatasetSource.SKLEARN:
            return self._load_sklearn_dataset(meta)
        elif meta.source == DatasetSource.CSV:
            return self._load_csv_dataset(meta)
        elif meta.source == DatasetSource.GENERATED:
            return self._generate_dataset(meta)
        else:
            raise ValueError(f"Unknown source type: {meta.source}")
    
    def _load_sklearn_dataset(self, meta: SampleDatasetMeta) -> pd.DataFrame:
        """Load a dataset from sklearn."""
        from sklearn import datasets
        
        loader_name = meta.sklearn_loader
        if not loader_name:
            raise ValueError(f"No sklearn loader specified for {meta.id}")
        
        # Get the loader function
        if not hasattr(datasets, loader_name):
            raise ValueError(f"sklearn.datasets has no function: {loader_name}")
        
        loader_func = getattr(datasets, loader_name)
        
        try:
            # Special handling for fetch_* functions (they download data)
            if loader_name.startswith("fetch_"):
                data = loader_func()
            else:
                data = loader_func()
            
            # Convert to DataFrame
            df = pd.DataFrame(data.data, columns=data.feature_names)
            df["target"] = data.target
            
            logger.info(f"Loaded sklearn dataset '{meta.id}' with shape {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load sklearn dataset {meta.id}: {e}")
            raise ValueError(f"Failed to load dataset {meta.id}: {e}")
    
    def _load_csv_dataset(self, meta: SampleDatasetMeta) -> pd.DataFrame:
        """Load a dataset from CSV file."""
        if not meta.file_name:
            raise ValueError(f"No file_name specified for CSV dataset {meta.id}")
        
        file_path = SAMPLE_DATA_DIR / meta.file_name
        
        if not file_path.exists():
            raise ValueError(
                f"Sample dataset file not found: {file_path}. "
                f"Please add '{meta.file_name}' to the sample_data folder."
            )
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV dataset '{meta.id}' from {file_path} with shape {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV dataset {meta.id}: {e}")
            raise ValueError(f"Failed to load dataset {meta.id}: {e}")
    
    def _generate_dataset(self, meta: SampleDatasetMeta) -> pd.DataFrame:
        """Generate a synthetic dataset."""
        # Placeholder for generated datasets
        # Could use sklearn.datasets.make_classification, etc.
        raise NotImplementedError(f"Generated dataset {meta.id} not yet implemented")
    
    def is_valid_sample(self, dataset_id: str) -> bool:
        """Check if a dataset ID is a valid sample dataset."""
        return dataset_id in self.catalog


# Singleton instance
sample_dataset_service = SampleDatasetService()
