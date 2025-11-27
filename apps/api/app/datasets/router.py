"""
Dataset API Router
Endpoints for dataset management and upload
"""

import uuid
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from packages.database.models import User, Dataset, DatasetVersion, IngestionJob
from packages.database.models.enums import ProblemType, FileFormat, UserTier
from app.services import (
    r2_service, 
    dataset_service, 
    ingestion_service,
    cache_service
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"]
)


# Pydantic Models
class UploadURLRequest(BaseModel):
    """Request for generating upload URL"""
    filename: str = Field(..., description="Name of file to upload")
    size_bytes: int = Field(..., gt=0, description="File size in bytes")


class UploadURLResponse(BaseModel):
    """Response with presigned upload URL"""
    upload_id: str
    upload_url: str
    expires_at: datetime
    max_size_bytes: int


class ConfirmUploadRequest(BaseModel):
    """Request to confirm upload and start processing"""
    upload_id: str
    dataset_name: str
    description: Optional[str] = None
    problem_type: Optional[ProblemType] = None
    target_column: Optional[str] = None
    create_new_version: bool = False
    dataset_id: Optional[str] = None  # Required if create_new_version=True
    version_label: Optional[str] = None


class ConfirmUploadResponse(BaseModel):
    """Response after confirming upload"""
    job_id: str
    dataset_id: str
    dataset_version_id: str
    version_number: int
    status: str
    estimated_duration_seconds: int


class DatasetResponse(BaseModel):
    """Dataset details response"""
    id: str
    name: str
    description: Optional[str]
    problem_type: Optional[ProblemType]
    target_column: Optional[str]
    current_version_id: Optional[str]
    row_count: Optional[int]
    column_count: Optional[int]
    created_at: datetime
    updated_at: datetime


class DatasetListResponse(BaseModel):
    """Paginated dataset list response"""
    datasets: List[DatasetResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    progress_percentage: int
    error_message: Optional[str]
    dataset_id: str
    dataset_version_id: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


# Endpoints
@router.post("/upload-url", response_model=UploadURLResponse)
async def generate_upload_url(
    request: UploadURLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a presigned URL for direct file upload to R2
    """
    # Check file size limits based on user tier
    size_limits = {
        UserTier.FREE: settings.MAX_UPLOAD_SIZE_MB_FREE * 1024 * 1024,
        UserTier.PRO: settings.MAX_UPLOAD_SIZE_MB_PRO * 1024 * 1024,
        UserTier.ENTERPRISE: settings.MAX_UPLOAD_SIZE_MB_ENTERPRISE * 1024 * 1024
    }
    
    max_size = size_limits.get(current_user.tier, size_limits[UserTier.FREE])
    
    if request.size_bytes > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {max_size // (1024*1024)}MB limit for {current_user.tier} tier"
        )
    
    # Check storage quota
    if not dataset_service.check_storage_quota(db, current_user.id, request.size_bytes):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Storage quota exceeded. Please upgrade your plan."
        )
    
    # Generate upload ID and presigned URL
    upload_id = str(uuid.uuid4())
    
    try:
        url, expires_at = r2_service.generate_presigned_upload_url(
            upload_id=upload_id,
            filename=request.filename,
            content_type='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Failed to generate upload URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )
    
    return UploadURLResponse(
        upload_id=upload_id,
        upload_url=url,
        expires_at=expires_at,
        max_size_bytes=max_size
    )


@router.post("/confirm", response_model=ConfirmUploadResponse)
async def confirm_upload(
    request: ConfirmUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm file upload and start processing job
    """
    # Validate upload exists in R2
    temp_key = f"uploads/temp/{request.upload_id}"
    file_extension = request.dataset_name.split('.')[-1] if '.' in request.dataset_name else 'csv'
    temp_key = f"{temp_key}.{file_extension}"
    
    if not r2_service.check_file_exists(temp_key):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found. Please upload the file first."
        )
    
    file_size = r2_service.get_file_size(temp_key)
    
    # Create or get dataset
    if request.create_new_version:
        if not request.dataset_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="dataset_id is required when creating new version"
            )
        
        dataset = dataset_service.get_dataset(
            db, 
            uuid.UUID(request.dataset_id), 
            current_user.id
        )
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
    else:
        # Create new dataset
        try:
            dataset = dataset_service.create_dataset(
                db=db,
                user_id=current_user.id,
                name=request.dataset_name,
                description=request.description,
                problem_type=request.problem_type,
                target_column=request.target_column
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Detect file format
    file_format = ingestion_service.detect_file_format(request.dataset_name)
    
    # Create version record
    version = dataset_service.create_dataset_version(
        db=db,
        dataset_id=dataset.id,
        upload_id=uuid.UUID(request.upload_id),
        original_filename=request.dataset_name,
        original_size_bytes=file_size,
        original_format=file_format,
        version_label=request.version_label
    )
    
    # Create ingestion job
    job = ingestion_service.create_ingestion_job(
        db=db,
        user_id=current_user.id,
        dataset_id=dataset.id,
        dataset_version_id=version.id,
        upload_id=uuid.UUID(request.upload_id),
        original_filename=request.dataset_name,
        original_size_bytes=file_size
    )
    
    # Queue Celery task
    from app.tasks import process_dataset_ingestion
    
    task = process_dataset_ingestion.delay(str(job.id))
    
    # Update job with Celery task ID
    ingestion_service.update_job_status(
        db=db,
        job_id=job.id,
        status="pending",
        celery_task_id=task.id
    )
    
    # Estimate duration based on file size
    estimated_duration = 30  # Base 30 seconds
    if file_size > 10 * 1024 * 1024:  # >10MB
        estimated_duration = 60
    if file_size > 100 * 1024 * 1024:  # >100MB
        estimated_duration = 180
    
    return ConfirmUploadResponse(
        job_id=str(job.id),
        dataset_id=str(dataset.id),
        dataset_version_id=str(version.id),
        version_number=version.version_number,
        status="pending",
        estimated_duration_seconds=estimated_duration
    )


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    problem_type: Optional[ProblemType] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|name)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's datasets with pagination
    """
    skip = (page - 1) * per_page
    
    datasets, total = dataset_service.list_user_datasets(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
        problem_type=problem_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert to response format
    dataset_responses = []
    for dataset in datasets:
        # Get current version info if available
        row_count = None
        column_count = None
        
        if dataset.current_version:
            row_count = dataset.current_version.row_count
            column_count = dataset.current_version.column_count
        
        dataset_responses.append(DatasetResponse(
            id=str(dataset.id),
            name=dataset.name,
            description=dataset.description,
            problem_type=dataset.problem_type,
            target_column=dataset.target_column,
            current_version_id=str(dataset.current_version_id) if dataset.current_version_id else None,
            row_count=row_count,
            column_count=column_count,
            created_at=dataset.created_at,
            updated_at=dataset.updated_at
        ))
    
    total_pages = (total + per_page - 1) // per_page
    
    return DatasetListResponse(
        datasets=dataset_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dataset details by ID
    """
    dataset = dataset_service.get_dataset(
        db=db,
        dataset_id=uuid.UUID(dataset_id),
        user_id=current_user.id,
        include_versions=False
    )
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Get current version info
    row_count = None
    column_count = None
    
    if dataset.current_version:
        row_count = dataset.current_version.row_count
        column_count = dataset.current_version.column_count
    
    return DatasetResponse(
        id=str(dataset.id),
        name=dataset.name,
        description=dataset.description,
        problem_type=dataset.problem_type,
        target_column=dataset.target_column,
        current_version_id=str(dataset.current_version_id) if dataset.current_version_id else None,
        row_count=row_count,
        column_count=column_count,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at
    )


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a dataset (hard delete with CASCADE)
    """
    success = dataset_service.delete_dataset(
        db=db,
        dataset_id=uuid.UUID(dataset_id),
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return {"message": "Dataset deleted successfully"}


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ingestion job status
    """
    # Check cache first
    cached_status = cache_service.get_cached_job_status(job_id)
    
    # Get job from database
    job = ingestion_service.get_ingestion_job(db, uuid.UUID(job_id))
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get progress from cache or estimate
    progress = 0
    if cached_status:
        progress = cached_status.get('progress', 0)
    else:
        progress_map = {
            "pending": 10,
            "processing": 50,
            "completed": 100,
            "failed": 0
        }
        progress = progress_map.get(job.status, 0)
    
    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        progress_percentage=progress,
        error_message=job.error_message,
        dataset_id=str(job.dataset_id),
        dataset_version_id=str(job.dataset_version_id) if job.dataset_version_id else None,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at
    )
