"""
Dataset Profile Model
Statistical profiles computed during ingestion (aligned with architecture doc)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType

if TYPE_CHECKING:
    from .dataset_version import DatasetVersion


class DatasetProfile(Base):
    """
    Statistical profiles computed during ingestion.
    Contains column-level statistics and metadata.
    
    Structure matches architecture doc:
    {
      "row_count": 1000,
      "columns": [
        {
          "name": "age",
          "dtype": "int64",
          "stats": {
            "null_count": 5,
            "unique_count": 45,
            "min": 18, "max": 90,
            "mean": 42.5, "median": 40, "std": 15.2,
            "sample_values": [25, 30, 35, 40, 45]
          }
        },
        {
          "name": "category",
          "dtype": "object",
          "stats": {
            "null_count": 0,
            "unique_count": 3,
            "top_values": [
              {"value": "A", "count": 500},
              {"value": "B", "count": 300}
            ],
            "sample_values": ["A", "B", "C"]
          }
        }
      ]
    }
    """
    
    __tablename__ = "dataset_profiles"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Reference to version (note: dataset_version_id not version_id)
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Profile data (note: profile_data not profile_json)
    profile_data: Mapped[dict] = mapped_column(
        JSONBType,
        nullable=False,
        comment="Statistical profile following architecture doc format"
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    dataset_version: Mapped["DatasetVersion"] = relationship(
        "DatasetVersion",
        back_populates="profile"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("dataset_version_id", name="ux_profile_dataset_version"),
        Index("idx_profiles_dataset_version_id", "dataset_version_id"),
    )
    
    def __repr__(self) -> str:
        return f"<DatasetProfile version_id={self.dataset_version_id}>"
