"""
API endpoints for credit management
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.user import User
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from .schemas import (
    CreditBalanceResponse,
    CreditTransactionListResponse,
    CreditTransactionResponse,
    MockPurchaseRequest,
    MockPurchaseResponse,
)
from .service import (
    get_user_balance,
    get_user_transactions,
    create_mock_purchase,
)


router = APIRouter(prefix="/credits", tags=["Credits"])


@router.get(
    "/balance",
    response_model=CreditBalanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get credit balance",
    description="Get the current user's credit balance with additional metadata",
)
async def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditBalanceResponse:
    """
    Get credit balance for the authenticated user.

    Returns:
        - balance: Current credit balance
        - total_earned: Total credits earned (purchases + refunds)
        - total_spent: Total credits spent (consumption)
        - transaction_count: Total number of transactions

    Errors:
        - 401: Unauthorized (invalid or missing token)
    """
    balance_data = get_user_balance(db, current_user.id)
    return CreditBalanceResponse(**balance_data)


@router.get(
    "/transactions",
    response_model=CreditTransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List credit transactions",
    description="Get a paginated list of the current user's credit transactions",
)
async def get_credit_transactions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditTransactionListResponse:
    """
    List credit transactions for the authenticated user.

    Transactions are ordered by created_at DESC (most recent first).

    Parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)

    Returns:
        - items: List of transactions
        - total: Total number of transactions
        - page: Current page number
        - page_size: Items per page
        - has_more: Whether there are more pages

    Errors:
        - 400: Bad Request (invalid pagination params)
        - 401: Unauthorized (invalid or missing token)
    """
    transactions_data = get_user_transactions(db, current_user.id, page, page_size)

    # Convert items to response models
    items = [
        CreditTransactionResponse.model_validate(txn)
        for txn in transactions_data["items"]
    ]

    return CreditTransactionListResponse(
        items=items,
        total=transactions_data["total"],
        page=transactions_data["page"],
        page_size=transactions_data["page_size"],
        has_more=transactions_data["has_more"],
    )


@router.post(
    "/mock-purchase",
    response_model=MockPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mock credit purchase",
    description="Create a mock credit purchase (for development/testing only)",
)
async def mock_purchase_credits(
    request: MockPurchaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockPurchaseResponse:
    """
    Create a mock credit purchase for the authenticated user.

    **IMPORTANT**: This endpoint is only available when the `ALLOW_MOCK_PURCHASES`
    environment variable is set to `true`. It should be disabled in production.

    Parameters:
        - amount: Number of credits to purchase (must be positive)
        - description: Optional description for the transaction

    Returns:
        - transaction_id: Created transaction ID
        - amount: Credits purchased
        - balance_after: Balance after purchase
        - description: Transaction description
        - created_at: Transaction timestamp
        - message: Success message

    Errors:
        - 400: Bad Request (invalid amount)
        - 401: Unauthorized (invalid or missing token)
        - 403: Forbidden (mock purchases disabled)
    """
    transaction = create_mock_purchase(
        db=db,
        user_id=current_user.id,
        amount=request.amount,
        description=request.description or "Mock credit purchase",
    )

    return MockPurchaseResponse(
        transaction_id=transaction.id,
        amount=transaction.amount,
        balance_after=transaction.balance_after,
        description=transaction.description or "Mock credit purchase",
        created_at=transaction.created_at,
        message=f"Successfully purchased {request.amount} credits",
    )
