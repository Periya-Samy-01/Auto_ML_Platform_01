"""
Pydantic schemas for credit endpoints
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.enums import TransactionType


class CreditBalanceResponse(BaseModel):
    """Response for GET /api/credits/balance"""

    balance: int = Field(..., description="Current credit balance")
    total_earned: int = Field(..., description="Total credits earned (purchases + refunds)")
    total_spent: int = Field(..., description="Total credits spent (consumption)")
    transaction_count: int = Field(..., description="Total number of transactions")

    model_config = {"from_attributes": True}


class CreditTransactionResponse(BaseModel):
    """Response for single credit transaction"""

    id: uuid.UUID = Field(..., description="Transaction ID")
    amount: int = Field(..., description="Transaction amount (positive = add, negative = deduct)")
    balance_after: int = Field(..., description="Balance after this transaction")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    related_job_id: Optional[uuid.UUID] = Field(None, description="Related job ID if applicable")
    description: Optional[str] = Field(None, description="Transaction description")
    created_at: datetime = Field(..., description="Transaction timestamp")

    model_config = {"from_attributes": True}


class CreditTransactionListResponse(BaseModel):
    """Paginated list of credit transactions"""

    items: List[CreditTransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more pages")

    model_config = {"from_attributes": True}


class MockPurchaseRequest(BaseModel):
    """Request body for POST /api/credits/mock-purchase"""

    amount: int = Field(..., description="Number of credits to purchase", gt=0)
    description: Optional[str] = Field(
        "Mock credit purchase",
        description="Optional description for the transaction"
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        """Validate amount is positive"""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class MockPurchaseResponse(BaseModel):
    """Response for POST /api/credits/mock-purchase"""

    transaction_id: uuid.UUID = Field(..., description="Created transaction ID")
    amount: int = Field(..., description="Credits purchased")
    balance_after: int = Field(..., description="Balance after purchase")
    description: str = Field(..., description="Transaction description")
    created_at: datetime = Field(..., description="Transaction timestamp")
    message: str = Field(..., description="Success message")

    model_config = {"from_attributes": True}
