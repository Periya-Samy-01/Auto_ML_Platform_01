/**
 * Learning Types
 * TypeScript types for learning content and progress
 */

export type DifficultyLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED";

// ============================================================================
// Lesson Types
// ============================================================================

export interface Lesson {
    id: string;
    title: string;
    description: string;
    order: number;
    estimated_minutes: number;
    is_completed: boolean;
}

export interface LessonDetail extends Lesson {
    content?: string; // Markdown content
    key_points?: string[];
    diagram_url?: string;
}

// ============================================================================
// Quiz Types
// ============================================================================

export interface QuizOption {
    id: string;
    text: string;
}

export interface QuizQuestion {
    id: string;
    question: string;
    options: QuizOption[];
    correct_option_id?: string; // Hidden initially
}

export interface QuizResult {
    score: number;
    total: number;
    percentage: number;
    passed: boolean;
    correct_answers: Record<string, string>;
}

// ============================================================================
// Topic Types
// ============================================================================

export interface TopicBase {
    id: string;
    title: string;
    description: string;
    icon: string;
    color: string;
    bg_color: string;
    difficulty?: DifficultyLevel;
    estimated_minutes?: number;
    lesson_count: number;
}

export interface TopicListItem extends TopicBase {
    completed_lessons: number;
    progress_percentage: number;
    is_completed: boolean;
    last_accessed_at?: string;
}

export interface TopicListResponse {
    topics: TopicListItem[];
    total_topics: number;
    completed_topics: number;
}

export interface TopicDetail extends TopicBase {
    lessons: Lesson[];
    quiz?: QuizQuestion[];
    completed_lessons: number;
    progress_percentage: number;
    is_completed: boolean;
    quiz_score?: number;
    quiz_passed: boolean;
}

// ============================================================================
// Progress Types
// ============================================================================

export interface ProgressResponse {
    topic_id: string;
    lesson_id: string;
    completed_lessons: string[];
    progress_percentage: number;
    is_topic_completed: boolean;
}

export interface ProgressSummary {
    total_topics: number;
    completed_topics: number;
    total_lessons: number;
    completed_lessons: number;
    overall_percentage: number;
    current_streak: number;
}
