"""
CreditTransaction Model
IMMUTABLE ledger - source of truth for credit balances
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..types import JSONBType, UUIDType
from .enums import TransactionType

if TYPE_CHECKING:
    from .job import Job
    from .user import User


class CreditTransaction(Base):
    """
    IMMUTABLE ledger.
    Triggers prevent UPDATE/DELETE.
    Source of truth for credit balances.
    """
    
    __tablename__ = "credit_transactions"
    
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
    
    # Transaction amount (positive = add, negative = deduct)
    amount: Mapped[int] = mapped_column(nullable=False)
    
    # Balance snapshot after transaction (computed by trigger)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # Transaction type
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType),
        nullable=False,
    )
    
    # Related entities (SET NULL on deletion)
    related_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    related_purchase_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        nullable=True,
    )
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Additional metadata
    # Uses database-agnostic type: JSONB on PostgreSQL, JSON on SQLite
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONBType, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="credit_transactions",
    )
    related_job: Mapped[Optional["Job"]] = relationship(
        "Job",
        back_populates="credit_transactions",
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_credit_tx_user_id", "user_id"),
        Index("idx_credit_tx_type", "transaction_type"),
        Index("idx_credit_tx_job_id", "related_job_id"),
        Index("idx_credit_tx_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        sign = "+" if self.amount >= 0 else ""
        return f"<CreditTransaction {sign}{self.amount} type={self.transaction_type}>"
