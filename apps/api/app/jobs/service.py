"""
Job service layer - Business logic for job operations
"""

import uuid
from datetime import datetime, timedelta
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

from packages.database.models.enums import JobStatus, TransactionType, UserTier
from packages.database.models.job import Job
from packages.database.models.job_node import JobNode
from packages.database.models.user import User

from .cost_calculator import calculate_job_cost, calculate_refund_amount
from .db_helpers import (
    check_sufficient_credits,
    create_credit_transaction,
    get_workflow_snapshot,
)


def create_job(
    db: Session,
    user: User,
    workflow_snapshot_id: uuid.UUID,
    priority: int = 0,
) -> Job:
    """
    Create a new job with atomic credit deduction.

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
            - 402 if insufficient credits
            - 400 if invalid workflow
    """
    # Fetch and validate workflow snapshot
    snapshot = get_workflow_snapshot(db, workflow_snapshot_id, user.id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow snapshot {workflow_snapshot_id} not found or access denied",
        )

    # Calculate job cost
    try:
        credits_cost = calculate_job_cost(snapshot.graph_json)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid workflow: {str(e)}",
        )

    # Check sufficient credits
    has_sufficient, current_balance = check_sufficient_credits(
        db, user.id, credits_cost
    )
    if not has_sufficient:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {credits_cost}, Available: {current_balance}",
        )

    # Start database transaction for atomic job creation + credit deduction
    try:
        # Create job record
        job = Job(
            user_id=user.id,
            workflow_snapshot_id=workflow_snapshot_id,
            status=JobStatus.PENDING,
            priority=priority,
            credits_cost=credits_cost,
        )
        db.add(job)
        db.flush()  # Get job ID

        # Deduct credits
        create_credit_transaction(
            db=db,
            user_id=user.id,
            amount=-credits_cost,
            transaction_type=TransactionType.CONSUMPTION,
            related_job_id=job.id,
            description=f"Job execution cost for job {job.id}",
            metadata={"workflow_snapshot_id": str(workflow_snapshot_id)},
        )

        # Commit both operations atomically
        db.commit()
        db.refresh(job)

        # Queue Celery task
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
    Queue job for execution in appropriate Celery queue.

    Args:
        job: Job to queue
        user_tier: User's subscription tier
    """
    # Import here to avoid circular imports
    from worker.tasks.job_execution_task import execute_job

    # Determine queue based on user tier
    if user_tier in (UserTier.PRO, UserTier.ENTERPRISE):
        queue_name = "high_priority"
    else:
        queue_name = "normal"

    # Queue Celery task
    task = execute_job.apply_async(
        args=[str(job.id)],
        queue=queue_name,
        priority=job.priority,
    )

    # Store task ID (will be saved when job is committed)
    job.celery_task_id = task.id
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
    Cancel a job and issue refund with penalty.

    Args:
        db: Database session
        user: Current user
        job_id: Job UUID

    Returns:
        Tuple of (updated job, refund_amount, refund_percentage)

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

    # Calculate user's cancellation count in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    cancellation_count = db.execute(
        select(func.count())
        .select_from(Job)
        .where(
            and_(
                Job.user_id == user.id,
                Job.status == JobStatus.CANCELLED,
                Job.created_at >= thirty_days_ago,
            )
        )
    ).scalar_one()

    # Calculate refund with penalty
    refund_amount, refund_percentage = calculate_refund_amount(
        job.credits_cost, cancellation_count
    )

    try:
        # Revoke Celery task if running
        if job.celery_task_id:
            revoke_celery_task(job.celery_task_id)

        # Update job status
        job.status = JobStatus.CANCELLED
        if not job.started_at and not job.completed_at:
            job.completed_at = datetime.utcnow()

        # Issue refund
        if refund_amount > 0:
            create_credit_transaction(
                db=db,
                user_id=user.id,
                amount=refund_amount,
                transaction_type=TransactionType.REFUND,
                related_job_id=job.id,
                description=f"Refund for cancelled job {job.id} ({refund_percentage * 100:.0f}%)",
                metadata={
                    "original_cost": job.credits_cost,
                    "refund_percentage": refund_percentage,
                    "cancellation_count_30d": cancellation_count,
                },
            )

        db.commit()
        db.refresh(job)

        return job, refund_amount, refund_percentage

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel job: {str(e)}",
        )


def revoke_celery_task(task_id: str) -> None:
    """
    Revoke a running Celery task.

    Args:
        task_id: Celery task ID
    """
    # Import here to avoid circular imports
    from worker.celery_app import celery_app

    # Revoke task with terminate flag
    # This will kill the worker process if the task is currently executing
    celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')


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
            - 402 if insufficient credits
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

    # Create new job (this will check credits and deduct automatically)
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

    # Calculate total credits spent
    total_spent_result = db.execute(
        select(func.coalesce(func.sum(Job.credits_cost), 0))
        .where(
            and_(
                Job.user_id == user.id,
                Job.status.in_([JobStatus.COMPLETED, JobStatus.RUNNING]),
            )
        )
    ).scalar_one()
    stats["total_credits_spent"] = int(total_spent_result)

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
