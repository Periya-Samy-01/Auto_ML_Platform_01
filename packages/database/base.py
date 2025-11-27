"""
SQLAlchemy Base Model
All models inherit from this Base class
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass
