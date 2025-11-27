"""
Database Configuration
Loads settings from environment variables
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration loaded from environment"""
    
    # PostgreSQL connection
    DATABASE_URL: str = "postgresql://localhost:5432/automl_dev"
    
    # Debug mode (logs SQL queries)
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> DatabaseSettings:
    """Cached settings instance"""
    return DatabaseSettings()


settings = get_settings()
