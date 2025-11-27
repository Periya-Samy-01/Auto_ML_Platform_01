"""
Core Routes
Health check and system endpoints
"""

from datetime import datetime, UTC

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns basic service status.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    """
    Database health check.
    Verifies database connectivity.
    """
    try:
        # Execute simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.get("/")
async def root():
    """
    Root endpoint.
    Returns API information.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
    }
