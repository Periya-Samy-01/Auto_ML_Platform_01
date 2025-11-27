"""
Auth Service
Business logic for authentication
"""

import uuid
from typing import Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.auth.jwt import create_token_pair
from app.auth.schemas import OAuthUserInfo

# Import models
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from database.models import User
from database.models.enums import OAuthProvider, UserTier


class AuthService:
    """Authentication service for OAuth and token management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False,
        ).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (case-insensitive)"""
        return self.db.query(User).filter(
            func.lower(User.email) == email.lower(),
            User.is_deleted == False,
        ).first()
    
    def get_user_by_oauth(
        self,
        provider: OAuthProvider,
        oauth_id: str,
    ) -> Optional[User]:
        """Get user by OAuth provider and ID"""
        return self.db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id,
            User.is_deleted == False,
        ).first()
    
    def find_or_create_oauth_user(
        self,
        oauth_info: OAuthUserInfo,
    ) -> Tuple[User, bool]:
        """
        Find existing user or create new one from OAuth info.
        
        Account linking: If email already exists, link OAuth to that account.
        
        Args:
            oauth_info: User info from OAuth provider
            
        Returns:
            Tuple of (user, is_new_user)
        """
        provider = OAuthProvider(oauth_info.provider.upper())
        
        # First, check if OAuth account already linked
        user = self.get_user_by_oauth(provider, oauth_info.provider_id)
        if user:
            return user, False
        
        # Check if email already exists (account linking)
        user = self.get_user_by_email(oauth_info.email)
        if user:
            # Link OAuth to existing account
            user.oauth_provider = provider
            user.oauth_id = oauth_info.provider_id
            if oauth_info.email_verified:
                user.email_verified = True
            if oauth_info.full_name and not user.full_name:
                user.full_name = oauth_info.full_name
            self.db.commit()
            self.db.refresh(user)
            return user, False
        
        # Create new user
        user = User(
            email=oauth_info.email.lower(),
            full_name=oauth_info.full_name,
            oauth_provider=provider,
            oauth_id=oauth_info.provider_id,
            email_verified=oauth_info.email_verified,
            tier=UserTier.FREE,
            credit_balance=settings.FREE_TIER_INITIAL_CREDITS,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user, True
    
    def authenticate_oauth(
        self,
        oauth_info: OAuthUserInfo,
    ) -> Tuple[str, str, User, bool]:
        """
        Authenticate user via OAuth and generate tokens.
        
        Args:
            oauth_info: User info from OAuth provider
            
        Returns:
            Tuple of (access_token, refresh_token, user, is_new_user)
        """
        user, is_new = self.find_or_create_oauth_user(oauth_info)
        access_token, refresh_token = create_token_pair(user.id)
        return access_token, refresh_token, user, is_new
    
    def refresh_tokens(self, user_id: uuid.UUID) -> Optional[Tuple[str, str]]:
        """
        Generate new token pair for user.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            Tuple of (access_token, refresh_token) or None if user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        return create_token_pair(user.id)


def get_auth_service(db: Session) -> AuthService:
    """Factory function to create AuthService"""
    return AuthService(db)
