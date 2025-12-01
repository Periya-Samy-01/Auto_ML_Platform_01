"""
Business logic for credit management
"""

import os
import uuid
from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.credit_transaction import CreditTransaction
from packages.database.models.enums import TransactionType
from app.jobs.db_helpers import get_user_credit_balance, create_credit_transaction


def get_user_balance(db: Session, user_id: uuid.UUID) -> Dict[str, Any]:
    """
    Get user's credit balance with additional metadata.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Dictionary with balance, total_earned, total_spent, transaction_count
    """
    # Get current balance
    balance = get_user_credit_balance(db, user_id)

    # Calculate total earned (PURCHASE + REFUND)
    total_earned_result = db.execute(
        select(func.coalesce(func.sum(CreditTransaction.amount), 0))
        .where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.amount > 0  # Only positive amounts
        )
    ).scalar_one()
    total_earned = int(total_earned_result)

    # Calculate total spent (CONSUMPTION - negative amounts)
    total_spent_result = db.execute(
        select(func.coalesce(func.sum(CreditTransaction.amount), 0))
        .where(
            CreditTransaction.user_id == user_id,
            CreditTransaction.amount < 0  # Only negative amounts
        )
    ).scalar_one()
    total_spent = abs(int(total_spent_result))  # Convert to positive for display

    # Get transaction count
    transaction_count = db.execute(
        select(func.count())
        .select_from(CreditTransaction)
        .where(CreditTransaction.user_id == user_id)
    ).scalar_one()

    return {
        "balance": balance,
        "total_earned": total_earned,
        "total_spent": total_spent,
        "transaction_count": transaction_count,
    }


def get_user_transactions(
    db: Session,
    user_id: uuid.UUID,
    page: int,
    page_size: int,
) -> Dict[str, Any]:
    """
    Get paginated list of user's credit transactions.

    Args:
        db: Database session
        user_id: User UUID
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Dictionary with items, total, page, page_size, has_more
    """
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    total = db.execute(
        select(func.count())
        .select_from(CreditTransaction)
        .where(CreditTransaction.user_id == user_id)
    ).scalar_one()

    # Get transactions (ordered by created_at DESC - most recent first)
    query = (
        select(CreditTransaction)
        .where(CreditTransaction.user_id == user_id)
        .order_by(CreditTransaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    transactions = db.execute(query).scalars().all()

    # Calculate has_more
    has_more = total > (page * page_size)

    return {
        "items": transactions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
    }


def create_mock_purchase(
    db: Session,
    user_id: uuid.UUID,
    amount: int,
    description: str,
) -> CreditTransaction:
    """
    Create a mock credit purchase (for development/testing only).

    Args:
        db: Database session
        user_id: User UUID
        amount: Number of credits to purchase (must be positive)
        description: Transaction description

    Returns:
        Created CreditTransaction

    Raises:
        HTTPException 403: If mock purchases are disabled
        HTTPException 400: If amount is invalid
    """
    # Check environment variable
    allow_mock_purchases = os.getenv("ALLOW_MOCK_PURCHASES", "false").lower() == "true"

    if not allow_mock_purchases:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mock purchases are disabled. Set ALLOW_MOCK_PURCHASES=true to enable."
        )

    # Validate amount
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )

    # Create transaction
    transaction = create_credit_transaction(
        db=db,
        user_id=user_id,
        amount=amount,
        transaction_type=TransactionType.PURCHASE,
        description=description or "Mock credit purchase",
    )

    db.commit()
    db.refresh(transaction)

    return transaction
