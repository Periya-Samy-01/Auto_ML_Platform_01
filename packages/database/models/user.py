"""
User Model
Core user account with soft-delete support
"""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import UUIDType
from .enums import OAuthProvider, UserTier

if TYPE_CHECKING:
    from .dataset import Dataset
    from .experiment import Experiment
    from .ingestion_job import IngestionJob
    from .job import Job
    from .model import Model
    from .tutorial import Tutorial
    from .user_tutorial_progress import UserTutorialProgress
    from .workflow import Workflow


class User(Base):
    """
    User accounts with soft-delete support.
    Hard delete after 30-day grace period triggers CASCADE to all user data.
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Authentication
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # OAuth fields
    oauth_provider: Mapped[Optional[OAuthProvider]] = mapped_column(
        Enum(OAuthProvider),
        nullable=True,
    )
    oauth_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    # Subscription
    tier: Mapped[UserTier] = mapped_column(
        Enum(UserTier),
        nullable=False,
        default=UserTier.FREE,
    )
    
    # Engagement
    streak_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )
    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Usage tracking (maintained by triggers)
    storage_used_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    dataset_count: Mapped[int] = mapped_column(nullable=False, default=0)
    workflow_count: Mapped[int] = mapped_column(nullable=False, default=0)
    model_count: Mapped[int] = mapped_column(nullable=False, default=0)
    
    # Status
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
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
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    models: Mapped[List["Model"]] = relationship(
        "Model",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    ingestion_jobs: Mapped[List["IngestionJob"]] = relationship(
        "IngestionJob",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    tutorials_created: Mapped[List["Tutorial"]] = relationship(
        "Tutorial",
        back_populates="created_by",
        foreign_keys="Tutorial.created_by_user_id",
    )
    tutorial_progress: Mapped[List["UserTutorialProgress"]] = relationship(
        "UserTutorialProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_users_tier", "tier"),
        Index("idx_users_created_at", "created_at"),
        Index("idx_users_oauth", "oauth_provider", "oauth_id"),
        CheckConstraint("streak_count >= 0", name="ck_users_streak_count"),
        CheckConstraint("storage_used_bytes >= 0", name="ck_users_storage"),
        CheckConstraint("dataset_count >= 0", name="ck_users_dataset_count"),
        CheckConstraint("workflow_count >= 0", name="ck_users_workflow_count"),
        CheckConstraint("model_count >= 0", name="ck_users_model_count"),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
