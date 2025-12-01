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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


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
    
    # Connect to Redis
    from app.auth.redis import redis_client
    print("Connecting to Redis...")
    await redis_client.connect()
    
    # Verify Redis connection
    if await redis_client.ping():
        print("✓ Redis connected successfully")
    else:
        print("✗ Redis connection failed")
    
    yield
    
    # Shutdown
    print("Shutting down AutoML API")
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
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
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
    
    # Include routers
    from app.core.routes import router as core_router
    from app.auth.router import router as auth_router
    from app.datasets.router import router as datasets_router
    from app.jobs.router import router as jobs_router
    from app.credits.router import router as credits_router

    app.include_router(core_router)
    app.include_router(auth_router, prefix="/api")
    app.include_router(datasets_router, prefix="/api", tags=["Datasets"])
    app.include_router(jobs_router, prefix="/api", tags=["Jobs"])
    app.include_router(credits_router, prefix="/api", tags=["Credits"])
    
    # Feature routers (will be added later)
    # from app.datasets.routes import router as datasets_router
    # from app.workflows.routes import router as workflows_router
    # from app.jobs.routes import router as jobs_router
    # from app.credits.routes import router as credits_router
    # from app.models.routes import router as models_router
    
    # app.include_router(datasets_router, prefix="/api/datasets", tags=["Datasets"])
    # app.include_router(workflows_router, prefix="/api/workflows", tags=["Workflows"])
    # app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
    # app.include_router(credits_router, prefix="/api/credits", tags=["Credits"])
    # app.include_router(models_router, prefix="/api/models", tags=["Models"])
    
    return app


# Create application instance
app = create_app()
