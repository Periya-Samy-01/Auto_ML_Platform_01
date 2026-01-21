"""
Workflow Model
User editable workflow projects (canvas graphs)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType

if TYPE_CHECKING:
    from .user import User
    from .workflow_snapshot import WorkflowSnapshot


class Workflow(Base):
    """
    User editable workflow projects (canvas graphs).
    Mutable - users can modify freely.
    """
    
    __tablename__ = "workflows"
    
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
    
    # Basic info
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Graph data (React Flow format: {nodes: [], edges: []})
    graph_json: Mapped[Optional[dict]] = mapped_column(JSONBType, nullable=True)
    
    # UI
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    last_modified: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="workflows")
    snapshots: Mapped[List["WorkflowSnapshot"]] = relationship(
        "WorkflowSnapshot",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_workflows_user_id", "user_id"),
        Index("idx_workflows_last_modified", "last_modified"),
    )
    
    def __repr__(self) -> str:
        return f"<Workflow {self.name}>"
