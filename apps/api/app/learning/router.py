"""
Learning API Router
Endpoints for learning content and progress tracking
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_user

# Import User model
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from database.models import User

from .service import LearningService
from .schemas import (
    TopicListResponse,
    TopicDetailResponse,
    LessonDetailResponse,
    ProgressUpdate,
    ProgressResponse,
    QuizSubmission,
    QuizResult,
    TopicProgressSummary,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/learning",
    tags=["learning"],
)


# =============================================================================
# Topic Endpoints
# =============================================================================

@router.get("/topics", response_model=TopicListResponse)
async def list_topics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all learning topics with user's progress.
    """
    service = LearningService(db)
    return service.get_topics_with_progress(current_user)


@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
async def get_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get topic details with lessons and progress.
    """
    service = LearningService(db)
    topic = service.get_topic_detail(current_user, topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found",
        )
    
    return topic


# =============================================================================
# Lesson Endpoints
# =============================================================================

@router.get("/topics/{topic_id}/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    topic_id: str,
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get full lesson content.
    """
    service = LearningService(db)
    lesson = service.get_lesson_detail(current_user, topic_id, lesson_id)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found in topic '{topic_id}'",
        )
    
    return lesson


@router.post("/topics/{topic_id}/lessons/{lesson_id}/complete", response_model=ProgressResponse)
async def complete_lesson(
    topic_id: str,
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a lesson as completed.
    """
    service = LearningService(db)
    progress = service.mark_lesson_complete(current_user, topic_id, lesson_id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' not found in topic '{topic_id}'",
        )
    
    return progress


# =============================================================================
# Quiz Endpoints
# =============================================================================

@router.post("/topics/{topic_id}/quiz", response_model=QuizResult)
async def submit_quiz(
    topic_id: str,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit quiz answers and get results.
    """
    service = LearningService(db)
    result = service.submit_quiz(current_user, topic_id, submission.answers)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz not found for topic '{topic_id}'",
        )
    
    return result


# =============================================================================
# Progress Endpoints
# =============================================================================

@router.get("/progress", response_model=TopicProgressSummary)
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get overall learning progress summary.
    """
    service = LearningService(db)
    return service.get_progress_summary(current_user)
