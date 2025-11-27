"""
Auth Module
OAuth authentication, JWT tokens, and user management
"""

from app.auth.router import router
from app.auth.dependencies import get_current_user, get_current_user_optional

__all__ = [
    "router",
    "get_current_user",
    "get_current_user_optional",
]
