"""
Dataset Model
Logical container for dataset versions (aligned with architecture doc)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
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
from ..types import UUIDType
from .enums import ProblemType

if TYPE_CHECKING:
    from .dataset_version import DatasetVersion
    from .experiment import Experiment
    from .ingestion_job import IngestionJob
    from .model import Model
    from .user import User


class Dataset(Base):
    """
    Dataset container - logical grouping of dataset versions.
    Files stored in R2, metadata stored here.
    This table does NOT store file-specific information.
    """
    
    __tablename__ = "datasets"
    
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
    
    # Sample dataset flag
    is_sample_dataset: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # ML configuration (user-defined at dataset level)
    problem_type: Mapped[Optional[ProblemType]] = mapped_column(
        Enum(ProblemType),
        nullable=True,
    )
    target_column: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Current version tracking (FK to dataset_versions)
    current_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("dataset_versions.id", ondelete="SET NULL"),
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
    user: Mapped["User"] = relationship("User", back_populates="datasets")
    
    versions: Mapped[List["DatasetVersion"]] = relationship(
        "DatasetVersion",
        back_populates="dataset",
        cascade="all, delete-orphan",
        foreign_keys="DatasetVersion.dataset_id",
        order_by="DatasetVersion.version_number.desc()",
    )
    
    current_version: Mapped[Optional["DatasetVersion"]] = relationship(
        "DatasetVersion",
        foreign_keys=[current_version_id],
        post_update=True,  # Avoid circular dependency
    )
    
    experiments: Mapped[List["Experiment"]] = relationship(
        "Experiment",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    
    ingestion_jobs: Mapped[List["IngestionJob"]] = relationship(
        "IngestionJob",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    models: Mapped[List["Model"]] = relationship(
        "Model",
        back_populates="dataset",
        foreign_keys="Model.dataset_id",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="ux_datasets_userid_name"),
        Index("idx_datasets_user_id", "user_id"),
        Index("idx_datasets_created_at", "created_at"),
        Index("idx_datasets_current_version", "current_version_id"),
        Index("idx_datasets_problem_type", "problem_type"),
    )
    
    def __repr__(self) -> str:
        return f"<Dataset {self.name}>"
