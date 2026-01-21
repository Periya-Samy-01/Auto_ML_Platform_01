"""
Model (TrainedModel) Model
Trained model artifacts
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType

if TYPE_CHECKING:
    from .dataset import Dataset
    from .experiment_run import ExperimentRun
    from .job import Job
    from .job_node import JobNode
    from .user import User


class Model(Base):
    """
    Trained model artifacts.
    Preserved even if source job/dataset deleted (SET NULL).
    """
    
    __tablename__ = "models"
    
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
    
    # Source (SET NULL on deletion to preserve model)
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("job_nodes.id", ondelete="SET NULL"),
        nullable=True,
    )
    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Model lineage (for versioning)
    parent_model_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("models.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Basic info
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Production flag
    is_production: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    # Storage
    s3_model_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )
    
    # Results
    metrics_json: Mapped[Optional[dict]] = mapped_column(JSONBType, nullable=True)
    hyperparameters_json: Mapped[Optional[dict]] = mapped_column(
        JSONBType,
        nullable=True,
    )
    shap_plots_s3_paths: Mapped[Optional[dict]] = mapped_column(
        JSONBType,
        nullable=True,
    )
    
    # MLflow integration
    mlflow_run_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Flags
    is_saved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="models")
    job: Mapped[Optional["Job"]] = relationship(
        "Job",
        back_populates="models",
        foreign_keys=[job_id],
    )
    job_node: Mapped[Optional["JobNode"]] = relationship(
        "JobNode",
        back_populates="model",
    )
    dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset",
        back_populates="models",
        foreign_keys=[dataset_id],
    )
    parent_model: Mapped[Optional["Model"]] = relationship(
        "Model",
        remote_side=[id],
        backref="child_models",
    )
    experiment_runs: Mapped[List["ExperimentRun"]] = relationship(
        "ExperimentRun",
        back_populates="model",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_models_user_id", "user_id"),
        Index("idx_models_job_id", "job_id"),
        Index("idx_models_dataset_id", "dataset_id"),
        Index("idx_models_parent_model_id", "parent_model_id"),
        Index("idx_models_name", "name"),
        Index("idx_models_is_production", "is_production"),
        Index("idx_models_created_at", "created_at"),
        CheckConstraint("model_size_bytes >= 0", name="ck_models_size"),
    )
    
    def __repr__(self) -> str:
        return f"<Model {self.name or self.id}>"
