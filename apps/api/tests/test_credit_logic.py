"""
Unit tests for credit logic
Tests the business logic without HTTP requests
"""

import uuid
import pytest
from sqlalchemy.orm import Session

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.user import User
from packages.database.models.enums import UserTier, TransactionType
from app.jobs.db_helpers import (
    get_user_credit_balance,
    create_credit_transaction,
)
from app.jobs.cost_calculator import (
    get_refund_percentage,
    calculate_refund_amount,
)


class TestCreditBalance:
    """Test credit balance calculation."""

    def test_initial_balance_zero(self, db_session: Session):
        """Test that a new user has zero balance."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        balance = get_user_credit_balance(db_session, user.id)
        assert balance == 0

    def test_balance_after_purchase(self, db_session: Session):
        """Test balance after a credit purchase."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # Purchase 100 credits
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
            description="Test purchase",
        )
        db_session.commit()

        balance = get_user_credit_balance(db_session, user.id)
        assert balance == 100

    def test_balance_after_consumption(self, db_session: Session):
        """Test balance after credit consumption."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=100,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # Add initial credits
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.commit()

        # Consume 30 credits
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-30,
            transaction_type=TransactionType.CONSUMPTION,
            description="Job execution",
        )
        db_session.commit()

        balance = get_user_credit_balance(db_session, user.id)
        assert balance == 70

    def test_balance_after_refund(self, db_session: Session):
        """Test balance after a refund."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=50,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # Initial balance
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.commit()

        # Consume credits
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-50,
            transaction_type=TransactionType.CONSUMPTION,
        )
        db_session.commit()

        # Refund 25 credits
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=25,
            transaction_type=TransactionType.REFUND,
            description="Job cancelled",
        )
        db_session.commit()

        balance = get_user_credit_balance(db_session, user.id)
        assert balance == 75  # 100 - 50 + 25

    def test_balance_with_multiple_transactions(self, db_session: Session):
        """Test balance calculation with multiple transactions."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # Multiple transactions
        transactions = [
            (100, TransactionType.PURCHASE),  # +100 = 100
            (-20, TransactionType.CONSUMPTION),  # -20 = 80
            (-30, TransactionType.CONSUMPTION),  # -30 = 50
            (50, TransactionType.PURCHASE),  # +50 = 100
            (15, TransactionType.REFUND),  # +15 = 115
            (-10, TransactionType.CONSUMPTION),  # -10 = 105
        ]

        for amount, txn_type in transactions:
            create_credit_transaction(
                db=db_session,
                user_id=user.id,
                amount=amount,
                transaction_type=txn_type,
            )
            db_session.commit()

        balance = get_user_credit_balance(db_session, user.id)
        assert balance == 105  # 100 - 20 - 30 + 50 + 15 - 10


class TestCreditTransactionCreation:
    """Test credit transaction creation."""

    def test_create_purchase_transaction(self, db_session: Session):
        """Test creating a purchase transaction."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        txn = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
            description="Test purchase",
        )
        db_session.commit()

        assert txn.amount == 100
        assert txn.transaction_type == TransactionType.PURCHASE
        assert txn.description == "Test purchase"
        assert txn.balance_after == 100

    def test_create_consumption_transaction(self, db_session: Session):
        """Test creating a consumption transaction."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=100,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # Add initial balance
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.commit()

        # Create consumption
        txn = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-50,
            transaction_type=TransactionType.CONSUMPTION,
            description="Job execution",
        )
        db_session.commit()

        assert txn.amount == -50
        assert txn.transaction_type == TransactionType.CONSUMPTION
        assert txn.balance_after == 50

    def test_create_refund_transaction(self, db_session: Session):
        """Test creating a refund transaction."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=50,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # Setup initial balance
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
        )
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-50,
            transaction_type=TransactionType.CONSUMPTION,
        )
        db_session.commit()

        # Create refund
        txn = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=25,
            transaction_type=TransactionType.REFUND,
            description="Job cancelled",
        )
        db_session.commit()

        assert txn.amount == 25
        assert txn.transaction_type == TransactionType.REFUND
        assert txn.balance_after == 75

    def test_balance_after_calculation(self, db_session: Session):
        """Test that balance_after is calculated correctly."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)  # Refresh to get generated ID

        # First transaction
        txn1 = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.commit()
        assert txn1.balance_after == 100

        # Second transaction
        txn2 = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-30,
            transaction_type=TransactionType.CONSUMPTION,
        )
        db_session.commit()
        assert txn2.balance_after == 70

        # Third transaction
        txn3 = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=50,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.commit()
        assert txn3.balance_after == 120


class TestRefundCalculation:
    """Test refund penalty logic."""

    def test_refund_no_cancellations(self):
        """Test 100% refund with 0 cancellations."""
        percentage = get_refund_percentage(0)
        assert percentage == 1.0  # 100%

        refund, pct = calculate_refund_amount(100, 0)
        assert refund == 100
        assert pct == 1.0

    def test_refund_5_cancellations(self):
        """Test 75% refund with 5 cancellations."""
        percentage = get_refund_percentage(5)
        assert percentage == 0.75  # 75%

        refund, pct = calculate_refund_amount(100, 5)
        assert refund == 75
        assert pct == 0.75

    def test_refund_10_cancellations(self):
        """Test 50% refund with 10 cancellations."""
        percentage = get_refund_percentage(10)
        assert percentage == 0.5  # 50%

        refund, pct = calculate_refund_amount(100, 10)
        assert refund == 50
        assert pct == 0.5

    def test_refund_20_cancellations(self):
        """Test 50% minimum refund with 20 cancellations."""
        percentage = get_refund_percentage(20)
        assert percentage == 0.5  # 50% minimum

        refund, pct = calculate_refund_amount(100, 20)
        assert refund == 50
        assert pct == 0.5

    def test_refund_progressive_penalty(self):
        """Test that penalty increases progressively."""
        refund_0 = get_refund_percentage(0)
        refund_2 = get_refund_percentage(2)
        refund_5 = get_refund_percentage(5)
        refund_8 = get_refund_percentage(8)
        refund_10 = get_refund_percentage(10)

        assert refund_0 > refund_2 > refund_5 > refund_8 >= refund_10
        assert refund_10 == 0.5  # Minimum
