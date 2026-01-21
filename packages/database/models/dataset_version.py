"""
Dataset Version Model
Immutable versions of datasets with parquet storage (aligned with architecture doc)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType
from .enums import FileFormat, ProcessingStatus

if TYPE_CHECKING:
    from .dataset import Dataset
    from .dataset_profile import DatasetProfile
    from .ingestion_job import IngestionJob


class DatasetVersion(Base):
    """
    Immutable dataset versions. Each row points to a Parquet file in R2.
    This is the SINGLE SOURCE OF TRUTH for all file-specific metadata.
    """
    
    __tablename__ = "dataset_versions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Parent dataset
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Version metadata
    version_number: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
    )
    
    # File storage (Parquet in R2)
    s3_path: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="Path in R2: datasets/<user_id>/<version_id>.parquet"
    )
    
    # Original file information
    original_filename: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    original_format: Mapped[FileFormat] = mapped_column(
        Enum(FileFormat, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    
    # Size metrics
    original_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )
    parquet_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )
    
    # Data shape (NULL until processing completes)
    row_count: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )
    column_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    
    # Schema (structural information only - stats go in dataset_profiles)
    columns_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONBType,
        nullable=True,
        comment="Structural schema only: {columns: [{name, dtype, null_count}]}"
    )
    
    # Processing state
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProcessingStatus.PENDING,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", 
        back_populates="versions",
        foreign_keys=[dataset_id],
    )
    
    profile: Mapped[Optional["DatasetProfile"]] = relationship(
        "DatasetProfile",
        back_populates="dataset_version",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    ingestion_job: Mapped[Optional["IngestionJob"]] = relationship(
        "IngestionJob",
        back_populates="dataset_version",
        uselist=False,
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number", name="ux_dataset_version_number"),
        Index("idx_dataset_versions_dataset_id", "dataset_id"),
        Index("idx_dataset_versions_status", "processing_status"),
        Index("idx_dataset_versions_created_at", "created_at"),
        CheckConstraint(
            "original_size_bytes IS NULL OR original_size_bytes >= 0",
            name="ck_dataset_versions_original_size",
        ),
        CheckConstraint(
            "parquet_size_bytes IS NULL OR parquet_size_bytes >= 0",
            name="ck_dataset_versions_parquet_size",
        ),
        CheckConstraint(
            "row_count IS NULL OR row_count >= 0", 
            name="ck_dataset_versions_row_count"
        ),
        CheckConstraint(
            "column_count IS NULL OR column_count >= 0", 
            name="ck_dataset_versions_column_count"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<DatasetVersion {self.dataset_id}:v{self.version_number}>"
