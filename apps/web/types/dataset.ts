/**
 * Dataset Types
 * Matches backend dataset schemas
 */

// Enums matching backend
export type FileFormat = "csv" | "json" | "parquet" | "excel" | "unknown";
export type ProblemType = "classification" | "regression" | "clustering" | "other";

// Column metadata from profiling
export interface ColumnMetadata {
  name: string;
  dtype: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values?: unknown[];
}

// Dataset response from backend
export interface Dataset {
  id: string;
  name: string;
  description: string | null;
  problem_type: ProblemType | null;
  target_column: string | null;
  current_version_id: string | null;
  row_count: number | null;
  column_count: number | null;
  columns_metadata: ColumnMetadata[] | null;
  file_size_bytes: number | null;
  created_at: string;
  updated_at: string;
  // Frontend-only: track if this dataset has a processing job
  processing_job_id?: string;
  processing_status?: string;
  processing_progress?: number;
}

// Request to get presigned upload URL
export interface UploadURLRequest {
  filename: string;
  size_bytes: number;
}

// Response with presigned upload URL
export interface UploadURLResponse {
  upload_id: string;
  upload_url: string;
  expires_at: string;
  max_size_bytes: number;
}

// Request to confirm upload and start processing
export interface ConfirmUploadRequest {
  upload_id: string;
  dataset_name: string;
  description?: string;
  problem_type?: ProblemType;
  target_column?: string;
  create_new_version?: boolean;
  dataset_id?: string; // Required if create_new_version=true
  version_label?: string;
}

// Response after confirming upload
export interface ConfirmUploadResponse {
  job_id: string;
  dataset_id: string;
  dataset_version_id: string;
  version_number: number;
  status: string;
  estimated_duration_seconds: number;
}

// Ingestion job status
export interface JobStatusResponse {
  job_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress_percentage: number;
  error_message: string | null;
  dataset_id: string;
  dataset_version_id: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

// Paginated dataset list response
export interface DatasetListResponse {
  datasets: Dataset[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Query params for listing datasets
export interface DatasetListParams {
  page?: number;
  per_page?: number;
  problem_type?: ProblemType;
  search?: string;
  sort_by?: "created_at" | "updated_at" | "name";
  sort_order?: "asc" | "desc";
  is_sample?: boolean;
}

// Upload state for tracking multi-step upload
export interface UploadState {
  step: "idle" | "getting-url" | "uploading" | "confirming" | "processing" | "completed" | "error";
  progress: number;
  uploadId?: string;
  jobId?: string;
  datasetId?: string;
  error?: string;
}
