/**
 * Learning API
 * API calls for learning content and progress tracking
 */

import api from "@/lib/axios";
import type {
  TopicListResponse,
  TopicDetail,
  LessonDetail,
  ProgressResponse,
  QuizResult,
  ProgressSummary,
} from "@/types/learning";

/**
 * Get all topics with user progress
 */
export const getTopics = async (): Promise<TopicListResponse> => {
  const response = await api.get<TopicListResponse>("/learning/topics");
  return response.data;
};

/**
 * Get topic details with lessons
 */
export const getTopic = async (topicId: string): Promise<TopicDetail> => {
  const response = await api.get<TopicDetail>(`/learning/topics/${topicId}`);
  return response.data;
};

/**
 * Get lesson content
 */
export const getLesson = async (
  topicId: string,
  lessonId: string
): Promise<LessonDetail> => {
  const response = await api.get<LessonDetail>(
    `/learning/topics/${topicId}/lessons/${lessonId}`
  );
  return response.data;
};

/**
 * Mark lesson as completed
 */
export const completeLesson = async (
  topicId: string,
  lessonId: string
): Promise<ProgressResponse> => {
  const response = await api.post<ProgressResponse>(
    `/learning/topics/${topicId}/lessons/${lessonId}/complete`
  );
  return response.data;
};

/**
 * Submit quiz answers
 */
export const submitQuiz = async (
  topicId: string,
  answers: Record<string, string>
): Promise<QuizResult> => {
  const response = await api.post<QuizResult>(`/learning/topics/${topicId}/quiz`, {
    answers,
  });
  return response.data;
};

/**
 * Get overall progress summary
 */
export const getProgressSummary = async (): Promise<ProgressSummary> => {
  const response = await api.get<ProgressSummary>("/learning/progress");
  return response.data;
};
