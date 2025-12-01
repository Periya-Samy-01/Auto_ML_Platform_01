"""
Integration tests for credit endpoints
Tests the full API with HTTP requests
"""

import os
import uuid
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.user import User
from packages.database.models.enums import UserTier, TransactionType
from app.jobs.db_helpers import create_credit_transaction


class TestCreditBalanceEndpoint:
    """Test GET /api/credits/balance."""

    @patch("app.auth.dependencies.get_current_user")
    def test_get_balance_success(self, mock_get_user, client: TestClient, db_session: Session):
        """Test getting credit balance successfully."""
        # Create test user with credits
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=100,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Add some transactions
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
        )
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-30,
            transaction_type=TransactionType.CONSUMPTION,
        )
        db_session.commit()

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.get("/api/credits/balance")

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "balance" in data
        assert data["balance"] == 70  # 100 - 30
        assert "total_earned" in data
        assert data["total_earned"] == 100
        assert "total_spent" in data
        assert data["total_spent"] == 30
        assert "transaction_count" in data
        assert data["transaction_count"] == 2

    @patch("app.auth.dependencies.get_current_user")
    def test_get_balance_new_user(self, mock_get_user, client: TestClient, db_session: Session):
        """Test getting balance for a new user with no transactions."""
        # Create test user with zero balance
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.get("/api/credits/balance")

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balance"] == 0
        assert data["total_earned"] == 0
        assert data["total_spent"] == 0
        assert data["transaction_count"] == 0

    @patch("app.auth.dependencies.get_current_user")
    def test_get_balance_with_transactions(self, mock_get_user, client: TestClient, db_session: Session):
        """Test getting balance with multiple transaction types."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Multiple transaction types
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=200,
            transaction_type=TransactionType.PURCHASE,
        )
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-50,
            transaction_type=TransactionType.CONSUMPTION,
        )
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=25,
            transaction_type=TransactionType.REFUND,
        )
        db_session.commit()

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.get("/api/credits/balance")

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balance"] == 175  # 200 - 50 + 25
        assert data["total_earned"] == 225  # 200 + 25
        assert data["total_spent"] == 50
        assert data["transaction_count"] == 3


class TestCreditTransactionsEndpoint:
    """Test GET /api/credits/transactions."""

    @patch("app.auth.dependencies.get_current_user")
    def test_list_transactions_success(self, mock_get_user, client: TestClient, db_session: Session):
        """Test listing transactions successfully."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=100,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create transactions
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
            description="Purchase 1",
        )
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-30,
            transaction_type=TransactionType.CONSUMPTION,
            description="Job execution",
        )
        db_session.commit()

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.get("/api/credits/transactions")

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["has_more"] is False

        # Check transaction details
        assert data["items"][0]["amount"] == -30  # Most recent first
        assert data["items"][1]["amount"] == 100

    @patch("app.auth.dependencies.get_current_user")
    def test_list_transactions_pagination(self, mock_get_user, client: TestClient, db_session: Session):
        """Test transaction pagination."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create 5 transactions
        for i in range(5):
            create_credit_transaction(
                db=db_session,
                user_id=user.id,
                amount=10,
                transaction_type=TransactionType.PURCHASE,
                description=f"Purchase {i}",
            )
        db_session.commit()

        # Mock authentication
        mock_get_user.return_value = user

        # Test page 1 with page_size=2
        response = client.get("/api/credits/transactions?page=1&page_size=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["has_more"] is True

        # Test page 2
        response = client.get("/api/credits/transactions?page=2&page_size=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 2
        assert data["has_more"] is True

        # Test page 3 (last page)
        response = client.get("/api/credits/transactions?page=3&page_size=2")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["page"] == 3
        assert data["has_more"] is False

    @patch("app.auth.dependencies.get_current_user")
    def test_list_transactions_empty(self, mock_get_user, client: TestClient, db_session: Session):
        """Test listing transactions when none exist."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.get("/api/credits/transactions")

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 0
        assert data["total"] == 0
        assert data["has_more"] is False

    @patch("app.auth.dependencies.get_current_user")
    def test_list_transactions_ordering(self, mock_get_user, client: TestClient, db_session: Session):
        """Test that transactions are ordered by created_at DESC."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create transactions in sequence
        txn1 = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=100,
            transaction_type=TransactionType.PURCHASE,
            description="First",
        )
        txn2 = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=-30,
            transaction_type=TransactionType.CONSUMPTION,
            description="Second",
        )
        txn3 = create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=50,
            transaction_type=TransactionType.PURCHASE,
            description="Third",
        )
        db_session.commit()

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.get("/api/credits/transactions")

        # Assert response (most recent first)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"][0]["description"] == "Third"
        assert data["items"][1]["description"] == "Second"
        assert data["items"][2]["description"] == "First"

    @patch("app.auth.dependencies.get_current_user")
    def test_pagination_invalid_params(self, mock_get_user, client: TestClient, db_session: Session):
        """Test invalid pagination parameters."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Test page < 1
        response = client.get("/api/credits/transactions?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test page_size > 100
        response = client.get("/api/credits/transactions?page_size=101")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test page_size < 1
        response = client.get("/api/credits/transactions?page_size=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestMockPurchaseEndpoint:
    """Test POST /api/credits/mock-purchase."""

    @patch("app.auth.dependencies.get_current_user")
    @patch.dict(os.environ, {"ALLOW_MOCK_PURCHASES": "true"})
    def test_mock_purchase_success(self, mock_get_user, client: TestClient, db_session: Session):
        """Test mock purchase successfully."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Call endpoint
        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": 100, "description": "Test purchase"}
        )

        # Assert response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "transaction_id" in data
        assert data["amount"] == 100
        assert data["balance_after"] == 100
        assert data["description"] == "Test purchase"
        assert "message" in data

    @patch("app.auth.dependencies.get_current_user")
    @patch.dict(os.environ, {"ALLOW_MOCK_PURCHASES": "true"})
    def test_mock_purchase_updates_balance(self, mock_get_user, client: TestClient, db_session: Session):
        """Test that mock purchase updates user balance."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=50,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Add initial balance
        create_credit_transaction(
            db=db_session,
            user_id=user.id,
            amount=50,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.commit()

        # Mock authentication
        mock_get_user.return_value = user

        # Make purchase
        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": 75}
        )

        # Assert response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["balance_after"] == 125  # 50 + 75

        # Verify balance endpoint
        response = client.get("/api/credits/balance")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["balance"] == 125

    @patch("app.auth.dependencies.get_current_user")
    @patch.dict(os.environ, {"ALLOW_MOCK_PURCHASES": "true"})
    def test_mock_purchase_creates_transaction(self, mock_get_user, client: TestClient, db_session: Session):
        """Test that mock purchase creates a transaction record."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Make purchase
        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": 100}
        )

        # Assert response
        assert response.status_code == status.HTTP_201_CREATED

        # Verify transaction exists
        response = client.get("/api/credits/transactions")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["amount"] == 100
        assert data["items"][0]["transaction_type"] == "purchase"

    @patch("app.auth.dependencies.get_current_user")
    @patch.dict(os.environ, {"ALLOW_MOCK_PURCHASES": "true"})
    def test_mock_purchase_invalid_amount(self, mock_get_user, client: TestClient, db_session: Session):
        """Test mock purchase with invalid amount."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Test amount <= 0
        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": 0}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": -10}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch("app.auth.dependencies.get_current_user")
    @patch.dict(os.environ, {"ALLOW_MOCK_PURCHASES": "true"})
    def test_mock_purchase_with_description(self, mock_get_user, client: TestClient, db_session: Session):
        """Test mock purchase with custom description."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Make purchase with description
        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": 100, "description": "Custom description"}
        )

        # Assert response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] == "Custom description"

    @patch("app.auth.dependencies.get_current_user")
    @patch.dict(os.environ, {"ALLOW_MOCK_PURCHASES": "false"})
    def test_mock_purchase_disabled_in_production(self, mock_get_user, client: TestClient, db_session: Session):
        """Test that mock purchases are disabled when env var is false."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            tier=UserTier.FREE,
            credit_balance=0,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Mock authentication
        mock_get_user.return_value = user

        # Attempt purchase
        response = client.post(
            "/api/credits/mock-purchase",
            json={"amount": 100}
        )

        # Assert forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "disabled" in response.json()["detail"].lower()
