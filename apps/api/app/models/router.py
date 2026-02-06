"""
Models API Router
Endpoints for trained model management
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.user import User

from .schemas import ModelBrief, ModelResponse, ModelListResponse
from .service import get_models, get_model_by_id, delete_model

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/models",
    tags=["models"],
)


@router.get("", response_model=ModelListResponse)
async def list_models(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of trained models for the current user.
    
    Returns models with their associated dataset names and metrics.
    """
    offset = (page - 1) * page_size
    
    models, total = get_models(
        db=db,
        user=current_user,
        limit=page_size,
        offset=offset,
    )
    
    # Convert to ModelBrief with dataset name
    model_briefs = []
    for model in models:
        # For sample datasets, we stored the name in version field
        # For real datasets, get from the relationship
        if model.dataset:
            ds_name = model.dataset.name
        elif model.version:
            # Sample dataset name stored in version (format it nicely)
            ds_name = model.version.replace('_', ' ').title()
        else:
            ds_name = None
        
        model_briefs.append(ModelBrief(
            id=model.id,
            name=model.name,
            model_type=model.model_type,
            dataset_id=model.dataset_id,
            dataset_name=ds_name,
            job_id=model.job_id,
            metrics_json=model.metrics_json,
            created_at=model.created_at,
        ))
    
    has_more = (offset + page_size) < total
    
    return ModelListResponse(
        items=model_briefs,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific model.
    """
    model = get_model_by_id(db=db, user=current_user, model_id=model_id)
    
    return ModelResponse(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        model_type=model.model_type,
        version=model.version,
        dataset_id=model.dataset_id,
        dataset_name=model.dataset.name if model.dataset else None,
        job_id=model.job_id,
        metrics_json=model.metrics_json,
        hyperparameters_json=model.hyperparameters_json,
        is_production=model.is_production,
        is_saved=model.is_saved,
        s3_model_path=model.s3_model_path,
        model_size_bytes=model.model_size_bytes,
        created_at=model.created_at,
    )


    delete_model(db=db, user=current_user, model_id=model_id)
    
    return {"message": "Model deleted successfully"}


@router.get("/{model_id}/download")
async def download_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download trained model file.
    """
    from fastapi.responses import FileResponse
    import os
    import logging
    
    logger = logging.getLogger(__name__)

    model = get_model_by_id(db=db, user=current_user, model_id=model_id)
    
    logger.info(f"Downloading model {model_id}")
    logger.info(f"Model path in DB: {model.s3_model_path}")
    
    if not model.s3_model_path:
        logger.error("Model path is missing in DB")
        raise HTTPException(status_code=404, detail="Model file not found (no path)")
        
    if not os.path.exists(model.s3_model_path):
        logger.error(f"File not found on disk at: {model.s3_model_path}")
        raise HTTPException(status_code=404, detail=f"Model file not found on disk")
        
    filename = f"{model.name.replace(' ', '_')}.joblib" if model.name else "model.joblib"
    
    logger.info(f"Serving file: {model.s3_model_path}")
    
    return FileResponse(
        path=model.s3_model_path,
        filename=filename,
        media_type="application/octet-stream"
    )
