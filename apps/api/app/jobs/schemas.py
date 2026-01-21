"""
Job Schemas
Pydantic models for job requests and responses
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Job Request Schemas
# ============================================================

class JobCreate(BaseModel):
    """Request to create a new job"""
    workflow_snapshot_id: uuid.UUID = Field(
        ...,
        description="ID of the workflow snapshot to execute"
    )
    priority: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Job priority (0-100, higher = more urgent)"
    )


# ============================================================
# Job Response Schemas
# ============================================================

class JobResponse(BaseModel):
    """Job response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    workflow_snapshot_id: Optional[uuid.UUID] = None
    status: str
    priority: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    celery_task_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobBrief(BaseModel):
    """Brief job info (for lists)"""
    id: uuid.UUID
    status: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Paginated list of jobs"""
    items: List[JobBrief]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================
# Job Node Schemas
# ============================================================

class JobNodeResponse(BaseModel):
    """Job node execution status"""
    id: uuid.UUID
    node_id: str
    node_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    output_summary: Optional[dict] = None

    model_config = {"from_attributes": True}


class JobLogsResponse(BaseModel):
    """Job execution logs"""
    job_id: uuid.UUID
    nodes: List[JobNodeResponse]
    overall_status: str
    total_duration_seconds: Optional[int] = None


# ============================================================
# Job Action Response Schemas
# ============================================================

class JobCancelResponse(BaseModel):
    """Response after cancelling a job"""
    job: JobResponse
    message: str


class JobRetryResponse(BaseModel):
    """Response after retrying a job"""
    new_job: JobResponse
    original_job_id: uuid.UUID
    message: str


# ============================================================
# Job Statistics Schemas
# ============================================================

class JobStatsResponse(BaseModel):
    """Job statistics for a user"""
    total_jobs: int
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    cancelled_jobs: int
    average_duration_seconds: Optional[float] = None
    success_rate: Optional[float] = None
