"""
Pytest Configuration and Fixtures
Shared test fixtures for API testing
"""

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

packages_path = project_root.parent.parent / "packages"
sys.path.insert(0, str(packages_path))

from database.base import Base
from database.models import *  # noqa: F401, F403

from app.main import app
from app.core.database import get_db


# Test database (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Tables are created and dropped for isolation.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database session override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    }
