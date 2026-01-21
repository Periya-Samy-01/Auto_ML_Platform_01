"use client";

import { useState, useMemo, useCallback } from "react";
import { ChevronDown, ChevronRight, AlertTriangle, Zap, Info, Coins } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ModelConfig } from "./model-node";
import type { AlgorithmId } from "@/configs/algorithms/types";
import {
  getAlgorithmConfig,
  getDefaultHyperparameters,
  algorithmRegistry,
} from "@/configs/algorithms";
import {
  getVisibleFields,
  validateWithContext,
  calculateWorkflowCost,
} from "@/lib/algorithmRenderer";
import { buildModelCapabilities } from "@/lib/workflowUtils";
import { DynamicField } from "../inspector/fields";

interface ModelInspectorProps {
  nodeId: string;
  config: ModelConfig;
  onConfigChange: (config: Partial<ModelConfig>) => void;
  onCapabilitiesChange?: (capabilities: ReturnType<typeof buildModelCapabilities>) => void;
  datasetInfo?: {
    sampleCount?: number;
    hasImbalancedClasses?: boolean;
  };
}

// Collapsible section component
function Section({
  title,
  icon,
  children,
  defaultOpen = true,
  badge,
}: {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
  badge?: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-white/10 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-white">{title}</span>
          {badge}
        </div>
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-zinc-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-zinc-400" />
        )}
      </button>
      {isOpen && <div className="px-4 pb-4 space-y-4">{children}</div>}
    </div>
  );
}

export function ModelInspector({
  nodeId,
  config,
  onConfigChange,
  onCapabilitiesChange,
  datasetInfo,
}: ModelInspectorProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Get algorithm config
  const algorithmConfig = config.algorithm
    ? getAlgorithmConfig(config.algorithm)
    : null;

  // Get available algorithms
  const availableAlgorithms = useMemo(() => {
    return Object.entries(algorithmRegistry).map(([id, cfg]) => ({
      id: id as AlgorithmId,
      name: cfg!.metadata.name,
      icon: cfg!.metadata.icon,
      description: cfg!.metadata.description,
      category: cfg!.metadata.category,
    }));
  }, []);

  // Get visible main and advanced fields
  const mainFields = useMemo(() => {
    if (!config.algorithm) return [];
    return getVisibleFields(config.algorithm, config.hyperparameters, "main");
  }, [config.algorithm, config.hyperparameters]);

  const advancedFields = useMemo(() => {
    if (!config.algorithm) return [];
    return getVisibleFields(config.algorithm, config.hyperparameters, "advanced");
  }, [config.algorithm, config.hyperparameters]);

  // Validation
  const validation = useMemo(() => {
    if (!config.algorithm) return { valid: true, errors: {}, warnings: [] };
    return validateWithContext(config.algorithm, config.hyperparameters, {
      datasetSize: datasetInfo?.sampleCount,
      hasImbalancedClasses: datasetInfo?.hasImbalancedClasses,
    });
  }, [config.algorithm, config.hyperparameters, datasetInfo]);

  // Cost calculation
  const estimatedCost = useMemo(() => {
    if (!config.algorithm) return 0;
    return calculateWorkflowCost({
      algorithmId: config.algorithm,
      sampleCount: datasetInfo?.sampleCount || 1000,
      useCrossValidation: config.useCrossValidation,
      useOptuna: config.useOptuna,
      optunaTrials: config.optunaTrials,
    });
  }, [config, datasetInfo?.sampleCount]);

  // Handle algorithm change
  const handleAlgorithmChange = useCallback(
    (algorithmId: AlgorithmId) => {
      const defaults = getDefaultHyperparameters(algorithmId);
      const capabilities = buildModelCapabilities(algorithmId);

      onConfigChange({
        algorithm: algorithmId,
        hyperparameters: defaults,
      });

      if (onCapabilitiesChange) {
        onCapabilitiesChange(capabilities);
      }
    },
    [onConfigChange, onCapabilitiesChange]
  );

  // Handle hyperparameter change
  const handleHyperparameterChange = useCallback(
    (key: string, value: unknown) => {
      onConfigChange({
        hyperparameters: {
          ...config.hyperparameters,
          [key]: value,
        },
      });
    },
    [config.hyperparameters, onConfigChange]
  );

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar">
      {/* Algorithm Info Header - Read-only display of selected algorithm */}
      {algorithmConfig && (
        <div className="px-4 pt-4 pb-2">
          <div className="p-4 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{algorithmConfig.metadata.icon}</span>
              <div className="flex-1">
                <p className="text-base font-semibold text-white">
                  {algorithmConfig.metadata.name}
                </p>
                <p className="text-xs text-zinc-400 mt-0.5">
                  {algorithmConfig.metadata.category.charAt(0).toUpperCase() +
                    algorithmConfig.metadata.category.slice(1)} Model
                </p>
              </div>
            </div>
            {/* Best for info */}
            <div className="mt-3 pt-3 border-t border-white/10">
              <div className="flex items-start gap-2">
                <Info className="w-3.5 h-3.5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-blue-300 font-medium">Best for:</p>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    {algorithmConfig.metadata.bestFor.slice(0, 2).join(" • ")}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* No algorithm selected state - should not happen with new flow */}
      {!config.algorithm && (
        <div className="px-4 pt-4 pb-2">
          <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <p className="text-sm font-medium text-yellow-300">No Algorithm Selected</p>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Please delete this node and create a new Model node to select an algorithm.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hyperparameters - Only show if algorithm is selected */}
      {config.algorithm && algorithmConfig && (
        <Section
          title="Hyperparameters"
          icon={<span className="text-lg">⚙️</span>}
          defaultOpen={true}
        >
          {/* Main hyperparameters */}
          <div className="space-y-4">
            {mainFields.map((field) => (
              <DynamicField
                key={field.key}
                field={field}
                value={config.hyperparameters[field.key] ?? field.default}
                onChange={(value) => handleHyperparameterChange(field.key, value)}
                allValues={config.hyperparameters}
              />
            ))}
          </div>

          {/* Advanced toggle */}
          {advancedFields.length > 0 && (
            <div className="mt-4">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-2 text-xs text-zinc-400 hover:text-zinc-300 transition-colors"
              >
                {showAdvanced ? (
                  <ChevronDown className="w-3 h-3" />
                ) : (
                  <ChevronRight className="w-3 h-3" />
                )}
                Advanced Settings ({advancedFields.length})
              </button>

              {showAdvanced && (
                <div className="mt-3 pt-3 border-t border-white/10 space-y-4">
                  {advancedFields.map((field) => (
                    <DynamicField
                      key={field.key}
                      field={field}
                      value={config.hyperparameters[field.key] ?? field.default}
                      onChange={(value) =>
                        handleHyperparameterChange(field.key, value)
                      }
                      allValues={config.hyperparameters}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Validation warnings */}
          {(validation.warnings.length > 0 ||
            Object.keys(validation.errors).length > 0) && (
              <div className="mt-4 space-y-2">
                {Object.entries(validation.errors).map(([key, message]) => (
                  <div
                    key={key}
                    className="flex items-start gap-2 p-2 rounded-lg bg-red-500/10 border border-red-500/20"
                  >
                    <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-red-300">{message}</p>
                  </div>
                ))}
                {validation.warnings.map((warning, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20"
                  >
                    <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-yellow-300">{warning}</p>
                  </div>
                ))}
              </div>
            )}
        </Section>
      )}

      {/* Training Settings */}
      {config.algorithm && (
        <Section
          title="Training Settings"
          icon={<Zap className="w-4 h-4 text-yellow-400" />}
          defaultOpen={true}
        >
          {/* Cross-Validation */}
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <div>
                <span className="text-sm text-white">Cross-Validation</span>
                <p className="text-xs text-zinc-500">
                  More reliable performance estimate
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={config.useCrossValidation}
                onClick={() =>
                  onConfigChange({ useCrossValidation: !config.useCrossValidation })
                }
                className={cn(
                  "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full",
                  "transition-colors duration-200 ease-in-out",
                  config.useCrossValidation ? "bg-blue-500" : "bg-zinc-600"
                )}
              >
                <span
                  className={cn(
                    "pointer-events-none inline-block h-4 w-4 transform rounded-full",
                    "bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
                    "mt-0.5",
                    config.useCrossValidation
                      ? "translate-x-4 ml-0.5"
                      : "translate-x-0.5"
                  )}
                />
              </button>
            </label>

            {config.useCrossValidation && (
              <div className="pl-4 border-l-2 border-blue-500/30">
                <label className="flex items-center justify-between">
                  <span className="text-xs text-zinc-300">Number of Folds</span>
                  <select
                    value={config.cvFolds}
                    onChange={(e) =>
                      onConfigChange({ cvFolds: parseInt(e.target.value) })
                    }
                    className="px-2 py-1 rounded bg-zinc-800 border border-white/10 text-sm text-white"
                  >
                    <option value={3}>3-Fold</option>
                    <option value={5}>5-Fold</option>
                    <option value={10}>10-Fold</option>
                  </select>
                </label>
              </div>
            )}
          </div>

          {/* Optuna */}
          <div className="space-y-3 mt-4">
            <label className="flex items-center justify-between">
              <div>
                <span className="text-sm text-white">Hyperparameter Tuning (Optuna)</span>
                <p className="text-xs text-zinc-500">
                  Automatically find optimal hyperparameters
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={config.useOptuna}
                onClick={() => onConfigChange({ useOptuna: !config.useOptuna })}
                className={cn(
                  "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full",
                  "transition-colors duration-200 ease-in-out",
                  config.useOptuna ? "bg-purple-500" : "bg-zinc-600"
                )}
              >
                <span
                  className={cn(
                    "pointer-events-none inline-block h-4 w-4 transform rounded-full",
                    "bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
                    "mt-0.5",
                    config.useOptuna ? "translate-x-4 ml-0.5" : "translate-x-0.5"
                  )}
                />
              </button>
            </label>

            {config.useOptuna && algorithmConfig && (
              <div className="pl-4 border-l-2 border-purple-500/30 space-y-3">
                <label className="flex items-center justify-between">
                  <span className="text-xs text-zinc-300">Number of Trials</span>
                  <select
                    value={config.optunaTrials}
                    onChange={(e) =>
                      onConfigChange({ optunaTrials: parseInt(e.target.value) })
                    }
                    className="px-2 py-1 rounded bg-zinc-800 border border-white/10 text-sm text-white"
                  >
                    <option value={20}>20 trials</option>
                    <option value={50}>50 trials</option>
                    <option value={100}>100 trials</option>
                  </select>
                </label>

                <label className="flex items-center justify-between">
                  <span className="text-xs text-zinc-300">Optimization Metric</span>
                  <select
                    value={config.optunaMetric}
                    onChange={(e) =>
                      onConfigChange({ optunaMetric: e.target.value })
                    }
                    className="px-2 py-1 rounded bg-zinc-800 border border-white/10 text-sm text-white"
                  >
                    {algorithmConfig.evaluate.supportedMetrics.map((metric) => (
                      <option key={metric} value={metric}>
                        {algorithmConfig.evaluate.metricDefinitions[metric]?.name ||
                          metric}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            )}
          </div>
        </Section>
      )}

      {/* Cost Estimate */}
      {config.algorithm && (
        <Section
          title="Cost Estimate"
          icon={<Coins className="w-4 h-4 text-yellow-400" />}
          defaultOpen={true}
        >
          <div className="p-3 rounded-lg bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20">
            <div className="flex items-center justify-between">
              <span className="text-sm text-zinc-300">Estimated Credits</span>
              <span className="text-lg font-bold text-yellow-400">
                {estimatedCost}
              </span>
            </div>
            <p className="text-xs text-zinc-500 mt-1">
              {config.useOptuna
                ? `${config.optunaTrials} Optuna trials`
                : config.useCrossValidation
                  ? `${config.cvFolds}-fold CV`
                  : "Single train/test split"}
            </p>
          </div>
        </Section>
      )}
    </div>
  );
}
