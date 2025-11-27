"""
Ingestion Service
Handles dataset ingestion jobs and processing
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import os
import tempfile

import polars as pl
from sqlalchemy.orm import Session

from packages.database.models import IngestionJob, DatasetProfile, DatasetVersion, User
from packages.database.models.enums import FileFormat
from app.core.config import settings
from app.services.cache import cache_service

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for dataset ingestion and processing"""
    
    @staticmethod
    def create_ingestion_job(
        db: Session,
        user_id: uuid.UUID,
        dataset_id: uuid.UUID,
        dataset_version_id: uuid.UUID,
        upload_id: uuid.UUID,
        original_filename: str,
        original_size_bytes: int
    ) -> IngestionJob:
        """
        Create an ingestion job record
        
        Args:
            db: Database session
            user_id: User ID
            dataset_id: Dataset ID
            dataset_version_id: Dataset version ID
            upload_id: Upload tracking ID
            original_filename: Original file name
            original_size_bytes: File size
            
        Returns:
            Created ingestion job
        """
        job = IngestionJob(
            id=uuid.uuid4(),
            user_id=user_id,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            upload_id=upload_id,
            original_filename=original_filename,
            original_size_bytes=original_size_bytes,
            status="pending",
            retry_count=0
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Cache job status
        cache_service.cache_job_status(
            str(job.id),
            "pending",
            progress=0
        )
        
        logger.info(f"Created ingestion job {job.id}")
        return job
    
    @staticmethod
    def get_ingestion_job(
        db: Session,
        job_id: uuid.UUID
    ) -> Optional[IngestionJob]:
        """Get an ingestion job by ID"""
        return db.query(IngestionJob).filter(
            IngestionJob.id == job_id
        ).first()
    
    @staticmethod
    def update_job_status(
        db: Session,
        job_id: uuid.UUID,
        status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None,
        celery_task_id: Optional[str] = None
    ) -> None:
        """
        Update ingestion job status
        
        Args:
            db: Database session
            job_id: Job ID
            status: New status
            started_at: Job start time
            completed_at: Job completion time
            error_message: Error message if failed
            error_traceback: Error traceback if failed
            celery_task_id: Celery task ID
        """
        job = db.query(IngestionJob).filter(
            IngestionJob.id == job_id
        ).first()
        
        if not job:
            raise ValueError("Job not found")
        
        # Update fields
        job.status = status
        
        if started_at:
            job.started_at = started_at
        if completed_at:
            job.completed_at = completed_at
        if error_message:
            job.error_message = error_message
        if error_traceback:
            job.error_traceback = error_traceback
        if celery_task_id:
            job.celery_task_id = celery_task_id
        
        db.commit()
        
        # Update cache
        progress_map = {
            "pending": 0,
            "processing": 50,
            "completed": 100,
            "failed": 0
        }
        cache_service.cache_job_status(
            str(job_id),
            status,
            progress=progress_map.get(status, 0)
        )
        
        logger.info(f"Updated job {job_id} status to {status}")
    
    @staticmethod
    def extract_schema(df: pl.DataFrame) -> Dict[str, Any]:
        """
        Extract schema information from a Polars DataFrame
        
        Args:
            df: Polars DataFrame
            
        Returns:
            Schema dictionary with column information
        """
        schema = {
            "columns": []
        }
        
        for col_name in df.columns:
            col_dtype = str(df[col_name].dtype)
            col_info = {
                "name": col_name,
                "dtype": col_dtype,
                "null_count": df[col_name].null_count(),
                "null_percentage": (df[col_name].null_count() / len(df)) * 100 if len(df) > 0 else 0
            }
            schema["columns"].append(col_info)
        
        return schema
    
    @staticmethod
    def compute_standard_profile(df: pl.DataFrame) -> Dict[str, Any]:
        """
        Compute statistical profile for a dataset
        
        Args:
            df: Polars DataFrame
            
        Returns:
            Profile dictionary with statistics
        """
        profile = {
            "columns": [],
            "row_count": len(df),
            "column_count": len(df.columns)
        }
        
        for col_name in df.columns:
            col = df[col_name]
            col_dtype = str(col.dtype)
            
            col_stats = {
                "name": col_name,
                "dtype": col_dtype,
                "null_count": col.null_count(),
                "null_percentage": (col.null_count() / len(df)) * 100 if len(df) > 0 else 0,
                "unique_count": col.n_unique()
            }
            
            # Add numeric statistics if applicable
            if col_dtype in ['Int8', 'Int16', 'Int32', 'Int64', 'Float32', 'Float64', 
                            'UInt8', 'UInt16', 'UInt32', 'UInt64']:
                try:
                    col_stats.update({
                        "min": float(col.min()) if col.min() is not None else None,
                        "max": float(col.max()) if col.max() is not None else None,
                        "mean": float(col.mean()) if col.mean() is not None else None,
                        "median": float(col.median()) if col.median() is not None else None,
                        "std": float(col.std()) if col.std() is not None else None
                    })
                except Exception as e:
                    logger.warning(f"Failed to compute numeric stats for {col_name}: {e}")
            
            # Add categorical statistics
            elif col_dtype in ['Utf8', 'Categorical']:
                try:
                    # Get value counts for top 10 values
                    value_counts = col.value_counts().head(10)
                    col_stats["top_values"] = [
                        {"value": str(row[0]), "count": int(row[1])}
                        for row in value_counts.iter_rows()
                    ]
                except Exception as e:
                    logger.warning(f"Failed to compute categorical stats for {col_name}: {e}")
            
            # Add sample values (first 5 non-null values)
            try:
                sample_values = col.drop_nulls().head(5).to_list()
                col_stats["sample_values"] = [
                    str(v) if v is not None else None 
                    for v in sample_values
                ]
            except Exception as e:
                logger.warning(f"Failed to get sample values for {col_name}: {e}")
                col_stats["sample_values"] = []
            
            profile["columns"].append(col_stats)
        
        return profile
    
    @staticmethod
    def create_dataset_profile(
        db: Session,
        dataset_version_id: uuid.UUID,
        profile_data: Dict[str, Any]
    ) -> DatasetProfile:
        """
        Store computed profile for a dataset version
        
        Args:
            db: Database session
            dataset_version_id: Dataset version ID
            profile_data: Computed profile data
            
        Returns:
            Created profile record
        """
        profile = DatasetProfile(
            id=uuid.uuid4(),
            dataset_version_id=dataset_version_id,
            profile_data=profile_data
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        # Cache profile
        version = db.query(DatasetVersion).filter(
            DatasetVersion.id == dataset_version_id
        ).first()
        
        if version:
            cache_service.cache_profile(
                str(version.dataset_id),
                str(dataset_version_id),
                profile_data
            )
        
        logger.info(f"Created profile for version {dataset_version_id}")
        return profile
    
    @staticmethod
    def detect_file_format(filename: str) -> FileFormat:
        """
        Detect file format from filename
        
        Args:
            filename: File name
            
        Returns:
            Detected file format
        """
        extension = os.path.splitext(filename)[1].lower()
        
        format_map = {
            '.csv': FileFormat.CSV,
            '.json': FileFormat.JSON,
            '.parquet': FileFormat.PARQUET,
            '.xlsx': FileFormat.EXCEL,
            '.xls': FileFormat.EXCEL
        }
        
        return format_map.get(extension, FileFormat.UNKNOWN)
    
    @staticmethod
    def load_dataframe(
        file_path: str,
        file_format: FileFormat,
        streaming: bool = False
    ) -> pl.DataFrame:
        """
        Load a file into a Polars DataFrame
        
        Args:
            file_path: Path to file
            file_format: File format
            streaming: Use lazy loading for large files
            
        Returns:
            Polars DataFrame
        """
        try:
            if file_format == FileFormat.CSV:
                if streaming:
                    return pl.scan_csv(file_path).collect()
                return pl.read_csv(file_path)
            
            elif file_format == FileFormat.JSON:
                return pl.read_json(file_path)
            
            elif file_format == FileFormat.PARQUET:
                if streaming:
                    return pl.scan_parquet(file_path).collect()
                return pl.read_parquet(file_path)
            
            elif file_format == FileFormat.EXCEL:
                return pl.read_excel(file_path)
            
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
                
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            raise
    
    @staticmethod
    def validate_dataframe(df: pl.DataFrame) -> Dict[str, Any]:
        """
        Validate a DataFrame for common issues
        
        Args:
            df: Polars DataFrame
            
        Returns:
            Validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if empty
        if len(df) == 0:
            validation["errors"].append("Dataset is empty")
            validation["valid"] = False
            return validation
        
        # Check if too few columns
        if len(df.columns) < 2:
            validation["warnings"].append("Dataset has only one column")
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            validation["errors"].append("Duplicate column names found")
            validation["valid"] = False
        
        # Check for columns with all nulls
        for col in df.columns:
            if df[col].null_count() == len(df):
                validation["warnings"].append(f"Column '{col}' contains only null values")
        
        # Check for very high null percentages
        for col in df.columns:
            null_pct = (df[col].null_count() / len(df)) * 100
            if null_pct > 90:
                validation["warnings"].append(
                    f"Column '{col}' has {null_pct:.1f}% null values"
                )
        
        return validation
    
    @staticmethod
    def compute_file_checksum(file_path: str) -> str:
        """
        Compute SHA-256 checksum of a file
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


# Singleton instance
ingestion_service = IngestionService()
