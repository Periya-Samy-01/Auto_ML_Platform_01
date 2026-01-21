"""
WorkflowSnapshot Model
IMMUTABLE snapshots created when user clicks "Run"
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType

if TYPE_CHECKING:
    from .job import Job
    from .user import User
    from .workflow import Workflow


class WorkflowSnapshot(Base):
    """
    IMMUTABLE snapshots created when user clicks "Run".
    Jobs reference snapshots to ensure reproducibility.
    NEVER modify graph_json after creation.
    """
    
    __tablename__ = "workflow_snapshots"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # References
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Frozen copy of workflow at execution time (IMMUTABLE)
    graph_json: Mapped[dict] = mapped_column(JSONBType, nullable=False)
    
    # Optional name for this snapshot
    snapshot_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    workflow: Mapped["Workflow"] = relationship(
        "Workflow",
        back_populates="snapshots",
    )
    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="workflow_snapshot",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_workflow_snapshots_workflow_id", "workflow_id"),
        Index("idx_workflow_snapshots_user_id", "user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<WorkflowSnapshot {self.id}>"
