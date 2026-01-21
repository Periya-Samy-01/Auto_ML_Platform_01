/**
 * Workflows API
 * Workflow-related API calls
 */

import api from "@/lib/axios";
import type { 
  Workflow, 
  WorkflowListResponse, 
  WorkflowCreateRequest,
  WorkflowUpdateRequest,
  PaginationParams 
} from "@/types";

/**
 * Get paginated list of workflows
 */
export const getWorkflows = async (
  params?: PaginationParams
): Promise<WorkflowListResponse> => {
  const response = await api.get<WorkflowListResponse>("/workflows", { params });
  return response.data;
};

/**
 * Get single workflow by ID
 */
export const getWorkflow = async (id: string): Promise<Workflow> => {
  const response = await api.get<Workflow>(`/workflows/${id}`);
  return response.data;
};

/**
 * Create new workflow
 */
export const createWorkflow = async (
  data: WorkflowCreateRequest
): Promise<Workflow> => {
  const response = await api.post<Workflow>("/workflows", data);
  return response.data;
};

/**
 * Update workflow
 */
export const updateWorkflow = async (
  id: string,
  data: WorkflowUpdateRequest
): Promise<Workflow> => {
  const response = await api.patch<Workflow>(`/workflows/${id}`, data);
  return response.data;
};

/**
 * Delete workflow
 */
export const deleteWorkflow = async (id: string): Promise<void> => {
  await api.delete(`/workflows/${id}`);
};

/**
 * Duplicate workflow
 */
export const duplicateWorkflow = async (id: string): Promise<Workflow> => {
  const response = await api.post<Workflow>(`/workflows/${id}/duplicate`);
  return response.data;
};
