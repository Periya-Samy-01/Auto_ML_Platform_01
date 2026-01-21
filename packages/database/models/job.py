"""
Job Model
Training job execution records
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import UUIDType
from .enums import JobStatus

if TYPE_CHECKING:
    from .experiment_run import ExperimentRun
    from .job_node import JobNode
    from .model import Model
    from .user import User
    from .workflow_snapshot import WorkflowSnapshot


class Job(Base):
    """
    Training job execution records.
    References immutable workflow_snapshot for reproducibility.
    """
    
    __tablename__ = "jobs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Owner
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Reference to workflow (SET NULL on deletion to preserve history)
    workflow_snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("workflow_snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Status
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        nullable=False,
        default=JobStatus.PENDING,
    )
    
    # Priority (higher = more urgent)
    priority: Mapped[int] = mapped_column(nullable=False, default=0)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Error info
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Celery integration
    celery_task_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    workflow_snapshot: Mapped[Optional["WorkflowSnapshot"]] = relationship(
        "WorkflowSnapshot",
        back_populates="jobs",
    )
    nodes: Mapped[List["JobNode"]] = relationship(
        "JobNode",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    models: Mapped[List["Model"]] = relationship(
        "Model",
        back_populates="job",
        foreign_keys="Model.job_id",
    )
    experiment_runs: Mapped[List["ExperimentRun"]] = relationship(
        "ExperimentRun",
        back_populates="job",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_jobs_user_id", "user_id"),
        Index("idx_jobs_workflow_snapshot_id", "workflow_snapshot_id"),
        Index("idx_jobs_celery_task_id", "celery_task_id"),
        # CRITICAL: Powers job queue scheduling
        Index(
            "idx_jobs_queue",
            "status",
            "priority",
            "created_at",
        ),
        CheckConstraint("priority >= 0", name="ck_jobs_priority"),
        CheckConstraint("duration_seconds >= 0", name="ck_jobs_duration"),
    )
    
    def __repr__(self) -> str:
        return f"<Job {self.id} status={self.status}>"
