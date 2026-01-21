"""
Experiment Model
User-created experiment groups for comparing runs
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import UUIDType

if TYPE_CHECKING:
    from .dataset import Dataset
    from .experiment_run import ExperimentRun
    from .user import User


class Experiment(Base):
    """
    User-created experiment groups for comparing runs on same dataset.
    """
    
    __tablename__ = "experiments"
    
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
    
    # Dataset
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
    user: Mapped["User"] = relationship("User", back_populates="experiments")
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="experiments",
    )
    runs: Mapped[List["ExperimentRun"]] = relationship(
        "ExperimentRun",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_experiments_user_id", "user_id"),
        Index("idx_experiments_dataset_id", "dataset_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Experiment {self.name}>"
