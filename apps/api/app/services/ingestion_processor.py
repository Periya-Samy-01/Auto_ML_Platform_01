"""
Ingestion Processor Service
Handles synchronous dataset ingestion processing (ported from worker)
"""

import os
import uuid
import tempfile
import traceback
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import polars as pl
from sqlalchemy.orm import Session

from packages.database.models import (
    IngestionJob, 
    DatasetVersion, 
    DatasetProfile,
    Dataset,
    User
)
from packages.database.session import SessionLocal

from app.services.r2 import r2_service
from app.services.cache import cache_service
from app.services.ingestion import ingestion_service

# Configure logging
logger = logging.getLogger(__name__)


class IngestionProcessor:
    """Service for processing ingestion jobs synchronously"""

    @classmethod
    def process_dataset_ingestion_sync(cls, job_id: str) -> Dict[str, Any]:
        """
        Process dataset ingestion job synchronously
        
        Args:
            job_id: Ingestion job ID
            
        Returns:
            Processing results
        """
        logger.info(f"Starting synchronous ingestion job {job_id}")
        
        # Create database session
        db = SessionLocal()
        temp_files = []  # Track temp files for cleanup
        job = None
        
        try:
            # 1. Load job from database
            job = db.query(IngestionJob).filter(
                IngestionJob.id == uuid.UUID(job_id)
            ).first()
            
            if not job:
                logger.error(f"Job {job_id} not found")
                return {"status": "failed", "error": "Job not found"}
            
            # Check if already completed (idempotency)
            if job.status == "completed":
                logger.info(f"Job {job_id} already completed")
                return {"status": "already_completed"}
            
            # Get version record
            version = db.query(DatasetVersion).filter(
                DatasetVersion.id == job.dataset_version_id
            ).first()
            
            if not version:
                raise ValueError(f"Version {job.dataset_version_id} not found")
            
            # 2. Update job status to processing
            job.status = "processing"
            job.started_at = datetime.utcnow()
            db.commit()
            
            # Update cache
            cache_service.cache_job_status(
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
            r2_service.download_file_from_r2(temp_r2_key, local_file)
            
            # Update progress
            cache_service.cache_job_status(
                str(job_id), 
                "processing", 
                progress=20
            )
            
            # 4. Load with Polars
            logger.info(f"Loading data with Polars from {local_file}")
            
            # Determine if we should use streaming (for large files)
            # Note: Streaming in API process might be risky if it holds GIL properly, 
            # but Polars is usually fine.
            use_streaming = job.original_size_bytes > 100 * 1024 * 1024  # >100MB
            
            df = cls._load_dataframe_safe(
                local_file, 
                file_ext,
                streaming=use_streaming
            )
            
            # Update progress
            cache_service.cache_job_status(
                str(job_id), 
                "processing", 
                progress=40
            )
            
            # 5. Validate data
            logger.info("Validating data")
            validation_results = ingestion_service.validate_dataframe(df)
            
            if not validation_results["valid"]:
                error_msg = f"Validation failed: {', '.join(validation_results['errors'])}"
                raise ValueError(error_msg)
            
            # Log warnings if any
            if validation_results["warnings"]:
                logger.warning(f"Validation warnings: {validation_results['warnings']}")
            
            # 6. Extract schema
            logger.info("Extracting schema")
            schema = ingestion_service.extract_schema(df)
            
            # 7. Compute profile
            logger.info("Computing statistical profile")
            profile = ingestion_service.compute_standard_profile(df)
            
            # Update progress
            cache_service.cache_job_status(
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
            

            
            # Update progress
            cache_service.cache_job_status(
                str(job_id), 
                "processing", 
                progress=80
            )
            
            # 10. Upload to R2 (permanent location)
            logger.info("Uploading Parquet to R2")
            r2_path = f"datasets/{version.dataset_id}/v{version.id}.parquet"
            
            parquet_size = r2_service.upload_file_to_r2(
                parquet_file,
                r2_path,
                content_type="application/octet-stream"
            )
            
            # 11. Update dataset version in database
            logger.info("Updating database records")
            
            version.s3_path = r2_path
            version.parquet_size_bytes = parquet_size
            version.original_size_bytes = job.original_size_bytes
            version.row_count = row_count
            version.column_count = column_count
            # version.checksum_sha256 = checksum
            version.columns_metadata = schema
            version.processing_status = "completed"
            
            db.commit()
            
            # 12. Store profile
            logger.info("Storing statistical profile")
            
            profile_record = DatasetProfile(
                id=uuid.uuid4(),
                dataset_version_id=version.id,
                profile_data=profile
            )
            
            db.add(profile_record)
            db.commit()
            
            # 13. Update user's storage usage and dataset version
            logger.info(f"Updating dataset {version.dataset_id} metadata")
            
            dataset = db.query(Dataset).filter(
                Dataset.id == version.dataset_id
            ).first()
            
            if dataset:
                # Update current version reference
                dataset.current_version_id = version.id
                logger.info(f"Set current_version_id to {version.id}")
                
                # Update storage usage
                if dataset.user_id:
                    user_record = db.query(User).filter(User.id == dataset.user_id).first()
                    if user_record:
                        user_record.storage_used_bytes += parquet_size
                        logger.info(f"Updated storage for user {user_record.id}")
                
                db.commit()
                logger.info("Database updates committed")
            
            # 14. Cache results
            logger.info("Caching results in Redis")
            
            # Cache schema
            cache_service.cache_schema(
                str(version.dataset_id),
                str(version.id),
                schema,
                ttl=86400  # 24 hours
            )
            
            # Cache preview (first 100 rows)
            preview_data = df.head(100).to_dicts()
            cache_service.cache_preview(
                str(version.dataset_id),
                str(version.id),
                preview_data,
                ttl=3600  # 1 hour
            )
            
            # Cache profile
            cache_service.cache_profile(
                str(version.dataset_id),
                str(version.id),
                profile,
                ttl=21600  # 6 hours
            )
            
            # 15. Delete temp file from R2
            logger.info("Cleaning up temp files")
            r2_service.delete_file_from_r2(temp_r2_key)
            
            # 16. Update job status to completed
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()
            
            # Update cache
            cache_service.cache_job_status(
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
                # "checksum": checksum
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
            cache_service.cache_job_status(
                str(job_id), 
                "failed", 
                progress=0
            )
            
            # No retries in BackgroundTasks for now (keep it simple)
            return {"status": "failed", "error": str(e)}
            
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


    @staticmethod
    def _load_dataframe_safe(
        file_path: str, 
        file_ext: str,
        streaming: bool = False
    ) -> pl.DataFrame:
        """
        Safely load a dataframe with error handling
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
            raise ValueError(f"Failed to load file: {str(e)}")

# Singleton instance
ingestion_processor = IngestionProcessor()
