"""
Cleanup Task
Scheduled task to clean up soft-deleted datasets
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from celery import Task
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session, sessionmaker

from worker.celery_app import celery_app
from worker.services.r2_service import R2Service

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/automl_dev")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(
    name='worker.cleanup_soft_deleted_datasets',
    max_retries=3,
    default_retry_delay=300
)
def cleanup_soft_deleted_datasets(days_before_delete: int = 7) -> Dict[str, Any]:
    """
    Clean up datasets that have been soft-deleted for more than N days
    
    Args:
        days_before_delete: Number of days to wait before permanent deletion
        
    Returns:
        Cleanup statistics
    """
    logger.info(f"Starting cleanup of datasets soft-deleted >{days_before_delete} days ago")
    
    db = SessionLocal()
    r2_service = R2Service()
    
    stats = {
        "datasets_deleted": 0,
        "versions_deleted": 0,
        "bytes_freed": 0,
        "errors": []
    }
    
    try:
        # Import models
        from packages.database.models import Dataset, DatasetVersion
        
        # Find datasets soft-deleted more than N days ago
        cutoff_date = datetime.utcnow() - timedelta(days=days_before_delete)
        
        datasets_to_delete = db.query(Dataset).filter(
            and_(
                Dataset.is_deleted == True,
                Dataset.deleted_at < cutoff_date
            )
        ).all()
        
        logger.info(f"Found {len(datasets_to_delete)} datasets to permanently delete")
        
        for dataset in datasets_to_delete:
            try:
                dataset_id = str(dataset.id)
                logger.info(f"Processing dataset {dataset_id}: {dataset.name}")
                
                # Get all versions for this dataset
                versions = db.query(DatasetVersion).filter(
                    DatasetVersion.dataset_id == dataset.id
                ).all()
                
                # Move R2 files to deleted folder and track freed space
                for version in versions:
                    if version.r2_parquet_path:
                        try:
                            # Move to deleted folder
                            deleted_path = f"deleted/{dataset_id}/{os.path.basename(version.r2_parquet_path)}"
                            
                            # Check if file exists before moving
                            if r2_service.check_file_exists(version.r2_parquet_path):
                                # Copy to deleted location
                                # Note: In production, you'd copy then delete
                                # For now, just delete since we don't have copy in R2Service
                                r2_service.delete_file_from_r2(version.r2_parquet_path)
                                stats["bytes_freed"] += version.parquet_size_bytes
                                
                            stats["versions_deleted"] += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to move R2 file {version.r2_parquet_path}: {e}")
                            stats["errors"].append(f"Failed to delete version {version.id}: {str(e)}")
                
                # Update user's storage quota
                if dataset.user:
                    total_size = sum(v.parquet_size_bytes for v in versions if v.parquet_size_bytes)
                    dataset.user.storage_used_bytes = max(0, dataset.user.storage_used_bytes - total_size)
                
                # Hard delete the dataset (cascades to versions, profiles, jobs)
                db.delete(dataset)
                db.commit()
                
                stats["datasets_deleted"] += 1
                logger.info(f"Successfully deleted dataset {dataset_id}")
                
            except Exception as e:
                logger.error(f"Failed to delete dataset {dataset.id}: {e}")
                stats["errors"].append(f"Failed to delete dataset {dataset.id}: {str(e)}")
                db.rollback()
        
        # Log summary
        logger.info(
            f"Cleanup completed: {stats['datasets_deleted']} datasets deleted, "
            f"{stats['versions_deleted']} versions deleted, "
            f"{stats['bytes_freed'] / (1024*1024):.2f} MB freed"
        )
        
        if stats["errors"]:
            logger.warning(f"Cleanup had {len(stats['errors'])} errors")
        
        return stats
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise
        
    finally:
        db.close()


@celery_app.task(
    name='worker.check_stuck_jobs',
    max_retries=1
)
def check_stuck_jobs(timeout_minutes: int = 30) -> Dict[str, Any]:
    """
    Check for stuck ingestion jobs and mark them as failed
    
    Args:
        timeout_minutes: Minutes before considering a job stuck
        
    Returns:
        Statistics on stuck jobs
    """
    logger.info(f"Checking for jobs stuck in processing for >{timeout_minutes} minutes")
    
    db = SessionLocal()
    
    stats = {
        "stuck_jobs_found": 0,
        "jobs_marked_failed": 0,
        "errors": []
    }
    
    try:
        from packages.database.models import IngestionJob
        
        # Find jobs stuck in processing
        timeout_cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        stuck_jobs = db.query(IngestionJob).filter(
            and_(
                IngestionJob.status == "processing",
                IngestionJob.started_at < timeout_cutoff
            )
        ).all()
        
        stats["stuck_jobs_found"] = len(stuck_jobs)
        
        for job in stuck_jobs:
            try:
                logger.warning(f"Marking stuck job {job.id} as failed")
                
                job.status = "failed"
                job.error_message = f"Job stuck in processing for over {timeout_minutes} minutes"
                job.completed_at = datetime.utcnow()
                
                db.commit()
                stats["jobs_marked_failed"] += 1
                
            except Exception as e:
                logger.error(f"Failed to update stuck job {job.id}: {e}")
                stats["errors"].append(f"Failed to update job {job.id}: {str(e)}")
                db.rollback()
        
        logger.info(
            f"Stuck job check completed: {stats['stuck_jobs_found']} found, "
            f"{stats['jobs_marked_failed']} marked as failed"
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Stuck job check failed: {e}")
        raise
        
    finally:
        db.close()


# Celery Beat Schedule (add to celery configuration)
CELERYBEAT_SCHEDULE = {
    'cleanup-soft-deleted-datasets': {
        'task': 'worker.cleanup_soft_deleted_datasets',
        'schedule': timedelta(days=1),  # Run daily
        'kwargs': {'days_before_delete': 7}
    },
    'check-stuck-jobs': {
        'task': 'worker.check_stuck_jobs',
        'schedule': timedelta(minutes=30),  # Run every 30 minutes
        'kwargs': {'timeout_minutes': 30}
    }
}
