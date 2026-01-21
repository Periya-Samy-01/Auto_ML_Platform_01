"""
Sample Datasets Router

API endpoints for listing and accessing sample datasets.
Sample datasets are read-only and available to all users.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.sample_datasets import sample_dataset_service


router = APIRouter(
    prefix="/datasets/samples",
    tags=["samples"]
)


# Pydantic Response Models
class ColumnInfoResponse(BaseModel):
    """Column metadata."""
    name: str
    dtype: str
    missing_percent: float = 0.0


class SampleDatasetResponse(BaseModel):
    """Sample dataset metadata response."""
    id: str
    name: str
    description: str
    source: str
    problem_type: str
    default_target: str
    rows: int
    columns: int
    size_bytes: int
    tags: List[str] = Field(default_factory=list)
    column_info: List[ColumnInfoResponse] = Field(default_factory=list)


class SampleListResponse(BaseModel):
    """List of sample datasets."""
    datasets: List[SampleDatasetResponse]
    total: int


# Endpoints
@router.get("", response_model=SampleListResponse)
async def list_sample_datasets(
    problem_type: Optional[str] = None,
    search: Optional[str] = None,
):
    """
    List all available sample datasets.
    
    No authentication required - sample datasets are public.
    
    Optional filters:
    - problem_type: Filter by problem type (classification, regression, etc.)
    - search: Search in name and description
    """
    samples = sample_dataset_service.list_samples()
    
    # Apply filters
    if problem_type:
        samples = [s for s in samples if s["problem_type"] == problem_type]
    
    if search:
        search_lower = search.lower()
        samples = [
            s for s in samples 
            if search_lower in s["name"].lower() 
            or search_lower in s["description"].lower()
        ]
    
    return SampleListResponse(
        datasets=[SampleDatasetResponse(**s) for s in samples],
        total=len(samples)
    )


@router.get("/{dataset_id}", response_model=SampleDatasetResponse)
async def get_sample_dataset(dataset_id: str):
    """
    Get metadata for a specific sample dataset.
    
    No authentication required.
    """
    sample = sample_dataset_service.get_sample_by_id(dataset_id)
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample dataset '{dataset_id}' not found"
        )
    
    return SampleDatasetResponse(**sample)
