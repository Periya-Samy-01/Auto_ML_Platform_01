"""
Learning Schemas
Pydantic models for learning API requests and responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


# ============================================================================
# Lesson Schemas
# ============================================================================

class LessonBase(BaseModel):
    """Base lesson information"""
    id: str
    title: str
    description: str
    order: int
    estimated_minutes: int = 5


class LessonResponse(LessonBase):
    """Lesson with progress info"""
    is_completed: bool = False


class LessonDetailResponse(LessonBase):
    """Full lesson content for viewing"""
    content: Optional[str] = None  # Markdown content
    key_points: Optional[List[str]] = None
    diagram_url: Optional[str] = None


# ============================================================================
# Quiz Schemas
# ============================================================================

class QuizOption(BaseModel):
    """Single quiz option"""
    id: str
    text: str


class QuizQuestion(BaseModel):
    """Quiz question"""
    id: str
    question: str
    options: List[QuizOption]
    correct_option_id: Optional[str] = None  # Hidden from client initially


class QuizSubmission(BaseModel):
    """User's quiz answer submission"""
    answers: dict[str, str] = Field(..., description="Map of question_id to selected option_id")


class QuizResult(BaseModel):
    """Quiz result after submission"""
    score: int
    total: int
    percentage: float
    passed: bool
    correct_answers: dict[str, str]  # Revealed after submission


# ============================================================================
# Topic Schemas
# ============================================================================

class TopicBase(BaseModel):
    """Base topic information"""
    id: str
    title: str
    description: str
    icon: str  # Icon name (e.g., "BookOpen", "Target")
    color: str  # Color class (e.g., "text-blue-400")
    bg_color: str  # Background color class (e.g., "bg-blue-500/10")
    difficulty: Optional[DifficultyLevel] = None
    estimated_minutes: Optional[int] = None
    lesson_count: int = 0


class TopicListItem(TopicBase):
    """Topic in list view with progress"""
    completed_lessons: int = 0
    progress_percentage: int = 0
    is_completed: bool = False
    last_accessed_at: Optional[datetime] = None


class TopicListResponse(BaseModel):
    """List of topics with user progress"""
    topics: List[TopicListItem]
    total_topics: int
    completed_topics: int


class TopicDetailResponse(TopicBase):
    """Full topic details with lessons"""
    lessons: List[LessonResponse]
    quiz: Optional[List[QuizQuestion]] = None
    # Progress info
    completed_lessons: int = 0
    progress_percentage: int = 0
    is_completed: bool = False
    quiz_score: Optional[int] = None
    quiz_passed: bool = False


# ============================================================================
# Progress Schemas
# ============================================================================

class ProgressUpdate(BaseModel):
    """Update lesson progress"""
    lesson_id: str
    completed: bool = True


class ProgressResponse(BaseModel):
    """Progress update response"""
    topic_id: str
    lesson_id: str
    completed_lessons: List[str]
    progress_percentage: int
    is_topic_completed: bool


class TopicProgressSummary(BaseModel):
    """Summary of user's overall learning progress"""
    total_topics: int
    completed_topics: int
    total_lessons: int
    completed_lessons: int
    overall_percentage: int
    current_streak: int = 0
