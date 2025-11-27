"""
OAuth Providers
Google and GitHub OAuth2 implementation
"""

from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.auth.schemas import OAuthUserInfo


class OAuthError(Exception):
    """OAuth authentication error"""
    pass


# ============================================================
# Google OAuth
# ============================================================

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

GOOGLE_SCOPES = [
    "openid",
    "email",
    "profile",
]


def get_google_auth_url(state: Optional[str] = None) -> str:
    """
    Generate Google OAuth authorization URL.
    
    Args:
        state: Optional state parameter for CSRF protection
        
    Returns:
        Authorization URL to redirect user to
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_google_code(code: str) -> OAuthUserInfo:
    """
    Exchange Google authorization code for user info.
    
    Args:
        code: Authorization code from Google callback
        
    Returns:
        OAuthUserInfo with user details
        
    Raises:
        OAuthError: If exchange fails
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
        )
        
        if token_response.status_code != 200:
            raise OAuthError(f"Failed to exchange code: {token_response.text}")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise OAuthError("No access token in response")
        
        # Get user info
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        if userinfo_response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {userinfo_response.text}")
        
        userinfo = userinfo_response.json()
        
        return OAuthUserInfo(
            provider="google",
            provider_id=userinfo["id"],
            email=userinfo["email"],
            full_name=userinfo.get("name"),
            email_verified=userinfo.get("verified_email", False),
        )


# ============================================================
# GitHub OAuth
# ============================================================

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

GITHUB_SCOPES = [
    "read:user",
    "user:email",
]


def get_github_auth_url(state: Optional[str] = None) -> str:
    """
    Generate GitHub OAuth authorization URL.
    
    Args:
        state: Optional state parameter for CSRF protection
        
    Returns:
        Authorization URL to redirect user to
    """
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": " ".join(GITHUB_SCOPES),
    }
    if state:
        params["state"] = state
    
    return f"{GITHUB_AUTH_URL}?{urlencode(params)}"


async def exchange_github_code(code: str) -> OAuthUserInfo:
    """
    Exchange GitHub authorization code for user info.
    
    Args:
        code: Authorization code from GitHub callback
        
    Returns:
        OAuthUserInfo with user details
        
    Raises:
        OAuthError: If exchange fails
    """
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        
        if token_response.status_code != 200:
            raise OAuthError(f"Failed to exchange code: {token_response.text}")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            error = token_data.get("error_description", "No access token")
            raise OAuthError(error)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        
        # Get user info
        userinfo_response = await client.get(GITHUB_USERINFO_URL, headers=headers)
        
        if userinfo_response.status_code != 200:
            raise OAuthError(f"Failed to get user info: {userinfo_response.text}")
        
        userinfo = userinfo_response.json()
        
        # GitHub may not return email in user info, need to fetch separately
        email = userinfo.get("email")
        email_verified = False
        
        if not email:
            # Fetch emails separately
            emails_response = await client.get(GITHUB_EMAILS_URL, headers=headers)
            
            if emails_response.status_code == 200:
                emails = emails_response.json()
                # Find primary email
                for e in emails:
                    if e.get("primary"):
                        email = e.get("email")
                        email_verified = e.get("verified", False)
                        break
                # Fallback to first verified email
                if not email:
                    for e in emails:
                        if e.get("verified"):
                            email = e.get("email")
                            email_verified = True
                            break
        
        if not email:
            raise OAuthError("Could not retrieve email from GitHub")
        
        return OAuthUserInfo(
            provider="github",
            provider_id=str(userinfo["id"]),
            email=email,
            full_name=userinfo.get("name"),
            email_verified=email_verified,
        )
