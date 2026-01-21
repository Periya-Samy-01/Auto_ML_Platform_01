"""
JobNode Model
Individual node execution records within a job
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType
from .enums import NodeStatus, NodeType

if TYPE_CHECKING:
    from .job import Job
    from .model import Model


class JobNode(Base):
    """
    Individual node execution records within a job.
    Used for progress tracking and debugging.
    """
    
    __tablename__ = "job_nodes"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Parent job
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Node identifier (from workflow graph)
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Node type
    node_type: Mapped[NodeType] = mapped_column(
        Enum(NodeType),
        nullable=False,
    )
    
    # Status
    status: Mapped[NodeStatus] = mapped_column(
        Enum(NodeStatus),
        nullable=False,
        default=NodeStatus.PENDING,
    )
    
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
    
    # Progress tracking
    progress_percentage: Mapped[Optional[int]] = mapped_column(nullable=True)
    progress_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Results (dataframe paths, metrics, artifact URLs, etc.)
    # Uses database-agnostic type: JSONB on PostgreSQL, JSON on SQLite
    result_json: Mapped[Optional[dict]] = mapped_column(JSONBType, nullable=True)
    
    # Error info
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="nodes")
    model: Mapped[Optional["Model"]] = relationship(
        "Model",
        back_populates="job_node",
        uselist=False,
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("job_id", "node_id", name="ux_jobnode_jobid_nodeid"),
        Index("idx_job_nodes_job_id", "job_id"),
        Index("idx_job_nodes_status", "status"),
        CheckConstraint("duration_seconds >= 0", name="ck_job_nodes_duration"),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_job_nodes_progress",
        ),
    )
    
    def __repr__(self) -> str:
        return f"<JobNode {self.node_id} status={self.status}>"
