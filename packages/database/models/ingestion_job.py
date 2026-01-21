"""
Ingestion Job Model
Tracks async dataset processing jobs (aligned with architecture doc)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import UUIDType

if TYPE_CHECKING:
    from .dataset import Dataset
    from .dataset_version import DatasetVersion
    from .user import User


class IngestionJob(Base):
    """
    Tracks async dataset processing jobs. Source of truth for job status.
    """
    
    __tablename__ = "ingestion_jobs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # References
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("dataset_versions.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to dataset_versions (not version_id for consistency)"
    )
    
    # Upload info
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        nullable=False,
    )  # Tracks temp file in R2
    original_filename: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    original_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    
    # Job state
    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="pending",
    )  # pending | processing | completed | failed
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    error_traceback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Task tracking
    celery_task_id: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="ingestion_jobs"
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="ingestion_jobs"
    )
    dataset_version: Mapped[Optional["DatasetVersion"]] = relationship(
        "DatasetVersion",
        back_populates="ingestion_job"
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_ingestion_jobs_user_id", "user_id"),
        Index("idx_ingestion_jobs_dataset_id", "dataset_id"),
        Index("idx_ingestion_jobs_dataset_version_id", "dataset_version_id"),
        Index("idx_ingestion_jobs_status", "status"),
        Index("idx_ingestion_jobs_created_at", "created_at"),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="chk_ingestion_status",
        ),
        CheckConstraint(
            "original_size_bytes >= 0",
            name="ck_ingestion_jobs_size",
        ),
        CheckConstraint(
            "retry_count >= 0",
            name="ck_ingestion_jobs_retry",
        ),
    )
    
    def __repr__(self) -> str:
        return f"<IngestionJob {self.id} status={self.status}>"
