/**
 * Jobs API
 * Job-related API calls
 */

import api from "@/lib/axios";
import type { 
  Job, 
  JobListResponse, 
  JobCreateRequest,
  PaginationParams,
  MessageResponse 
} from "@/types";

interface JobListParams extends PaginationParams {
  status?: string;
}

/**
 * Get paginated list of jobs
 */
export const getJobs = async (
  params?: JobListParams
): Promise<JobListResponse> => {
  const response = await api.get<JobListResponse>("/jobs", { params });
  return response.data;
};

/**
 * Get single job by ID
 */
export const getJob = async (id: string): Promise<Job> => {
  const response = await api.get<Job>(`/jobs/${id}`);
  return response.data;
};

/**
 * Create new job
 */
export const createJob = async (data: JobCreateRequest): Promise<Job> => {
  const response = await api.post<Job>("/jobs", data);
  return response.data;
};

/**
 * Cancel job
 */
export const cancelJob = async (id: string): Promise<Job> => {
  const response = await api.post<Job>(`/jobs/${id}/cancel`);
  return response.data;
};

/**
 * Retry failed job
 */
export const retryJob = async (id: string): Promise<Job> => {
  const response = await api.post<Job>(`/jobs/${id}/retry`);
  return response.data;
};

/**
 * Get job logs
 */
export const getJobLogs = async (id: string): Promise<string[]> => {
  const response = await api.get<string[]>(`/jobs/${id}/logs`);
  return response.data;
};
