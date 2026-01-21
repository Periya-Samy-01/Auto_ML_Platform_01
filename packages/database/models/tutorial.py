"""
Tutorial Model
Interactive learning content
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
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
from ..types import ArrayOfStrings, JSONBType, UUIDType
from .enums import TutorialDifficulty

if TYPE_CHECKING:
    from .user import User
    from .user_tutorial_progress import UserTutorialProgress


class Tutorial(Base):
    """
    Interactive learning content.
    Platform tutorials survive tutor deletion (SET NULL).
    """
    
    __tablename__ = "tutorials"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Creator (SET NULL on deletion to preserve tutorial)
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Basic info
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Difficulty
    difficulty: Mapped[Optional[TutorialDifficulty]] = mapped_column(
        Enum(TutorialDifficulty),
        nullable=True,
    )
    
    # Duration
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Content (structured steps: {steps: [{type, content, action}, ...]})
    # Uses database-agnostic type: JSONB on PostgreSQL, JSON on SQLite
    content_json: Mapped[Optional[dict]] = mapped_column(JSONBType, nullable=True)
    
    # Tags
    # Uses database-agnostic type: ARRAY(Text) on PostgreSQL, JSON on SQLite
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ArrayOfStrings,
        nullable=True,
    )
    
    # Flags
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    # Stats
    enrollment_count: Mapped[int] = mapped_column(nullable=False, default=0)
    completion_count: Mapped[int] = mapped_column(nullable=False, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Relationships
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="tutorials_created",
        foreign_keys=[created_by_user_id],
    )
    progress_records: Mapped[List["UserTutorialProgress"]] = relationship(
        "UserTutorialProgress",
        back_populates="tutorial",
        cascade="all, delete-orphan",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_tutorials_author", "created_by_user_id"),
        Index("idx_tutorials_difficulty", "difficulty"),
        Index("idx_tutorials_is_published", "is_published"),
        Index("idx_tutorials_is_featured", "is_featured"),
        CheckConstraint(
            "estimated_duration_minutes >= 0",
            name="ck_tutorials_duration",
        ),
        CheckConstraint(
            "enrollment_count >= 0",
            name="ck_tutorials_enrollment",
        ),
        CheckConstraint(
            "completion_count >= 0",
            name="ck_tutorials_completion",
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Tutorial {self.title}>"
