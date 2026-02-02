"""
AutoML Platform - FastAPI Application
Main entry point for the API server
"""

# CRITICAL: Add project root to Python path for packages imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def get_arq_redis_settings() -> RedisSettings:
    """Parse Redis URL into ARQ RedisSettings"""
    from urllib.parse import urlparse

    redis_url = settings.REDIS_URL
    
    # Auto-detect Upstash and ensure TLS is used
    use_ssl = False
    if "upstash.io" in redis_url:
        use_ssl = True
        if redis_url.startswith("redis://"):
            redis_url = redis_url.replace("redis://", "rediss://", 1)
    
    # Also detect if URL explicitly uses rediss://
    if redis_url.startswith("rediss://"):
        use_ssl = True
    
    parsed = urlparse(redis_url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
        password=parsed.password,
        ssl=use_ssl,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    print(f"Starting AutoML API v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")

    # Connect to Redis (non-fatal - app can work without it for basic API calls)
    from app.auth.redis import redis_client
    print("Connecting to Redis...")
    try:
        await redis_client.connect()
        # Verify Redis connection
        if await redis_client.ping():
            print("✓ Redis connected successfully")
        else:
            print("✗ Redis ping failed")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("⚠️ App will start without Redis (some features may be limited)")

    # Create ARQ Redis pool for job queuing
    print("Creating ARQ Redis pool...")
    try:
        app.state.arq_pool = await create_pool(get_arq_redis_settings())
        print("✓ ARQ pool created successfully")
    except Exception as e:
        print(f"✗ Failed to create ARQ pool: {e}")
        app.state.arq_pool = None

    yield

    # Shutdown
    print("Shutting down AutoML API")

    # Close ARQ pool
    if hasattr(app.state, 'arq_pool') and app.state.arq_pool:
        print("Closing ARQ pool...")
        await app.state.arq_pool.close()
        print("✓ ARQ pool closed")

    print("Disconnecting from Redis...")
    await redis_client.disconnect()
    print("✓ Redis disconnected")


def create_app() -> FastAPI:
    """
    Application factory.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AutoML Platform API - No-code ML training platform",
        version=settings.VERSION,
        docs_url="/docs",  # Always enabled for demo
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json",  # Always enabled for demo
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    
    # Rate limiting middleware
    from app.core.middleware import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)
    
    # Include routers
    from app.core.routes import router as core_router
    from app.auth.router import router as auth_router
    from app.datasets.router import router as datasets_router
    from app.datasets.samples_router import router as samples_router
    from app.jobs.router import router as jobs_router
    from app.plugins.router import router as plugins_router
    from app.workflows.router import router as workflows_router
    from app.models.router import router as models_router
    from app.learning.router import router as learning_router

    app.include_router(core_router)
    app.include_router(auth_router, prefix="/api")
    app.include_router(datasets_router, prefix="/api", tags=["Datasets"])
    app.include_router(samples_router, prefix="/api", tags=["Sample Datasets"])
    app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
    app.include_router(plugins_router, prefix="/api", tags=["Plugins"])
    app.include_router(workflows_router, prefix="/api", tags=["Workflows"])
    app.include_router(models_router, prefix="/api", tags=["Models"])
    app.include_router(learning_router, prefix="/api", tags=["Learning"])
    
    return app


# Create application instance
app = create_app()
