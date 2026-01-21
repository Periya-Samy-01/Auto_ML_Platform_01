"""
Pytest Configuration and Fixtures
Shared test fixtures for API testing
"""

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

# Set test environment BEFORE any imports
os.environ["ALLOW_MOCK_PURCHASES"] = "true"
os.environ["ENVIRONMENT"] = "test"

import pytest
from sqlalchemy import create_engine, event, TypeDecorator, CHAR, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add project root (where 'packages' folder is) to make 'packages.database' work
automl_root = project_root.parent.parent
sys.path.insert(0, str(automl_root))

from packages.database.base import Base
from packages.database.models import *  # noqa: F401, F403


# SQLite UUID compatibility fix - TypeDecorator for handling UUID <-> String conversion
class SQLiteUUID(TypeDecorator):
    """Platform-independent UUID type that converts UUID to/from strings for SQLite."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


# Test database (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    # Completely disable insertmanyvalues batching to avoid UUID matching issues with SQLite
    # SQLite returns strings but SQLAlchemy tries to match them with Python UUID objects
    use_insertmanyvalues=False,
)


# Patch UUID type in all models BEFORE creating tables
# This replaces PG_UUID with our SQLite-compatible type
@event.listens_for(engine, "connect")
def _on_connect(dbapi_conn, connection_record):
    """Register adapters for SQLite to handle UUID."""
    import sqlite3
    # Register UUID adapter - convert UUID to string when inserting
    sqlite3.register_adapter(uuid.UUID, lambda u: str(u))
    # Register converter - convert string back to UUID when reading
    sqlite3.register_converter("UUID", lambda b: uuid.UUID(b.decode()))


@event.listens_for(Base.metadata, "before_create")
def _set_sqlite_pragma(target, connection, **kw):
    """Enable foreign keys for SQLite"""
    if connection.dialect.name == "sqlite":
        cursor = connection.connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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
        # Drop all tables after test - disable foreign key checks for SQLite
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            conn.commit()
        Base.metadata.drop_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a test client with database session override.
    Uses a separate test app without lifespan to avoid Redis connection.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from starlette.middleware.cors import CORSMiddleware
    
    from app.core.config import settings
    from app.core.database import get_db
    
    # Create test app without lifespan (no Redis connection)
    test_app = FastAPI(
        title="Test API",
        version="test",
    )
    
    # Add CORS
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from app.core.routes import router as core_router
    from app.auth.router import router as auth_router
    from app.datasets.router import router as datasets_router
    from app.jobs.router import router as jobs_router
    
    test_app.include_router(core_router)
    test_app.include_router(auth_router, prefix="/api")
    test_app.include_router(datasets_router, prefix="/api", tags=["Datasets"])
    test_app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Mock Redis client for auth
    mock_redis = MagicMock()
    mock_redis.connect = AsyncMock()
    mock_redis.disconnect = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.is_token_blacklisted = AsyncMock(return_value=False)
    mock_redis.blacklist_token = AsyncMock(return_value=True)
    mock_redis.store_oauth_state = AsyncMock(return_value=True)
    mock_redis.verify_and_delete_oauth_state = AsyncMock(return_value=True)
    
    with patch('app.auth.redis.redis_client', mock_redis):
        with patch('app.auth.redis.get_redis', AsyncMock(return_value=mock_redis)):
            with TestClient(test_app, raise_server_exceptions=False) as test_client:
                yield test_client


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
    }


@pytest.fixture(scope="function")
def test_user(db_session: Session):
    """Create a test user for authenticated tests."""
    from packages.database.models.user import User
    from packages.database.models.enums import UserTier

    user = User(
        email="test@example.com",
        tier=UserTier.FREE,
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authenticated_client(db_session: Session, test_user):
    """
    Create a test client with authentication override.
    This bypasses JWT validation and returns the test_user directly.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from starlette.middleware.cors import CORSMiddleware

    from app.core.config import settings
    from app.core.database import get_db
    from app.auth.dependencies import get_current_user

    # Create test app without lifespan (no Redis connection)
    test_app = FastAPI(
        title="Test API",
        version="test",
    )

    # Add CORS
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from app.core.routes import router as core_router
    from app.auth.router import router as auth_router
    from app.datasets.router import router as datasets_router
    from app.jobs.router import router as jobs_router

    test_app.include_router(core_router)
    test_app.include_router(auth_router, prefix="/api")
    test_app.include_router(datasets_router, prefix="/api", tags=["Datasets"])
    test_app.include_router(jobs_router, prefix="/api", tags=["Jobs"])

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return test_user

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = override_get_current_user

    # Mock Redis client for auth
    mock_redis = MagicMock()
    mock_redis.connect = AsyncMock()
    mock_redis.disconnect = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.is_token_blacklisted = AsyncMock(return_value=False)
    mock_redis.blacklist_token = AsyncMock(return_value=True)
    mock_redis.store_oauth_state = AsyncMock(return_value=True)
    mock_redis.verify_and_delete_oauth_state = AsyncMock(return_value=True)

    with patch('app.auth.redis.redis_client', mock_redis):
        with patch('app.auth.redis.get_redis', AsyncMock(return_value=mock_redis)):
            with TestClient(test_app, raise_server_exceptions=False) as test_client:
                yield test_client
