/**
 * Dataset Hooks
 * TanStack Query hooks for dataset operations
 */

import { 
  useInfiniteQuery, 
  useQuery, 
  useMutation, 
  useQueryClient,
  type InfiniteData 
} from "@tanstack/react-query";
import { useState, useEffect, useCallback } from "react";
import {
  getDatasets,
  getDataset,
  deleteDataset,
  uploadDataset,
  getJobStatus,
} from "@/lib/api/datasets";
import type {
  Dataset,
  DatasetListResponse,
  DatasetListParams,
  ConfirmUploadResponse,
  JobStatusResponse,
  UploadState,
} from "@/types";

// Query keys
export const datasetKeys = {
  all: ["datasets"] as const,
  lists: () => [...datasetKeys.all, "list"] as const,
  list: (params: DatasetListParams) => [...datasetKeys.lists(), params] as const,
  details: () => [...datasetKeys.all, "detail"] as const,
  detail: (id: string) => [...datasetKeys.details(), id] as const,
  jobs: () => [...datasetKeys.all, "jobs"] as const,
  job: (id: string) => [...datasetKeys.jobs(), id] as const,
};

/**
 * Infinite scroll datasets list
 */
export function useDatasets(params?: Omit<DatasetListParams, "page">) {
  return useInfiniteQuery({
    queryKey: datasetKeys.list(params || {}),
    queryFn: async ({ pageParam = 1 }) => {
      return getDatasets({ ...params, page: pageParam, per_page: 20 });
    },
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    initialPageParam: 1,
  });
}

/**
 * Get single dataset
 */
export function useDataset(id: string | undefined) {
  return useQuery({
    queryKey: datasetKeys.detail(id!),
    queryFn: () => getDataset(id!),
    enabled: !!id,
  });
}

/**
 * Delete dataset mutation
 */
export function useDeleteDataset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteDataset(id),
    onSuccess: () => {
      // Invalidate all dataset lists
      queryClient.invalidateQueries({ queryKey: datasetKeys.lists() });
    },
  });
}

/**
 * Upload dataset with progress tracking
 */
export function useUploadDataset() {
  const queryClient = useQueryClient();
  const [uploadState, setUploadState] = useState<UploadState>({
    step: "idle",
    progress: 0,
  });

  const resetState = useCallback(() => {
    setUploadState({ step: "idle", progress: 0 });
  }, []);

  const mutation = useMutation({
    mutationFn: async ({
      file,
      name,
      description,
      problemType,
      targetColumn,
    }: {
      file: File;
      name: string;
      description?: string;
      problemType?: "classification" | "regression" | "clustering" | "other";
      targetColumn?: string;
    }) => {
      return uploadDataset(
        file,
        { name, description, problemType, targetColumn },
        {
          onProgress: (progress) => {
            setUploadState((prev) => ({ ...prev, progress }));
          },
          onStepChange: (step) => {
            setUploadState((prev) => ({
              ...prev,
              step: step as UploadState["step"],
            }));
          },
        }
      );
    },
    onSuccess: (data) => {
      setUploadState({
        step: "processing",
        progress: 100,
        uploadId: data.dataset_version_id,
        jobId: data.job_id,
        datasetId: data.dataset_id,
      });
      // Invalidate datasets list to show the new processing dataset
      queryClient.invalidateQueries({ queryKey: datasetKeys.lists() });
    },
    onError: (error) => {
      setUploadState((prev) => ({
        ...prev,
        step: "error",
        error: error instanceof Error ? error.message : "Upload failed",
      }));
    },
  });

  return {
    ...mutation,
    uploadState,
    resetState,
  };
}

/**
 * Poll job status until completion
 */
export function useJobStatus(
  jobId: string | undefined,
  options?: {
    enabled?: boolean;
    onStatusUpdate?: (job: JobStatusResponse) => void;
    onComplete?: (job: JobStatusResponse) => void;
    onError?: (job: JobStatusResponse) => void;
  }
) {
  const queryClient = useQueryClient();
  const { enabled = true, onStatusUpdate, onComplete, onError } = options || {};

  const query = useQuery({
    queryKey: datasetKeys.job(jobId!),
    queryFn: () => getJobStatus(jobId!),
    enabled: !!jobId && enabled,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Stop polling when completed or failed
      if (data?.status === "completed" || data?.status === "failed") {
        return false;
      }
      // Poll every 2 seconds while processing
      return 2000;
    },
  });

  // Report status updates on every data change
  useEffect(() => {
    if (query.data) {
      onStatusUpdate?.(query.data);
      
      if (query.data.status === "completed") {
        onComplete?.(query.data);
        // Invalidate datasets to refresh the list
        queryClient.invalidateQueries({ queryKey: datasetKeys.lists() });
      } else if (query.data.status === "failed") {
        onError?.(query.data);
      }
    }
  }, [query.data, onStatusUpdate, onComplete, onError, queryClient]);

  return query;
}

/**
 * Helper to flatten infinite query pages
 */
export function flattenDatasetPages(
  data: InfiniteData<DatasetListResponse> | undefined
): Dataset[] {
  if (!data) return [];
  return data.pages.flatMap((page) => page.datasets);
}

/**
 * Get total count from infinite query
 */
export function getDatasetTotal(
  data: InfiniteData<DatasetListResponse> | undefined
): number {
  return data?.pages[0]?.total ?? 0;
}
