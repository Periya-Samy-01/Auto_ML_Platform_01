"""
CreditPackage Model
Pricing configuration for credit purchases
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Numeric,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from ..types import UUIDType
from .enums import CreditTierRestriction


class CreditPackage(Base):
    """
    Pricing configuration for credit purchases.
    Admin-managed.
    """
    
    __tablename__ = "credit_packages"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Package info
    name: Mapped[str] = mapped_column(Text, nullable=False)
    credits: Mapped[int] = mapped_column(nullable=False)
    price_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    
    # Access restriction
    tier_restriction: Mapped[CreditTierRestriction] = mapped_column(
        Enum(CreditTierRestriction),
        nullable=False,
        default=CreditTierRestriction.NONE,
    )
    
    # Flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    
    # Display order
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
    # Constraints
    __table_args__ = (
        Index("idx_credit_packages_active", "is_active"),
        CheckConstraint("credits >= 0", name="ck_credit_packages_credits"),
        CheckConstraint("price_usd >= 0", name="ck_credit_packages_price"),
    )
    
    def __repr__(self) -> str:
        return f"<CreditPackage {self.name} ({self.credits} credits)>"
