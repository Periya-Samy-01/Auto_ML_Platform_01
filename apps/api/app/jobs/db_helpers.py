"""
Database helper functions for job operations
"""

import uuid
from typing import Optional

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
from packages.database.models.user import User
from packages.database.models.workflow_snapshot import WorkflowSnapshot


def get_user_credit_balance(db: Session, user_id: uuid.UUID) -> int:
    """
    Calculate user's current credit balance by summing all transactions.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Current credit balance (can be negative in edge cases)
    """
    # Sum all credit transaction amounts for the user
    result = db.execute(
        select(func.coalesce(func.sum(CreditTransaction.amount), 0))
        .where(CreditTransaction.user_id == user_id)
    ).scalar_one()

    return int(result)


def create_credit_transaction(
    db: Session,
    user_id: uuid.UUID,
    amount: int,
    transaction_type: TransactionType,
    related_job_id: Optional[uuid.UUID] = None,
    description: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> CreditTransaction:
    """
    Create a new credit transaction with calculated balance_after.

    Args:
        db: Database session
        user_id: User UUID
        amount: Credit amount (positive = add, negative = deduct)
        transaction_type: Type of transaction
        related_job_id: Optional job ID
        description: Optional description
        metadata: Optional metadata dict

    Returns:
        Created CreditTransaction

    Note:
        This function calculates balance_after by querying current balance.
        Should be called within a transaction for consistency.
    """
    # Get current balance
    current_balance = get_user_credit_balance(db, user_id)
    balance_after = current_balance + amount

    # Create transaction
    transaction = CreditTransaction(
        user_id=user_id,
        amount=amount,
        balance_after=balance_after,
        transaction_type=transaction_type,
        related_job_id=related_job_id,
        description=description,
        metadata_json=metadata,
    )

    db.add(transaction)

    # Update user's cached credit_balance field if it exists
    user = db.get(User, user_id)
    if user and hasattr(user, 'credit_balance'):
        user.credit_balance = balance_after

    return transaction


def get_workflow_snapshot(
    db: Session,
    snapshot_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[WorkflowSnapshot]:
    """
    Fetch workflow snapshot with authorization check.

    Args:
        db: Database session
        snapshot_id: Workflow snapshot UUID
        user_id: User UUID (for authorization)

    Returns:
        WorkflowSnapshot if found and authorized, None otherwise
    """
    snapshot = db.get(WorkflowSnapshot, snapshot_id)

    # Check ownership
    if snapshot and snapshot.user_id == user_id:
        return snapshot

    return None


def check_sufficient_credits(
    db: Session,
    user_id: uuid.UUID,
    required_credits: int,
) -> tuple[bool, int]:
    """
    Check if user has sufficient credits.

    Args:
        db: Database session
        user_id: User UUID
        required_credits: Required credit amount

    Returns:
        Tuple of (has_sufficient, current_balance)
    """
    current_balance = get_user_credit_balance(db, user_id)
    has_sufficient = current_balance >= required_credits

    return has_sufficient, current_balance
