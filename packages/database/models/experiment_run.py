"""
ExperimentRun Model
Links jobs/models to experiment groups
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import UUIDType

if TYPE_CHECKING:
    from .experiment import Experiment
    from .job import Job
    from .model import Model


class ExperimentRun(Base):
    """
    Links jobs/models to experiment groups.
    Jobs and models preserved if deleted (SET NULL).
    """
    
    __tablename__ = "experiment_runs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Parent experiment
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Linked entities (SET NULL on deletion)
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    model_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("models.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    experiment: Mapped["Experiment"] = relationship(
        "Experiment",
        back_populates="runs",
    )
    job: Mapped[Optional["Job"]] = relationship(
        "Job",
        back_populates="experiment_runs",
    )
    model: Mapped[Optional["Model"]] = relationship(
        "Model",
        back_populates="experiment_runs",
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "experiment_id",
            "job_id",
            name="ux_experiment_runs_experiment_job",
        ),
        Index("idx_experiment_runs_experiment_id", "experiment_id"),
        Index("idx_experiment_runs_job_id", "job_id"),
        Index("idx_experiment_runs_model_id", "model_id"),
    )
    
    def __repr__(self) -> str:
        return f"<ExperimentRun experiment={self.experiment_id}>"
