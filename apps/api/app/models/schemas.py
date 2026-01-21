"""
Models Schemas
Pydantic models for model (trained ML model) requests and responses
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    """Base model that outputs camelCase in JSON responses."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True,
    )


class ModelBrief(CamelCaseModel):
    """Brief model info for lists."""
    id: uuid.UUID
    name: Optional[str] = None
    model_type: Optional[str] = None  # Algorithm slug
    dataset_id: Optional[uuid.UUID] = None
    dataset_name: Optional[str] = None  # Joined from dataset
    job_id: Optional[uuid.UUID] = None
    metrics_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class ModelResponse(CamelCaseModel):
    """Full model response."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: Optional[str] = None
    model_type: Optional[str] = None
    version: Optional[str] = None
    dataset_id: Optional[uuid.UUID] = None
    dataset_name: Optional[str] = None
    job_id: Optional[uuid.UUID] = None
    metrics_json: Optional[Dict[str, Any]] = None
    hyperparameters_json: Optional[Dict[str, Any]] = None
    is_production: bool = False
    is_saved: bool = False
    s3_model_path: Optional[str] = None
    model_size_bytes: Optional[int] = None
    created_at: datetime


class ModelListResponse(CamelCaseModel):
    """Paginated list of models."""
    items: List[ModelBrief]
    total: int
    page: int
    page_size: int
    has_more: bool
