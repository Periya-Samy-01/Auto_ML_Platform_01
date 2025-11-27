"""
Database Connection
Re-exports from shared database package with API-specific configuration
"""

import sys
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Add packages to path for local development
packages_path = Path(__file__).parent.parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

# Import from shared database package
from database.base import Base
from database.models import *  # noqa: F401, F403


# Create engine with API settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Ensures proper cleanup after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Base",
]
