"""
Database-Agnostic Type Definitions

Provides SQLAlchemy types that work across PostgreSQL (production)
and SQLite (testing). Uses `with_variant()` to map PostgreSQL-specific
types to SQLite-compatible alternatives.

Usage:
    from database.types import JSONBType, ArrayOfStrings, ArrayOfIntegers, UUIDType
    
    # In model:
    id = mapped_column(UUIDType, primary_key=True, default=uuid.uuid4)
    data = mapped_column(JSONBType, nullable=True)
    tags = mapped_column(ArrayOfStrings, nullable=True)
"""

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID

# =============================================================================
# UUID Type
# =============================================================================

# PostgreSQL UUID for production, String(36) for SQLite testing
# SQLite stores UUIDs as 36-character strings: "550e8400-e29b-41d4-a716-446655440000"
UUIDType = PG_UUID(as_uuid=True).with_variant(String(36), "sqlite")

# =============================================================================
# JSON Types
# =============================================================================

# JSONB for PostgreSQL, JSON for SQLite
# PostgreSQL JSONB supports indexing and efficient queries
# SQLite JSON is basic but works for storage/retrieval
JSONBType = JSONB().with_variant(JSON(), "sqlite")

# =============================================================================
# Array Types
# =============================================================================

# ARRAY(Text) for PostgreSQL, JSON for SQLite
# SQLite stores arrays as JSON lists: ["tag1", "tag2"]
ArrayOfStrings = ARRAY(Text).with_variant(JSON(), "sqlite")

# ARRAY(Integer) for PostgreSQL, JSON for SQLite
# SQLite stores integer arrays as JSON lists: [1, 2, 3]
ArrayOfIntegers = ARRAY(Integer).with_variant(JSON(), "sqlite")

# =============================================================================
# Enum Note
# =============================================================================
# Use SQLAlchemy's built-in Enum type (sqlalchemy.Enum) instead of
# PostgreSQL's ENUM (sqlalchemy.dialects.postgresql.ENUM).
# 
# SQLAlchemy's Enum automatically:
# - Creates native ENUM type on PostgreSQL
# - Uses VARCHAR with check constraint on SQLite
#
# Usage in models:
#     from sqlalchemy import Enum
#     from .enums import UserTier
#     
#     tier = mapped_column(Enum(UserTier), nullable=False, default=UserTier.FREE)
#
# This is database-agnostic and works for both testing (SQLite) and
# production (PostgreSQL).
