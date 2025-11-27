"""
Auth Schemas
Pydantic models for authentication requests and responses
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ============================================================
# Token Schemas
# ============================================================

class TokenPair(BaseModel):
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user_id as string
    exp: datetime
    type: str  # "access" or "refresh"


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token"""
    refresh_token: str


class DevLoginRequest(BaseModel):
    """Development login request (bypasses OAuth)"""
    email: EmailStr
    full_name: Optional[str] = None


# ============================================================
# User Schemas
# ============================================================

class UserBase(BaseModel):
    """Base user properties"""
    email: EmailStr
    full_name: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: uuid.UUID
    tier: str
    credit_balance: int
    email_verified: bool
    oauth_provider: Optional[str] = None
    created_at: datetime
    
    # Usage stats
    dataset_count: int
    workflow_count: int
    model_count: int
    storage_used_bytes: int
    
    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    """Brief user info (for token responses)"""
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    tier: str
    credit_balance: int
    
    model_config = {"from_attributes": True}


# ============================================================
# OAuth Schemas
# ============================================================

class OAuthUserInfo(BaseModel):
    """User info from OAuth provider"""
    provider: str
    provider_id: str
    email: EmailStr
    full_name: Optional[str] = None
    email_verified: bool = False


# ============================================================
# Auth Response Schemas
# ============================================================

class AuthResponse(BaseModel):
    """Authentication response with tokens and user info"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
