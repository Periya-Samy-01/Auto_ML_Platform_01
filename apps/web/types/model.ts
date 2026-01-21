/**
 * Model Types
 * Matches backend model schemas (camelCase from API)
 */

export interface ModelMetrics {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  roc_auc?: number;
  mae?: number;
  mse?: number;
  rmse?: number;
  r2_score?: number;
  [key: string]: number | undefined;
}

/**
 * Brief model info returned in lists (camelCase from backend)
 */
export interface ModelBrief {
  id: string;
  name: string | null;
  modelType: string | null;
  datasetId: string | null;
  datasetName: string | null;
  jobId: string | null;
  metricsJson: ModelMetrics | null;
  createdAt: string;
}

/**
 * Full model response (camelCase from backend)
 */
export interface Model {
  id: string;
  userId: string;
  name: string | null;
  modelType: string | null;
  version: string | null;
  datasetId: string | null;
  datasetName: string | null;
  jobId: string | null;
  metricsJson: ModelMetrics | null;
  hyperparametersJson: Record<string, unknown> | null;
  isProduction: boolean;
  isSaved: boolean;
  s3ModelPath: string | null;
  modelSizeBytes: number | null;
  createdAt: string;
}

/**
 * Paginated list response (camelCase from backend)
 */
export interface ModelListResponse {
  items: ModelBrief[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ModelCompareResponse {
  models: Model[];
  metricsComparison: Record<string, Record<string, number>>;
}
