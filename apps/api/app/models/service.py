"""
Models Service
Business logic for trained model operations
"""

import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.model import Model
from packages.database.models.user import User
from packages.database.models.dataset import Dataset

logger = logging.getLogger(__name__)


def get_models(
    db: Session,
    user: User,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Model], int]:
    """
    Get paginated list of models for a user.
    
    Returns:
        Tuple of (models list, total count)
    """
    # Base query with dataset join for dataset name
    query = db.query(Model).filter(Model.user_id == user.id)
    
    # Get total count
    total = query.count()
    
    # Get paginated results with eager loading
    models = (
        query
        .options(joinedload(Model.dataset))
        .order_by(Model.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return models, total


def get_model_by_id(
    db: Session,
    user: User,
    model_id,
) -> Model:
    """
    Get a specific model by ID.
    
    Raises:
        ValueError: If model not found or access denied
    """
    from fastapi import HTTPException
    
    model = (
        db.query(Model)
        .options(joinedload(Model.dataset))
        .filter(Model.id == model_id, Model.user_id == user.id)
        .first()
    )
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return model


def delete_model(
    db: Session,
    user: User,
    model_id,
) -> None:
    """
    Delete a specific model by ID.
    
    Raises:
        HTTPException: If model not found or access denied
    """
    from fastapi import HTTPException
    
    model = (
        db.query(Model)
        .filter(Model.id == model_id, Model.user_id == user.id)
        .first()
    )
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(model)
    db.commit()
    
    logger.info(f"Deleted model {model_id} for user {user.id}")
