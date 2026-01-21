"""
Job service layer - Business logic for job operations
"""

import uuid
from datetime import datetime, timedelta, UTC
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.enums import JobStatus, UserTier
from packages.database.models.job import Job
from packages.database.models.job_node import JobNode
from packages.database.models.user import User

from .db_helpers import get_workflow_snapshot


def create_job(
    db: Session,
    user: User,
    workflow_snapshot_id: uuid.UUID,
    priority: int = 0,
) -> Job:
    """
    Create a new job.

    Args:
        db: Database session
        user: Current user
        workflow_snapshot_id: ID of workflow snapshot to execute
        priority: Job priority (0-100)

    Returns:
        Created Job

    Raises:
        HTTPException:
            - 404 if workflow snapshot not found
            - 400 if invalid workflow
    """
    # Fetch and validate workflow snapshot
    snapshot = get_workflow_snapshot(db, workflow_snapshot_id, user.id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow snapshot {workflow_snapshot_id} not found or access denied",
        )

    try:
        # Create job record
        job = Job(
            user_id=user.id,
            workflow_snapshot_id=workflow_snapshot_id,
            status=JobStatus.PENDING,
            priority=priority,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Queue job for execution
        queue_job_execution(job, user.tier)

        return job

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}",
        )


def queue_job_execution(job: Job, user_tier: UserTier) -> None:
    """
    Queue job for execution in appropriate queue.

    Args:
        job: Job to queue
        user_tier: User's subscription tier
    """
    # Import here to avoid circular imports
    # Note: Celery integration removed for final year project demo
    # Jobs will be executed directly for now

    # Determine queue based on user tier (kept for future use)
    if user_tier in (UserTier.PRO, UserTier.ENTERPRISE):
        queue_name = "high_priority"
    else:
        queue_name = "normal"

    # Update job status to queued
    job.status = JobStatus.QUEUED


def get_jobs(
    db: Session,
    user: User,
    status_filter: Optional[JobStatus] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Job], int]:
    """
    Get paginated list of jobs for user.

    Args:
        db: Database session
        user: Current user
        status_filter: Optional status filter
        limit: Page size
        offset: Pagination offset

    Returns:
        Tuple of (jobs list, total count)
    """
    # Base query
    query = select(Job).where(Job.user_id == user.id)

    # Apply status filter
    if status_filter:
        query = query.where(Job.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar_one()

    # Apply ordering and pagination
    query = query.order_by(Job.created_at.desc()).limit(limit).offset(offset)

    # Execute query
    jobs = db.execute(query).scalars().all()

    return list(jobs), total


def get_job_by_id(
    db: Session,
    user: User,
    job_id: uuid.UUID,
) -> Job:
    """
    Get job by ID with authorization check.

    Args:
        db: Database session
        user: Current user
        job_id: Job UUID

    Returns:
        Job

    Raises:
        HTTPException: 404 if not found or unauthorized
    """
    job = db.get(Job, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    # Authorization check
    if job.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",  # Don't leak existence
        )

    return job


def cancel_job(
    db: Session,
    user: User,
    job_id: uuid.UUID,
) -> Tuple[Job, int, float]:
    """
    Cancel a job.

    Args:
        db: Database session
        user: Current user
        job_id: Job UUID

    Returns:
        Tuple of (updated job, 0, 0.0) - refund values kept for API compatibility

    Raises:
        HTTPException:
            - 404 if not found
            - 400 if job not cancellable
    """
    # Fetch job with authorization
    job = get_job_by_id(db, user, job_id)

    # Check if cancellable
    cancellable_statuses = [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING]
    if job.status not in cancellable_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job cannot be cancelled (status: {job.status})",
        )

    try:
        # Update job status
        job.status = JobStatus.CANCELLED
        if not job.started_at and not job.completed_at:
            job.completed_at = datetime.now(UTC)

        db.commit()
        db.refresh(job)

        # Return 0 for refund values since credits are removed
        return job, 0, 0.0

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}",
        )


def retry_job(
    db: Session,
    user: User,
    job_id: uuid.UUID,
) -> Job:
    """
    Retry a failed job by creating a new job.

    Args:
        db: Database session
        user: Current user
        job_id: Original job UUID

    Returns:
        New Job

    Raises:
        HTTPException:
            - 404 if not found
            - 400 if job not failed
    """
    # Fetch original job
    original_job = get_job_by_id(db, user, job_id)

    # Check if retryable
    if original_job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only failed jobs can be retried (current status: {original_job.status})",
        )

    # Check if workflow snapshot still exists
    if not original_job.workflow_snapshot_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot retry job: workflow snapshot no longer exists",
        )

    # Create new job
    new_job = create_job(
        db=db,
        user=user,
        workflow_snapshot_id=original_job.workflow_snapshot_id,
        priority=original_job.priority,
    )

    return new_job


def get_job_logs(
    db: Session,
    user: User,
    job_id: uuid.UUID,
) -> List[JobNode]:
    """
    Get execution logs (node statuses) for a job.

    Args:
        db: Database session
        user: Current user
        job_id: Job UUID

    Returns:
        List of JobNode records with execution details

    Raises:
        HTTPException: 404 if not found
    """
    # Fetch job with authorization
    job = get_job_by_id(db, user, job_id)

    # Fetch job nodes ordered by creation
    nodes = db.execute(
        select(JobNode)
        .where(JobNode.job_id == job.id)
        .order_by(JobNode.created_at.asc())
    ).scalars().all()

    return list(nodes)


def get_job_stats(db: Session, user: User) -> dict:
    """
    Get job statistics for user.

    Args:
        db: Database session
        user: Current user

    Returns:
        Dictionary with job statistics
    """
    # Count jobs by status
    stats = {
        "total_jobs": 0,
        "pending_jobs": 0,
        "running_jobs": 0,
        "completed_jobs": 0,
        "failed_jobs": 0,
        "cancelled_jobs": 0,
    }

    # Query job counts grouped by status
    results = db.execute(
        select(Job.status, func.count(Job.id))
        .where(Job.user_id == user.id)
        .group_by(Job.status)
    ).all()

    for job_status, count in results:
        stats["total_jobs"] += count
        if job_status == JobStatus.PENDING:
            stats["pending_jobs"] = count
        elif job_status == JobStatus.RUNNING:
            stats["running_jobs"] = count
        elif job_status == JobStatus.COMPLETED:
            stats["completed_jobs"] = count
        elif job_status == JobStatus.FAILED:
            stats["failed_jobs"] = count
        elif job_status == JobStatus.CANCELLED:
            stats["cancelled_jobs"] = count

    # Calculate average duration for completed jobs
    avg_duration_result = db.execute(
        select(func.avg(Job.duration_seconds))
        .where(
            and_(
                Job.user_id == user.id,
                Job.status == JobStatus.COMPLETED,
                Job.duration_seconds.isnot(None),
            )
        )
    ).scalar_one()
    stats["average_duration_seconds"] = (
        float(avg_duration_result) if avg_duration_result else None
    )

    # Calculate success rate
    completed_and_failed = stats["completed_jobs"] + stats["failed_jobs"]
    if completed_and_failed > 0:
        stats["success_rate"] = stats["completed_jobs"] / completed_and_failed
    else:
        stats["success_rate"] = None

    return stats
