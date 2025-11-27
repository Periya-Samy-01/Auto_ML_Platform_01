"""
Dataset Ingestion Task
Processes uploaded datasets asynchronously
"""

import os
import uuid
import tempfile
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import polars as pl
from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from worker.celery_app import celery_app
from worker.errors import ProcessingError

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration (from environment)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/automl_dev")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class IngestionTask(Task):
    """Custom task class with database session management"""
    
    def __init__(self):
        self.r2_service = None
        self.cache_service = None
    
    def __call__(self, *args, **kwargs):
        """Initialize services on first call"""
        if not self.r2_service:
            from worker.services.r2_service import R2Service
            from worker.services.cache_service import CacheService
            self.r2_service = R2Service()
            self.cache_service = CacheService()
        return super().__call__(*args, **kwargs)


@celery_app.task(
    bind=True,
    base=IngestionTask,
    name='worker.process_dataset_ingestion',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ProcessingError,),
    acks_late=True,
    reject_on_worker_lost=True
)
def process_dataset_ingestion(self, job_id: str) -> Dict[str, Any]:
    """
    Process dataset ingestion job
    
    Args:
        job_id: Ingestion job ID
        
    Returns:
        Processing results
    """
    logger.info(f"Starting ingestion job {job_id}")
    
    # Create database session
    db = SessionLocal()
    temp_files = []  # Track temp files for cleanup
    
    try:
        # Import models (avoid circular imports)
        from packages.database.models import (
            IngestionJob, 
            DatasetVersion, 
            DatasetProfile,
            Dataset
        )
        
        # 1. Load job from database
        job = db.query(IngestionJob).filter(
            IngestionJob.id == uuid.UUID(job_id)
        ).first()
        
        if not job:
            raise ProcessingError(f"Job {job_id} not found")
        
        # Check if already completed (idempotency)
        if job.status == "completed":
            logger.info(f"Job {job_id} already completed")
            return {"status": "already_completed"}
        
        # Get version record
        version = db.query(DatasetVersion).filter(
            DatasetVersion.id == job.version_id
        ).first()
        
        if not version:
            raise ProcessingError(f"Version {job.version_id} not found")
        
        # 2. Update job status to processing
        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Update cache
        self.cache_service.cache_job_status(
            str(job_id), 
            "processing", 
            progress=10
        )
        
        # 3. Download temp file from R2
        logger.info(f"Downloading file from R2: upload_id={job.upload_id}")
        
        # Determine file extension from original filename
        file_ext = os.path.splitext(job.original_filename)[1].lower()
        if not file_ext:
            file_ext = '.csv'  # Default to CSV
        
        temp_r2_key = f"uploads/temp/{job.upload_id}{file_ext}"
        
        # Create local temp file
        temp_dir = tempfile.mkdtemp()
        local_file = os.path.join(temp_dir, f"data{file_ext}")
        temp_files.append(temp_dir)
        
        # Download from R2
        self.r2_service.download_file_from_r2(temp_r2_key, local_file)
        
        # Update progress
        self.cache_service.cache_job_status(
            str(job_id), 
            "processing", 
            progress=20
        )
        
        # 4. Load with Polars
        logger.info(f"Loading data with Polars from {local_file}")
        
        # Determine if we should use streaming (for large files)
        use_streaming = job.original_size_bytes > 100 * 1024 * 1024  # >100MB
        
        df = load_dataframe_safe(
            local_file, 
            file_ext,
            streaming=use_streaming
        )
        
        # Update progress
        self.cache_service.cache_job_status(
            str(job_id), 
            "processing", 
            progress=40
        )
        
        # 5. Validate data
        logger.info("Validating data")
        validation_results = validate_dataframe(df)
        
        if not validation_results["valid"]:
            error_msg = f"Validation failed: {', '.join(validation_results['errors'])}"
            raise ProcessingError(error_msg)
        
        # Log warnings if any
        if validation_results["warnings"]:
            logger.warning(f"Validation warnings: {validation_results['warnings']}")
        
        # 6. Extract schema
        logger.info("Extracting schema")
        schema = extract_schema(df)
        
        # 7. Compute profile
        logger.info("Computing statistical profile")
        profile = compute_standard_profile(df)
        
        # Update progress
        self.cache_service.cache_job_status(
            str(job_id), 
            "processing", 
            progress=60
        )
        
        # 8. Convert to Parquet
        logger.info("Converting to Parquet format")
        parquet_file = os.path.join(temp_dir, "data.parquet")
        
        # Write with compression
        df.write_parquet(
            parquet_file,
            compression="snappy",
            statistics=True,
            row_group_size=50000
        )
        
        # Get file sizes
        parquet_size = os.path.getsize(parquet_file)
        row_count = len(df)
        column_count = len(df.columns)
        
        # 9. Compute checksum
        logger.info("Computing checksum")
        checksum = self.r2_service.compute_file_checksum(parquet_file)
        
        # Check for duplicate (same file uploaded before)
        existing = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == version.dataset_id,
            DatasetVersion.checksum_sha256 == checksum,
            DatasetVersion.id != version.id
        ).first()
        
        if existing:
            logger.warning(f"Duplicate file detected. Matches version {existing.version_number}")
        
        # Update progress
        self.cache_service.cache_job_status(
            str(job_id), 
            "processing", 
            progress=80
        )
        
        # 10. Upload to R2 (permanent location)
        logger.info("Uploading Parquet to R2")
        r2_path = f"datasets/{version.dataset_id}/v{version.id}.parquet"
        
        parquet_size = self.r2_service.upload_file_to_r2(
            parquet_file,
            r2_path,
            content_type="application/octet-stream"
        )
        
        # 11. Update dataset version in database
        logger.info("Updating database records")
        
        version.r2_parquet_path = r2_path
        version.parquet_size_bytes = parquet_size
        version.original_size_bytes = job.original_size_bytes
        version.row_count = row_count
        version.column_count = column_count
        version.checksum_sha256 = checksum
        version.schema_json = schema
        version.processing_status = "completed"
        
        db.commit()
        
        # 12. Store profile
        logger.info("Storing statistical profile")
        
        profile_record = DatasetProfile(
            id=uuid.uuid4(),
            version_id=version.id,
            profile_json=profile,
            computed_at=datetime.utcnow()
        )
        
        db.add(profile_record)
        db.commit()
        
        # 13. Update user's storage usage
        dataset = db.query(Dataset).filter(
            Dataset.id == version.dataset_id
        ).first()
        
        if dataset and dataset.user:
            dataset.user.storage_used_bytes += parquet_size
            db.commit()
        
        # 14. Cache results
        logger.info("Caching results in Redis")
        
        # Cache schema
        self.cache_service.cache_schema(
            str(version.dataset_id),
            str(version.id),
            schema,
            ttl=86400  # 24 hours
        )
        
        # Cache preview (first 100 rows)
        preview_data = df.head(100).to_dicts()
        self.cache_service.cache_preview(
            str(version.dataset_id),
            str(version.id),
            preview_data,
            ttl=3600  # 1 hour
        )
        
        # Cache profile
        self.cache_service.cache_profile(
            str(version.dataset_id),
            str(version.id),
            profile,
            ttl=21600  # 6 hours
        )
        
        # 15. Delete temp file from R2
        logger.info("Cleaning up temp files")
        self.r2_service.delete_file_from_r2(temp_r2_key)
        
        # 16. Update job status to completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        
        # Update cache
        self.cache_service.cache_job_status(
            str(job_id), 
            "completed", 
            progress=100
        )
        
        logger.info(f"Successfully completed ingestion job {job_id}")
        
        return {
            "status": "completed",
            "dataset_id": str(version.dataset_id),
            "version_id": str(version.id),
            "version_number": version.version_number,
            "row_count": row_count,
            "column_count": column_count,
            "parquet_size_bytes": parquet_size,
            "checksum": checksum
        }
        
    except Exception as e:
        # Log error
        logger.error(f"Failed to process job {job_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Update job status
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.error_traceback = traceback.format_exc()
            job.completed_at = datetime.utcnow()
            job.retry_count += 1
            db.commit()
        
        # Update cache
        self.cache_service.cache_job_status(
            str(job_id), 
            "failed", 
            progress=0
        )
        
        # Retry if retries remaining
        if job and job.retry_count < 3:
            logger.info(f"Retrying job {job_id} (attempt {job.retry_count + 1}/3)")
            raise self.retry(exc=e, countdown=60 * (2 ** job.retry_count))
        
        raise
        
    finally:
        # Clean up temp files
        import shutil
        for temp_path in temp_files:
            try:
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_path}: {e}")
        
        # Close database session
        db.close()


def load_dataframe_safe(
    file_path: str, 
    file_ext: str,
    streaming: bool = False
) -> pl.DataFrame:
    """
    Safely load a dataframe with error handling
    
    Args:
        file_path: Path to file
        file_ext: File extension
        streaming: Use lazy loading
        
    Returns:
        Polars DataFrame
    """
    try:
        if file_ext in ['.csv', '.txt']:
            # Try to infer separator
            if streaming:
                df = pl.scan_csv(
                    file_path,
                    ignore_errors=True,
                    try_parse_dates=True
                ).collect()
            else:
                df = pl.read_csv(
                    file_path,
                    ignore_errors=True,
                    try_parse_dates=True
                )
                
        elif file_ext == '.json':
            df = pl.read_json(file_path)
            
        elif file_ext == '.parquet':
            if streaming:
                df = pl.scan_parquet(file_path).collect()
            else:
                df = pl.read_parquet(file_path)
                
        elif file_ext in ['.xlsx', '.xls']:
            df = pl.read_excel(file_path)
            
        else:
            # Try CSV as default
            df = pl.read_csv(file_path, ignore_errors=True)
            
        return df
        
    except Exception as e:
        logger.error(f"Failed to load file: {e}")
        raise ProcessingError(f"Failed to load file: {str(e)}")


def extract_schema(df: pl.DataFrame) -> Dict[str, Any]:
    """Extract schema information from DataFrame"""
    schema = {
        "columns": []
    }
    
    for col_name in df.columns:
        col_dtype = str(df[col_name].dtype)
        col_info = {
            "name": col_name,
            "dtype": col_dtype,
            "null_count": int(df[col_name].null_count()),
            "null_percentage": float((df[col_name].null_count() / len(df)) * 100) if len(df) > 0 else 0.0
        }
        schema["columns"].append(col_info)
    
    return schema


def compute_standard_profile(df: pl.DataFrame) -> Dict[str, Any]:
    """Compute statistical profile for dataset"""
    profile = {
        "columns": [],
        "row_count": len(df),
        "column_count": len(df.columns),
        "computed_at": datetime.utcnow().isoformat()
    }
    
    for col_name in df.columns:
        col = df[col_name]
        col_dtype = str(col.dtype)
        
        col_stats = {
            "name": col_name,
            "dtype": col_dtype,
            "null_count": int(col.null_count()),
            "null_percentage": float((col.null_count() / len(df)) * 100) if len(df) > 0 else 0.0,
            "unique_count": int(col.n_unique())
        }
        
        # Numeric statistics
        if col_dtype in ['Int8', 'Int16', 'Int32', 'Int64', 'Float32', 'Float64', 
                        'UInt8', 'UInt16', 'UInt32', 'UInt64']:
            try:
                col_stats.update({
                    "min": float(col.min()) if col.min() is not None else None,
                    "max": float(col.max()) if col.max() is not None else None,
                    "mean": float(col.mean()) if col.mean() is not None else None,
                    "median": float(col.median()) if col.median() is not None else None,
                    "std": float(col.std()) if col.std() is not None else None,
                    "percentiles": {
                        "25": float(col.quantile(0.25)) if len(col) > 0 else None,
                        "50": float(col.quantile(0.50)) if len(col) > 0 else None,
                        "75": float(col.quantile(0.75)) if len(col) > 0 else None
                    }
                })
            except Exception as e:
                logger.warning(f"Failed to compute numeric stats for {col_name}: {e}")
        
        # Categorical statistics
        elif col_dtype in ['Utf8', 'Categorical', 'String']:
            try:
                # Get top 10 values
                value_counts = col.value_counts().head(10)
                col_stats["top_values"] = [
                    {"value": str(row[0]) if row[0] is not None else None, 
                     "count": int(row[1])}
                    for row in value_counts.iter_rows()
                ]
                
                # Get mode
                if len(value_counts) > 0:
                    col_stats["mode"] = str(value_counts[0, 0])
                    
            except Exception as e:
                logger.warning(f"Failed to compute categorical stats for {col_name}: {e}")
        
        # Boolean statistics
        elif col_dtype == 'Boolean':
            try:
                true_count = int(col.sum()) if col.sum() is not None else 0
                false_count = len(col) - true_count - int(col.null_count())
                col_stats["true_count"] = true_count
                col_stats["false_count"] = false_count
                col_stats["true_percentage"] = float((true_count / len(df)) * 100) if len(df) > 0 else 0.0
            except Exception as e:
                logger.warning(f"Failed to compute boolean stats for {col_name}: {e}")
        
        # Date/Datetime statistics
        elif 'Date' in col_dtype or 'Datetime' in col_dtype:
            try:
                col_stats["min"] = str(col.min()) if col.min() is not None else None
                col_stats["max"] = str(col.max()) if col.max() is not None else None
            except Exception as e:
                logger.warning(f"Failed to compute date stats for {col_name}: {e}")
        
        # Sample values
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


def validate_dataframe(df: pl.DataFrame) -> Dict[str, Any]:
    """Validate DataFrame for common issues"""
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
    
    # Check minimum rows
    if len(df) < 10:
        validation["warnings"].append(f"Dataset has only {len(df)} rows")
    
    # Check minimum columns
    if len(df.columns) < 2:
        validation["warnings"].append(f"Dataset has only {len(df.columns)} column(s)")
    
    # Check for duplicate column names
    if len(df.columns) != len(set(df.columns)):
        validation["errors"].append("Duplicate column names found")
        validation["valid"] = False
    
    # Check for columns with all nulls
    for col in df.columns:
        null_count = df[col].null_count()
        if null_count == len(df):
            validation["warnings"].append(f"Column '{col}' contains only null values")
    
    # Check for high null percentages
    for col in df.columns:
        null_pct = (df[col].null_count() / len(df)) * 100
        if null_pct > 90:
            validation["warnings"].append(
                f"Column '{col}' has {null_pct:.1f}% null values"
            )
    
    # Check for suspicious column names
    suspicious_patterns = ['unnamed', 'column', '__']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in suspicious_patterns):
            validation["warnings"].append(
                f"Column '{col}' has a generic name, consider renaming"
            )
    
    return validation
