"""
JWT Token Handling
Create and verify JWT access and refresh tokens
"""

import uuid
from datetime import datetime, timedelta, UTC
from typing import Optional, Tuple

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(user_id: uuid.UUID) -> Tuple[str, datetime]:
    """
    Create a short-lived access token.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        Tuple of (token, expiry_datetime)
    """
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire


def create_refresh_token(user_id: uuid.UUID) -> Tuple[str, datetime]:
    """
    Create a long-lived refresh token.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        Tuple of (token, expiry_datetime)
    """
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire


def create_token_pair(user_id: uuid.UUID) -> Tuple[str, str]:
    """
    Create both access and refresh tokens.
    
    Args:
        user_id: The user's UUID
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token, _ = create_access_token(user_id)
    refresh_token, _ = create_refresh_token(user_id)
    return access_token, refresh_token


def verify_token(token: str, expected_type: str = "access") -> Optional[uuid.UUID]:
    """
    Verify a JWT token and extract user_id.
    
    Args:
        token: The JWT token to verify
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        User UUID if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        # Check token type
        token_type = payload.get("type")
        if token_type != expected_type:
            return None
        
        # Extract user_id
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
            
        return uuid.UUID(user_id_str)
        
    except JWTError:
        return None
    except ValueError:
        # Invalid UUID format
        return None


def decode_token_payload(token: str) -> Optional[dict]:
    """
    Decode token without verification (for debugging).
    
    Args:
        token: The JWT token
        
    Returns:
        Payload dict if decodable, None otherwise
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
    except JWTError:
        return None
