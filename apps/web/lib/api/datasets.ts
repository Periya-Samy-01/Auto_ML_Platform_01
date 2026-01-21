/**
 * Datasets API
 * Dataset-related API calls matching backend endpoints
 */

import api from "@/lib/axios";
import type {
  Dataset,
  DatasetListResponse,
  DatasetListParams,
  UploadURLRequest,
  UploadURLResponse,
  ConfirmUploadRequest,
  ConfirmUploadResponse,
  JobStatusResponse,
} from "@/types";

/**
 * Get paginated list of datasets
 */
export const getDatasets = async (
  params?: DatasetListParams
): Promise<DatasetListResponse> => {
  const response = await api.get<DatasetListResponse>("/datasets", { params });
  return response.data;
};

/**
 * Get single dataset by ID
 */
export const getDataset = async (id: string): Promise<Dataset> => {
  const response = await api.get<Dataset>(`/datasets/${id}`);
  return response.data;
};

/**
 * Request presigned upload URL
 */
export const getUploadUrl = async (
  data: UploadURLRequest
): Promise<UploadURLResponse> => {
  const response = await api.post<UploadURLResponse>(
    "/datasets/upload-url",
    data
  );
  return response.data;
};

/**
 * Confirm dataset upload and start processing
 */
export const confirmUpload = async (
  data: ConfirmUploadRequest
): Promise<ConfirmUploadResponse> => {
  const response = await api.post<ConfirmUploadResponse>(
    "/datasets/confirm",
    data
  );
  return response.data;
};

/**
 * Get ingestion job status
 */
export const getJobStatus = async (jobId: string): Promise<JobStatusResponse> => {
  const response = await api.get<JobStatusResponse>(`/datasets/jobs/${jobId}`);
  return response.data;
};

/**
 * Delete dataset
 */
export const deleteDataset = async (id: string): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/datasets/${id}`);
  return response.data;
};

/**
 * Upload file to presigned URL (direct to R2)
 * Returns a promise that resolves when upload completes
 */
export const uploadToPresignedUrl = async (
  uploadUrl: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<void> => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable && onProgress) {
        const progress = Math.round((event.loaded / event.total) * 100);
        onProgress(progress);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`));
      }
    });

    xhr.addEventListener("error", () => {
      reject(new Error("Upload failed due to network error"));
    });

    xhr.addEventListener("abort", () => {
      reject(new Error("Upload aborted"));
    });

    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type || "application/octet-stream");
    xhr.send(file);
  });
};

/**
 * Full upload flow: get URL → upload → confirm
 * Returns job info for polling
 */
export const uploadDataset = async (
  file: File,
  options: {
    name: string;
    description?: string;
    problemType?: "classification" | "regression" | "clustering" | "other";
    targetColumn?: string;
  },
  callbacks?: {
    onProgress?: (progress: number) => void;
    onStepChange?: (step: string) => void;
  }
): Promise<ConfirmUploadResponse> => {
  const { onProgress, onStepChange } = callbacks || {};

  // Step 1: Get presigned URL
  onStepChange?.("getting-url");
  const urlResponse = await getUploadUrl({
    filename: file.name,
    size_bytes: file.size,
  });

  // Step 2: Upload to R2
  onStepChange?.("uploading");
  await uploadToPresignedUrl(urlResponse.upload_url, file, onProgress);

  // Step 3: Confirm and start processing
  onStepChange?.("confirming");
  const confirmResponse = await confirmUpload({
    upload_id: urlResponse.upload_id,
    dataset_name: options.name,
    description: options.description,
    problem_type: options.problemType,
    target_column: options.targetColumn,
  });

  onStepChange?.("processing");
  return confirmResponse;
};
