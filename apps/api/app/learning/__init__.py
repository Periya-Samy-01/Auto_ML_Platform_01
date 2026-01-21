"""
Learning Module
API endpoints for learning content and progress tracking
"""

from .router import router
from .service import LearningService

__all__ = ["router", "LearningService"]
