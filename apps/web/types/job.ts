/**
 * Job Types
 * Matches backend job schemas
 */

export type JobStatus =
  | "pending"
  | "queued"
  | "running"
  | "failed"
  | "completed"
  | "cancelled";

export type NodeType =
  | "dataset"
  | "preprocess"
  | "model"
  | "visualize"
  | "save";

export type NodeStatus =
  | "pending"
  | "running"
  | "success"
  | "failed"
  | "skipped";

export interface JobNode {
  id: string;
  job_id: string;
  node_id: string;
  node_type: NodeType;
  status: NodeStatus;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  progress_percentage: number | null;
  progress_message: string | null;
  result_json: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
}

export interface Job {
  id: string;
  user_id: string;
  workflow_snapshot_id: string | null;
  status: JobStatus;
  priority: number;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  celery_task_id: string | null;
  created_at: string;
  nodes?: JobNode[];
}

export interface JobCreateRequest {
  workflow_id: string;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface JobProgress {
  job_id: string;
  status: JobStatus;
  progress_percentage: number;
  current_node: string | null;
  message: string | null;
}
