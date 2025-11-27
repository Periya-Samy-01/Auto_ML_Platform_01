"""
Database Session Management
Handles connection pooling and session lifecycle
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import settings


# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,        # Number of connections to maintain
    max_overflow=10,     # Additional connections when pool is exhausted
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.DEBUG, # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Ensures proper cleanup after request completion.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
