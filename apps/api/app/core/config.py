"""
Application Configuration
Loads settings from environment variables
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    PROJECT_NAME: str = "AutoML Platform"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/automl_dev"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS - accepts comma-separated string or JSON array
    # Use "*" to allow all origins (for development/demo)
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from string (comma-separated or JSON array)"""
        value = self.CORS_ORIGINS_STR
        if not value:
            return ["http://localhost:3000"]
        # Handle wildcard
        if value.strip() == "*":
            return ["*"]
        # Try JSON array first
        if value.startswith("["):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    
    # Storage (Cloudflare R2)
    R2_ACCOUNT_ID: str = ""
    R2_ENDPOINT_URL: str = ""  # Will be https://{account_id}.r2.cloudflarestorage.com
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "automl-datasets-production"
    
    # ARQ (Async Redis Queue) - uses REDIS_URL for connection
    
    # File Upload Limits
    MAX_UPLOAD_SIZE_MB_FREE: int = 100
    MAX_UPLOAD_SIZE_MB_PRO: int = 1000
    MAX_UPLOAD_SIZE_MB_ENTERPRISE: int = 5000
    
    # Frontend URL (for OAuth redirects)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # OAuth - Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # OAuth - GitHub
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/auth/github/callback"
    
    # Workflow Execution Mode
    # Set to True to run workflows synchronously (no ARQ worker needed)
    # Useful for free-tier deployments without background worker support
    SYNC_WORKFLOW_EXECUTION: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    
    # Free tier defaults
    FREE_TIER_INITIAL_CREDITS: int = 50
    FREE_TIER_DATASET_LIMIT: int = 10
    FREE_TIER_WORKFLOW_LIMIT: int = 5
    FREE_TIER_STORAGE_LIMIT_MB: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
