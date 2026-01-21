/**
 * usePlugins Hook
 *
 * Fetches and caches plugin data from the API.
 * Provides access to model plugins and preprocessing methods.
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";

// Types
export interface ModelPlugin {
  slug: string;
  name: string;
  description: string;
  icon: string;
  problemTypes: string[];
  category: string;
  bestFor?: string;
}

export interface ModelPluginDetail extends ModelPlugin {
  hyperparameters: {
    main: HyperparameterField[];
    advanced: HyperparameterField[];
  };
  capabilities?: {
    supportedMetrics: string[];
    defaultMetrics: string[];
    supportedPlots: string[];
    defaultPlots: string[];
  };
}

export interface HyperparameterField {
  key: string;
  name: string;
  type: "int" | "float" | "select" | "bool" | "range";
  default: unknown;
  description?: string;
  min?: number;
  max?: number;
  step?: number;
  nullable?: boolean;
  nullLabel?: string;
  options?: Array<{ value: string; label: string }>;
  required?: boolean;
}

export interface PreprocessingMethod {
  key: string;
  name: string;
  category: string;
  description: string;
  applicableTypes: string[];
  parameters: Record<string, unknown>;
}

export interface MetricDefinition {
  key: string;
  name: string;
  description: string;
  higherIsBetter: boolean;
  formula?: string;
}

export interface PlotDefinition {
  key: string;
  name: string;
  description: string;
  cost: number;
}

// API functions
async function fetchModelPlugins(): Promise<ModelPlugin[]> {
  const response = await api.get("/api/plugins/models");
  return response.data;
}

async function fetchModelPluginDetail(slug: string): Promise<ModelPluginDetail> {
  const response = await api.get(`/api/plugins/models/${slug}`);
  return response.data;
}

async function fetchPreprocessingMethods(): Promise<PreprocessingMethod[]> {
  const response = await api.get("/api/plugins/preprocessing");
  return response.data;
}

async function fetchMetrics(): Promise<MetricDefinition[]> {
  const response = await api.get("/api/plugins/metrics");
  return response.data;
}

async function fetchPlots(): Promise<PlotDefinition[]> {
  const response = await api.get("/api/plugins/plots");
  return response.data;
}

// Hooks
export function useModelPlugins() {
  return useQuery({
    queryKey: ["plugins", "models"],
    queryFn: fetchModelPlugins,
    staleTime: 1000 * 60 * 30, // 30 minutes
    gcTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useModelPluginDetail(slug: string | null) {
  return useQuery({
    queryKey: ["plugins", "models", slug],
    queryFn: () => fetchModelPluginDetail(slug!),
    enabled: !!slug,
    staleTime: 1000 * 60 * 30,
    gcTime: 1000 * 60 * 60,
  });
}

export function usePreprocessingMethods() {
  return useQuery({
    queryKey: ["plugins", "preprocessing"],
    queryFn: fetchPreprocessingMethods,
    staleTime: 1000 * 60 * 30,
    gcTime: 1000 * 60 * 60,
  });
}

export function useMetrics() {
  return useQuery({
    queryKey: ["plugins", "metrics"],
    queryFn: fetchMetrics,
    staleTime: 1000 * 60 * 30,
    gcTime: 1000 * 60 * 60,
  });
}

export function usePlots() {
  return useQuery({
    queryKey: ["plugins", "plots"],
    queryFn: fetchPlots,
    staleTime: 1000 * 60 * 30,
    gcTime: 1000 * 60 * 60,
  });
}

/**
 * Combined hook for all plugin data
 */
export function usePlugins() {
  const models = useModelPlugins();
  const preprocessing = usePreprocessingMethods();
  const metrics = useMetrics();
  const plots = usePlots();

  return {
    models: models.data ?? [],
    preprocessing: preprocessing.data ?? [],
    metrics: metrics.data ?? [],
    plots: plots.data ?? [],
    isLoading: models.isLoading || preprocessing.isLoading || metrics.isLoading || plots.isLoading,
    error: models.error || preprocessing.error || metrics.error || plots.error,
    refetch: () => {
      models.refetch();
      preprocessing.refetch();
      metrics.refetch();
      plots.refetch();
    },
  };
}
