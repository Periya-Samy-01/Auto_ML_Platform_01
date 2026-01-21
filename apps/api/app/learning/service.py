"""
Learning Service
Business logic for learning content and progress tracking
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

# Import models
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from database.models import User, Tutorial, UserTutorialProgress

from .content import get_all_topics, get_topic_by_id, get_lesson_by_id, TOPICS
from .schemas import (
    TopicListItem,
    TopicListResponse,
    TopicDetailResponse,
    LessonResponse,
    LessonDetailResponse,
    ProgressResponse,
    QuizResult,
    QuizQuestion,
    TopicProgressSummary,
)


class LearningService:
    """Service for managing learning content and progress"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Topic Methods
    # =========================================================================
    
    def get_topics_with_progress(self, user: User) -> TopicListResponse:
        """Get all topics with user's progress"""
        topics_data = get_all_topics()
        topic_items: List[TopicListItem] = []
        completed_count = 0
        
        for topic_data in topics_data:
            topic_id = topic_data["id"]
            lessons = topic_data.get("lessons", [])
            lesson_count = len(lessons)
            
            # Get user progress for this topic
            progress = self._get_or_create_progress(user.id, topic_id)
            completed_lessons = len(progress.completed_steps) if progress else 0
            progress_pct = int((completed_lessons / lesson_count) * 100) if lesson_count > 0 else 0
            is_completed = progress.is_completed if progress else False
            
            if is_completed:
                completed_count += 1
            
            topic_items.append(TopicListItem(
                id=topic_id,
                title=topic_data["title"],
                description=topic_data["description"],
                icon=topic_data["icon"],
                color=topic_data["color"],
                bg_color=topic_data["bg_color"],
                difficulty=topic_data.get("difficulty"),
                estimated_minutes=topic_data.get("estimated_minutes"),
                lesson_count=lesson_count,
                completed_lessons=completed_lessons,
                progress_percentage=progress_pct,
                is_completed=is_completed,
                last_accessed_at=progress.last_accessed_at if progress else None,
            ))
        
        return TopicListResponse(
            topics=topic_items,
            total_topics=len(topic_items),
            completed_topics=completed_count,
        )
    
    def get_topic_detail(self, user: User, topic_id: str) -> Optional[TopicDetailResponse]:
        """Get topic details with lessons and progress"""
        topic_data = get_topic_by_id(topic_id)
        if not topic_data:
            return None
        
        lessons_data = topic_data.get("lessons", [])
        quiz_data = topic_data.get("quiz", [])
        
        # Get user progress
        progress = self._get_or_create_progress(user.id, topic_id)
        completed_step_ids = self._get_completed_lesson_ids(progress, lessons_data)
        
        # Update last accessed
        if progress:
            progress.last_accessed_at = datetime.utcnow()
            self.db.commit()
        
        # Build lesson responses
        lessons: List[LessonResponse] = []
        for lesson in lessons_data:
            lessons.append(LessonResponse(
                id=lesson["id"],
                title=lesson["title"],
                description=lesson["description"],
                order=lesson["order"],
                estimated_minutes=lesson.get("estimated_minutes", 5),
                is_completed=lesson["id"] in completed_step_ids,
            ))
        
        # Build quiz questions (hide correct answers)
        quiz_questions: List[QuizQuestion] = []
        for q in quiz_data:
            quiz_questions.append(QuizQuestion(
                id=q["id"],
                question=q["question"],
                options=q["options"],
                correct_option_id=None,  # Hidden
            ))
        
        # Calculate progress
        lesson_count = len(lessons_data)
        completed_count = len(completed_step_ids)
        progress_pct = int((completed_count / lesson_count) * 100) if lesson_count > 0 else 0
        
        return TopicDetailResponse(
            id=topic_id,
            title=topic_data["title"],
            description=topic_data["description"],
            icon=topic_data["icon"],
            color=topic_data["color"],
            bg_color=topic_data["bg_color"],
            difficulty=topic_data.get("difficulty"),
            estimated_minutes=topic_data.get("estimated_minutes"),
            lesson_count=lesson_count,
            lessons=lessons,
            quiz=quiz_questions if quiz_questions else None,
            completed_lessons=completed_count,
            progress_percentage=progress_pct,
            is_completed=progress.is_completed if progress else False,
            quiz_score=self._get_quiz_score(progress),
            quiz_passed=self._has_passed_quiz(progress),
        )
    
    # =========================================================================
    # Lesson Methods
    # =========================================================================
    
    def get_lesson_detail(self, user: User, topic_id: str, lesson_id: str) -> Optional[LessonDetailResponse]:
        """Get full lesson content"""
        lesson_data = get_lesson_by_id(topic_id, lesson_id)
        if not lesson_data:
            return None
        
        return LessonDetailResponse(
            id=lesson_data["id"],
            title=lesson_data["title"],
            description=lesson_data["description"],
            order=lesson_data["order"],
            estimated_minutes=lesson_data.get("estimated_minutes", 5),
            content=lesson_data.get("content"),  # Markdown content (to be added later)
            key_points=lesson_data.get("key_points"),
            diagram_url=lesson_data.get("diagram_url"),
        )
    
    def mark_lesson_complete(self, user: User, topic_id: str, lesson_id: str) -> Optional[ProgressResponse]:
        """Mark a lesson as completed"""
        topic_data = get_topic_by_id(topic_id)
        if not topic_data:
            return None
        
        lesson = get_lesson_by_id(topic_id, lesson_id)
        if not lesson:
            return None
        
        lessons_data = topic_data.get("lessons", [])
        lesson_index = next(
            (i for i, l in enumerate(lessons_data) if l["id"] == lesson_id),
            None
        )
        
        if lesson_index is None:
            return None
        
        # Get or create progress
        progress = self._get_or_create_progress(user.id, topic_id, create=True)
        
        # Add to completed steps if not already there
        if lesson_index not in progress.completed_steps:
            progress.completed_steps = progress.completed_steps + [lesson_index]
        
        # Update progress percentage
        lesson_count = len(lessons_data)
        progress.completion_percentage = int((len(progress.completed_steps) / lesson_count) * 100)
        progress.last_accessed_at = datetime.utcnow()
        
        # Check if all lessons completed
        if len(progress.completed_steps) >= lesson_count:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        completed_ids = self._get_completed_lesson_ids(progress, lessons_data)
        
        return ProgressResponse(
            topic_id=topic_id,
            lesson_id=lesson_id,
            completed_lessons=list(completed_ids),
            progress_percentage=progress.completion_percentage,
            is_topic_completed=progress.is_completed,
        )
    
    # =========================================================================
    # Quiz Methods
    # =========================================================================
    
    def submit_quiz(self, user: User, topic_id: str, answers: Dict[str, str]) -> Optional[QuizResult]:
        """Submit quiz answers and calculate score"""
        topic_data = get_topic_by_id(topic_id)
        if not topic_data:
            return None
        
        quiz_data = topic_data.get("quiz", [])
        if not quiz_data:
            return None
        
        # Calculate score
        correct_answers = {}
        score = 0
        total = len(quiz_data)
        
        for question in quiz_data:
            q_id = question["id"]
            correct_id = question["correct_option_id"]
            correct_answers[q_id] = correct_id
            
            if answers.get(q_id) == correct_id:
                score += 1
        
        percentage = (score / total) * 100 if total > 0 else 0
        passed = percentage >= 70  # 70% to pass
        
        # Save quiz result in progress
        progress = self._get_or_create_progress(user.id, topic_id, create=True)
        
        # Store quiz result in a simple format (could extend later)
        # For now, just mark topic as completed if passed
        if passed:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
            progress.completion_percentage = 100
        
        progress.last_accessed_at = datetime.utcnow()
        self.db.commit()
        
        return QuizResult(
            score=score,
            total=total,
            percentage=percentage,
            passed=passed,
            correct_answers=correct_answers,
        )
    
    # =========================================================================
    # Summary Methods
    # =========================================================================
    
    def get_progress_summary(self, user: User) -> TopicProgressSummary:
        """Get overall learning progress summary"""
        topics_data = get_all_topics()
        
        total_topics = len(topics_data)
        completed_topics = 0
        total_lessons = 0
        completed_lessons = 0
        
        for topic_data in topics_data:
            lessons = topic_data.get("lessons", [])
            total_lessons += len(lessons)
            
            progress = self._get_or_create_progress(user.id, topic_data["id"])
            if progress:
                completed_lessons += len(progress.completed_steps)
                if progress.is_completed:
                    completed_topics += 1
        
        overall_pct = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        return TopicProgressSummary(
            total_topics=total_topics,
            completed_topics=completed_topics,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            overall_percentage=overall_pct,
            current_streak=0,  # Can be implemented later
        )
    
    # =========================================================================
    # Private Helper Methods
    # =========================================================================
    
    def _get_or_create_progress(
        self, 
        user_id: uuid.UUID, 
        topic_id: str, 
        create: bool = False
    ) -> Optional[UserTutorialProgress]:
        """Get or optionally create user progress for a topic"""
        # First, ensure we have a Tutorial record for this topic
        tutorial = self.db.query(Tutorial).filter(
            Tutorial.title == topic_id  # Using title as topic_id for simplicity
        ).first()
        
        if not tutorial:
            if not create:
                return None
            # Create tutorial record
            topic_data = get_topic_by_id(topic_id)
            if not topic_data:
                return None
            
            tutorial = Tutorial(
                id=uuid.uuid4(),
                title=topic_id,  # Use topic_id as title for lookup
                description=topic_data.get("description", ""),
                difficulty=topic_data.get("difficulty"),
                estimated_duration_minutes=topic_data.get("estimated_minutes"),
                is_published=True,
                is_featured=False,
                enrollment_count=0,
                completion_count=0,
            )
            self.db.add(tutorial)
            self.db.flush()
        
        # Now get or create progress
        progress = self.db.query(UserTutorialProgress).filter(
            and_(
                UserTutorialProgress.user_id == user_id,
                UserTutorialProgress.tutorial_id == tutorial.id,
            )
        ).first()
        
        if not progress and create:
            progress = UserTutorialProgress(
                id=uuid.uuid4(),
                user_id=user_id,
                tutorial_id=tutorial.id,
                current_step_index=0,
                completed_steps=[],
                is_completed=False,
                completion_percentage=0,
            )
            self.db.add(progress)
            self.db.flush()
        
        return progress
    
    def _get_completed_lesson_ids(
        self, 
        progress: Optional[UserTutorialProgress], 
        lessons_data: List[Dict]
    ) -> set:
        """Convert completed step indices to lesson IDs"""
        if not progress or not progress.completed_steps:
            return set()
        
        completed_ids = set()
        for idx in progress.completed_steps:
            if 0 <= idx < len(lessons_data):
                completed_ids.add(lessons_data[idx]["id"])
        
        return completed_ids
    
    def _get_quiz_score(self, progress: Optional[UserTutorialProgress]) -> Optional[int]:
        """Get quiz score from progress (placeholder for now)"""
        # Could be extended to store quiz scores in progress
        return None
    
    def _has_passed_quiz(self, progress: Optional[UserTutorialProgress]) -> bool:
        """Check if user has passed the quiz"""
        # For now, if topic is completed, assume quiz is passed
        return progress.is_completed if progress else False
