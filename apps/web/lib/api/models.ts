/**
 * Models API
 * Model-related API calls matching backend endpoints
 */

import api from "@/lib/axios";
import type { Model, ModelBrief, ModelListResponse } from "@/types";

export interface ModelsByDatasetParams {
  datasetId: string;
  page?: number;
  pageSize?: number;
}

export interface DatasetWithModels {
  id: string;
  name: string;
  modelCount: number;
}

/**
 * Get paginated list of models
 */
export const getModels = async (params?: {
  page?: number;
  pageSize?: number;
}): Promise<ModelListResponse> => {
  const response = await api.get<ModelListResponse>("/models", {
    params: {
      page: params?.page || 1,
      page_size: params?.pageSize || 50,
    },
  });
  return response.data;
};

/**
 * Get single model by ID with full details
 */
export const getModelDetails = async (modelId: string): Promise<Model> => {
  const response = await api.get<Model>(`/models/${modelId}`);
  return response.data;
};

/**
 * Get models trained on a specific dataset
 * Handles both real datasets (UUID) and sample datasets (prefixed with 'sample:')
 */
export const getModelsByDataset = async (
  datasetId: string
): Promise<ModelBrief[]> => {
  // Check if this is a sample dataset (uses 'sample:' prefix)
  if (datasetId.startsWith("sample:")) {
    const sampleName = datasetId.replace("sample:", "");
    // Fetch all models and filter client-side by datasetName
    const response = await api.get<ModelListResponse>("/models", {
      params: { page_size: 100 },
    });
    return response.data.items.filter(
      (model) => model.datasetName === sampleName && !model.datasetId
    );
  }

  // Regular dataset - filter by dataset_id
  const response = await api.get<ModelListResponse>("/models", {
    params: {
      dataset_id: datasetId,
      page_size: 100,
    },
  });
  return response.data.items;
};

/**
 * Get list of datasets that have trained models
 * This fetches all models and extracts unique datasets
 * Handles both real datasets (with datasetId) and sample datasets (datasetName only)
 */
export const getDatasetsWithModels = async (): Promise<DatasetWithModels[]> => {
  const response = await api.get<ModelListResponse>("/models", {
    params: { page_size: 100 },
  });

  // Group models by dataset - use datasetId if available, otherwise use datasetName
  const datasetMap = new Map<
    string,
    { id: string; name: string; count: number }
  >();

  for (const model of response.data.items) {
    // Use datasetId if available, otherwise use datasetName as a key
    const groupKey = model.datasetId || model.datasetName;

    if (groupKey) {
      const existing = datasetMap.get(groupKey);
      if (existing) {
        existing.count++;
      } else {
        datasetMap.set(groupKey, {
          id: model.datasetId || `sample:${model.datasetName}`, // Use special prefix for sample datasets
          name: model.datasetName || `Dataset ${groupKey.slice(0, 8)}`,
          count: 1,
        });
      }
    }
  }

  return Array.from(datasetMap.values()).map((d) => ({
    id: d.id,
    name: d.name,
    modelCount: d.count,
  }));
};

/**
 * Delete a model
 */
export const deleteModel = async (
  modelId: string
): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/models/${modelId}`);
  return response.data;
};
