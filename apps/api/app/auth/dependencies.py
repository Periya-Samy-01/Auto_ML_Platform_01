"""
Auth Dependencies
FastAPI dependencies for authentication
"""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.jwt import verify_token
from app.auth.service import AuthService

# Import User model
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from database.models import User


# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that extracts and validates the current user from JWT token.
    
    Raises:
        HTTPException 401: If no token, invalid token, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    user_id = verify_token(token, expected_type="access")
    
    if not user_id:
        raise credentials_exception
    
    service = AuthService(db)
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency that optionally extracts the current user.
    Returns None if no valid token, instead of raising exception.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user_id = verify_token(token, expected_type="access")
    
    if not user_id:
        return None
    
    service = AuthService(db)
    return service.get_user_by_id(user_id)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that ensures user is active (not deleted/suspended).
    """
    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user
