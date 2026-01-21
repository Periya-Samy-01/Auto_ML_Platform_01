"""
Auth Router
OAuth authentication endpoints
"""

import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.jwt import (
    verify_token,
    create_token_pair,
    create_access_token,
    create_refresh_token,
)
from app.auth.oauth import (
    get_google_auth_url,
    exchange_google_code,
    get_github_auth_url,
    exchange_github_code,
    OAuthError,
)
from app.auth.redis import get_redis, RedisClient
from app.auth.schemas import (
    AuthResponse,
    DevLoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenPair,
    UserBrief,
    UserResponse,
)
from app.auth.service import AuthService

# Import User model
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from database.models import User, UserTier


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================
# Google OAuth
# ============================================================

@router.get("/google")
async def google_login(
    redis: RedisClient = Depends(get_redis),
):
    """
    Redirect to Google OAuth login page.
    
    Frontend should redirect user here, then Google will redirect
    back to /auth/google/callback with an authorization code.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in Redis (5 minute expiry)
    await redis.store_oauth_state(state)
    
    auth_url = get_google_auth_url(state=state)
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: Optional[str] = Query(None, description="State for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from Google"),
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
):
    """
    Handle Google OAuth callback.
    
    Exchanges authorization code for user info, creates/finds user,
    and redirects to frontend with JWT tokens.
    """
    frontend_callback = f"{settings.FRONTEND_URL}/auth/callback"
    
    if error:
        return RedirectResponse(
            url=f"{frontend_callback}?error={error}"
        )
    
    # Verify state (CSRF protection)
    if not state:
        return RedirectResponse(
            url=f"{frontend_callback}?error=missing_state"
        )
    
    state_valid = await redis.verify_and_delete_oauth_state(state)
    if not state_valid:
        return RedirectResponse(
            url=f"{frontend_callback}?error=invalid_state"
        )
    
    try:
        oauth_info = await exchange_google_code(code)
    except OAuthError as e:
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_failed&message={str(e)}"
        )
    
    service = AuthService(db)
    access_token, refresh_token, user, is_new = service.authenticate_oauth(oauth_info)
    
    # Redirect to frontend with tokens
    return RedirectResponse(
        url=f"{frontend_callback}?access_token={access_token}&refresh_token={refresh_token}&is_new={str(is_new).lower()}"
    )


# ============================================================
# GitHub OAuth
# ============================================================

@router.get("/github")
async def github_login(
    redis: RedisClient = Depends(get_redis),
):
    """
    Redirect to GitHub OAuth login page.
    
    Frontend should redirect user here, then GitHub will redirect
    back to /auth/github/callback with an authorization code.
    """
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in Redis (5 minute expiry)
    await redis.store_oauth_state(state)
    
    auth_url = get_github_auth_url(state=state)
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: Optional[str] = Query(None, description="State for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from GitHub"),
    error_description: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
):
    """
    Handle GitHub OAuth callback.
    
    Exchanges authorization code for user info, creates/finds user,
    and redirects to frontend with JWT tokens.
    """
    frontend_callback = f"{settings.FRONTEND_URL}/auth/callback"
    
    if error:
        detail = error_description or error
        return RedirectResponse(
            url=f"{frontend_callback}?error={detail}"
        )
    
    # Verify state (CSRF protection)
    if not state:
        return RedirectResponse(
            url=f"{frontend_callback}?error=missing_state"
        )
    
    state_valid = await redis.verify_and_delete_oauth_state(state)
    if not state_valid:
        return RedirectResponse(
            url=f"{frontend_callback}?error=invalid_state"
        )
    
    try:
        oauth_info = await exchange_github_code(code)
    except OAuthError as e:
        return RedirectResponse(
            url=f"{frontend_callback}?error=oauth_failed&message={str(e)}"
        )
    
    service = AuthService(db)
    access_token, refresh_token, user, is_new = service.authenticate_oauth(oauth_info)
    
    # Redirect to frontend with tokens
    return RedirectResponse(
        url=f"{frontend_callback}?access_token={access_token}&refresh_token={refresh_token}&is_new={str(is_new).lower()}"
    )


# ============================================================
# Token Management
# ============================================================

@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis),
):
    """
    Refresh access token using refresh token.
    
    Returns new access and refresh token pair.
    The old refresh token is blacklisted.
    """
    # Verify refresh token
    user_id = verify_token(request.refresh_token, expected_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Check if token is blacklisted
    is_blacklisted = await redis.is_token_blacklisted(request.refresh_token)
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    
    # Verify user exists
    service = AuthService(db)
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Blacklist old refresh token
    await redis.blacklist_token(request.refresh_token)
    
    # Generate new token pair
    access_token, refresh_token = create_token_pair(user.id)
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: RefreshTokenRequest,
    redis: RedisClient = Depends(get_redis),
):
    """
    Logout user by blacklisting refresh token.
    
    The access token will expire naturally after 15 minutes.
    """
    # Blacklist the refresh token (don't need to verify it)
    await redis.blacklist_token(request.refresh_token)
    
    return MessageResponse(message="Successfully logged out")


# ============================================================
# User Info
# ============================================================

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user's profile.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        tier=current_user.tier.value,
        email_verified=current_user.email_verified,
        oauth_provider=current_user.oauth_provider.value if current_user.oauth_provider else None,
        created_at=current_user.created_at,
        dataset_count=current_user.dataset_count,
        workflow_count=current_user.workflow_count,
        model_count=current_user.model_count,
        storage_used_bytes=current_user.storage_used_bytes,
    )


# ============================================================
# Development Login (Testing Only)
# ============================================================

@router.post("/dev-login", response_model=AuthResponse)
async def dev_login(
    request: DevLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Development-only login endpoint that bypasses OAuth.
    
    **ONLY ENABLED IN DEVELOPMENT MODE.**
    
    Creates or finds user by email and returns JWT tokens.
    Useful for testing without setting up OAuth credentials.
    
    Args:
        request: Email and optional full name
        
    Returns:
        JWT tokens and user info
    """
    # Only allow in development mode
    if not settings.DEBUG and settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development login is disabled in production",
        )
    
    # Look up or create user
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Create new user for development
        user = User(
            email=request.email,
            full_name=request.full_name or request.email.split("@")[0],
            tier=UserTier.FREE,
            email_verified=True,  # Auto-verify in dev mode
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate tokens
    access_token, _ = create_access_token(user.id)
    refresh_token, _ = create_refresh_token(user.id)
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserBrief(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            tier=user.tier.value,
        ),
    )


@router.post("/debug-token")
async def debug_token(
    token: str,
    db: Session = Depends(get_db),
):
    """
    **DEVELOPMENT ONLY** - Debug token validation.
    
    Helps troubleshoot authentication issues by showing:
    - Token payload
    - User lookup result
    - Any errors
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug endpoint only available in development",
        )
    
    from jose import jwt, JWTError
    import uuid
    
    result = {}
    
    try:
        # Decode without verification first to see payload
        unverified = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": False}
        )
        result["unverified_payload"] = unverified
        
        # Now verify properly
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        result["verified_payload"] = payload
        result["verification"] = "SUCCESS"
        
        # Extract user_id
        user_id_str = payload.get("sub")
        if user_id_str:
            result["user_id"] = user_id_str
            
            # Try to find user
            try:
                user_uuid = uuid.UUID(user_id_str)
                user = db.query(User).filter(User.id == user_uuid).first()
                
                if user:
                    result["user_found"] = True
                    result["user_email"] = user.email
                    result["user_is_deleted"] = user.is_deleted
                else:
                    result["user_found"] = False
                    result["error"] = "User not found in database"
            except ValueError as e:
                result["error"] = f"Invalid UUID: {e}"
        
    except JWTError as e:
        result["verification"] = "FAILED"
        result["error"] = str(e)
    
    return result
