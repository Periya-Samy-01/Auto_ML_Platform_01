"""
UserTutorialProgress Model
Tracks user progress through tutorials
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import ArrayOfIntegers, UUIDType

if TYPE_CHECKING:
    from .tutorial import Tutorial
    from .user import User


class UserTutorialProgress(Base):
    """
    Tracks user progress through tutorials.
    Unique per user-tutorial pair.
    """
    
    __tablename__ = "user_tutorial_progress"
    
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
    tutorial_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("tutorials.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Progress tracking
    current_step_index: Mapped[int] = mapped_column(nullable=False, default=0)
    # Uses database-agnostic type: ARRAY(Integer) on PostgreSQL, JSON on SQLite
    completed_steps: Mapped[List[int]] = mapped_column(
        ArrayOfIntegers,
        nullable=False,
        default=list,
    )
    
    # Completion status
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    completion_percentage: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Timestamps
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tutorial_progress",
    )
    tutorial: Mapped["Tutorial"] = relationship(
        "Tutorial",
        back_populates="progress_records",
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "tutorial_id", name="ux_user_tutorial"),
        Index("idx_user_tutorial_progress_user_id", "user_id"),
        Index("idx_user_tutorial_progress_tutorial_id", "tutorial_id"),
        Index("idx_user_tutorial_progress_last_accessed", "last_accessed_at"),
        CheckConstraint(
            "current_step_index >= 0",
            name="ck_user_tutorial_progress_step",
        ),
        CheckConstraint(
            "completion_percentage >= 0 AND completion_percentage <= 100",
            name="ck_user_tutorial_progress_percentage",
        ),
    )
    
    def __repr__(self) -> str:
        return f"<UserTutorialProgress user={self.user_id} tutorial={self.tutorial_id}>"
