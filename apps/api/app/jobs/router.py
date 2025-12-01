"""
Job API Router
Endpoints for job creation, management, and monitoring
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.enums import JobStatus
from packages.database.models.user import User

from .schemas import (
    JobBrief,
    JobCancelResponse,
    JobCreate,
    JobListResponse,
    JobLogsResponse,
    JobNodeResponse,
    JobResponse,
    JobRetryResponse,
    JobStatsResponse,
)
from .service import (
    cancel_job,
    create_job,
    get_job_by_id,
    get_job_logs,
    get_job_stats,
    get_jobs,
    retry_job,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


# ============================================================
# Job CRUD Endpoints
# ============================================================

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_new_job(
    request: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new job and queue it for execution.

    This endpoint will:
    1. Validate the workflow snapshot exists and belongs to the user
    2. Calculate the estimated credit cost based on workflow complexity
    3. Check if user has sufficient credits
    4. Atomically create the job and deduct credits
    5. Queue the job for execution in Celery

    **Returns:**
    - 201: Job created successfully
    - 400: Invalid workflow
    - 402: Insufficient credits
    - 404: Workflow snapshot not found
    """
    logger.info(
        f"User {current_user.id} creating job for workflow {request.workflow_snapshot_id}"
    )

    job = create_job(
        db=db,
        user=current_user,
        workflow_snapshot_id=request.workflow_snapshot_id,
        priority=request.priority,
    )

    logger.info(
        f"Job {job.id} created successfully (cost: {job.credits_cost} credits)"
    )

    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status_filter: Optional[JobStatus] = Query(
        None, description="Filter by job status"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of jobs for the current user.

    **Query Parameters:**
    - status_filter: Optional filter by job status
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)

    **Returns:**
    - List of jobs with pagination metadata
    """
    offset = (page - 1) * page_size

    jobs, total = get_jobs(
        db=db,
        user=current_user,
        status_filter=status_filter,
        limit=page_size,
        offset=offset,
    )

    # Convert to brief format
    job_briefs = [JobBrief.model_validate(job) for job in jobs]

    # Calculate pagination metadata
    has_more = (offset + page_size) < total

    return JobListResponse(
        items=job_briefs,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific job.

    **Returns:**
    - 200: Job details
    - 404: Job not found or access denied
    """
    job = get_job_by_id(db=db, user=current_user, job_id=job_id)

    return job


# ============================================================
# Job Action Endpoints
# ============================================================

@router.post("/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_job_endpoint(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a running or queued job.

    This endpoint will:
    1. Verify the job is cancellable (pending/queued/running)
    2. Revoke the Celery task if it's running
    3. Calculate refund amount with penalty based on cancellation history
    4. Issue credit refund
    5. Update job status to cancelled

    **Refund Policy:**
    - 0 cancellations in last 30 days: 100% refund
    - 5 cancellations in last 30 days: 75% refund
    - 10+ cancellations in last 30 days: 50% refund (minimum)

    **Returns:**
    - 200: Job cancelled successfully with refund details
    - 400: Job cannot be cancelled (already completed/failed)
    - 404: Job not found
    """
    logger.info(f"User {current_user.id} cancelling job {job_id}")

    job, refund_amount, refund_percentage = cancel_job(
        db=db, user=current_user, job_id=job_id
    )

    message = (
        f"Job cancelled successfully. "
        f"Refunded {refund_amount} credits ({refund_percentage * 100:.0f}%)"
    )

    logger.info(
        f"Job {job_id} cancelled (refund: {refund_amount} credits, {refund_percentage * 100:.0f}%)"
    )

    return JobCancelResponse(
        job=JobResponse.model_validate(job),
        refund_amount=refund_amount,
        refund_percentage=refund_percentage,
        message=message,
    )


@router.post("/{job_id}/retry", response_model=JobRetryResponse, status_code=status.HTTP_201_CREATED)
async def retry_job_endpoint(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retry a failed job by creating a new job with the same workflow.

    This endpoint will:
    1. Verify the original job failed
    2. Check if user has sufficient credits
    3. Create a new job with the same workflow snapshot
    4. Deduct credits for the new job
    5. Queue the new job for execution

    **Returns:**
    - 201: New job created successfully
    - 400: Original job is not failed
    - 402: Insufficient credits for retry
    - 404: Original job not found
    """
    logger.info(f"User {current_user.id} retrying job {job_id}")

    new_job = retry_job(db=db, user=current_user, job_id=job_id)

    message = f"Job retried successfully. New job ID: {new_job.id}"

    logger.info(f"Job {job_id} retried as new job {new_job.id}")

    return JobRetryResponse(
        new_job=JobResponse.model_validate(new_job),
        original_job_id=job_id,
        message=message,
    )


# ============================================================
# Job Monitoring Endpoints
# ============================================================

@router.get("/{job_id}/logs", response_model=JobLogsResponse)
async def get_job_logs_endpoint(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get execution logs (node statuses) for a job.

    Returns detailed information about each node's execution status,
    including timing, errors, and output summaries.

    **Returns:**
    - 200: Job logs with node execution details
    - 404: Job not found
    """
    # Get job for authorization and metadata
    job = get_job_by_id(db=db, user=current_user, job_id=job_id)

    # Get job nodes
    nodes = get_job_logs(db=db, user=current_user, job_id=job_id)

    # Convert to response format
    node_responses = [JobNodeResponse.model_validate(node) for node in nodes]

    return JobLogsResponse(
        job_id=job_id,
        nodes=node_responses,
        overall_status=job.status.value,
        total_duration_seconds=job.duration_seconds,
    )


@router.get("/stats/summary", response_model=JobStatsResponse)
async def get_job_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get job statistics for the current user.

    Returns comprehensive statistics including:
    - Job counts by status
    - Total credits spent
    - Average job duration
    - Success rate

    **Returns:**
    - Job statistics summary
    """
    stats = get_job_stats(db=db, user=current_user)

    return JobStatsResponse(**stats)
