"use client";

import { useState, useMemo, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  AlertCircle,
  Info,
  TrendingUp,
  Check,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { EvaluateConfig } from "./evaluate-node";
import type { ModelCapabilities } from "@/lib/workflowUtils";
import { getAlgorithmConfig } from "@/configs/algorithms";

interface EvaluateInspectorProps {
  nodeId: string;
  config: EvaluateConfig;
  onConfigChange: (config: Partial<EvaluateConfig>) => void;
  capabilities: ModelCapabilities | null;
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
    <div className="border-b border-purple-700/30 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-purple-700/20 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-white/90">{title}</span>
          {badge}
        </div>
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-purple-300/70" />
        ) : (
          <ChevronRight className="w-4 h-4 text-purple-300/70" />
        )}
      </button>
      {isOpen && <div className="px-4 pb-4 space-y-4">{children}</div>}
    </div>
  );
}

// Metric checkbox component
function MetricCheckbox({
  metricKey,
  definition,
  checked,
  onChange,
}: {
  metricKey: string;
  definition: {
    name: string;
    formula?: string;
    tooltip: string;
    higherIsBetter: boolean;
  };
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <label
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all relative",
        "border",
        checked
          ? "bg-blue-500/10 border-blue-500/30"
          : "bg-white/5 border-white/10 hover:bg-white/8"
      )}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="relative flex-shrink-0 mt-0.5">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="sr-only"
        />
        <div
          className={cn(
            "w-5 h-5 rounded border-2 transition-all flex items-center justify-center",
            checked ? "bg-blue-500 border-blue-500" : "bg-transparent border-zinc-500"
          )}
        >
          {checked && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white">{definition.name}</span>
          {definition.higherIsBetter ? (
            <TrendingUp className="w-3 h-3 text-green-400" />
          ) : (
            <TrendingUp className="w-3 h-3 text-red-400 rotate-180" />
          )}
        </div>
        {definition.formula && (
          <p className="text-xs text-zinc-500 font-mono mt-0.5">{definition.formula}</p>
        )}
      </div>

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute left-full ml-2 top-0 z-50 w-48 p-2 bg-zinc-800 rounded-lg shadow-lg border border-white/10">
          <p className="text-xs text-zinc-300">{definition.tooltip}</p>
        </div>
      )}
    </label>
  );
}

export function EvaluateInspector({
  nodeId,
  config,
  onConfigChange,
  capabilities,
}: EvaluateInspectorProps) {
  // Get algorithm config if we have capabilities
  const algorithmConfig = capabilities?.algorithm
    ? getAlgorithmConfig(capabilities.algorithm)
    : null;

  // Get available metrics from capabilities
  const availableMetrics = useMemo(() => {
    if (!capabilities || !algorithmConfig) return [];
    return capabilities.supportedMetrics.map((key) => ({
      key,
      definition: algorithmConfig.evaluate.metricDefinitions[key],
    }));
  }, [capabilities, algorithmConfig]);

  // Group metrics by category
  const metricGroups = useMemo(() => {
    const groups: Record<
      string,
      Array<{ key: string; definition: (typeof availableMetrics)[0]["definition"] }>
    > = {
      primary: [],
      secondary: [],
    };

    availableMetrics.forEach((metric) => {
      if (
        capabilities?.defaultMetrics.includes(metric.key)
      ) {
        groups.primary.push(metric);
      } else {
        groups.secondary.push(metric);
      }
    });

    return groups;
  }, [availableMetrics, capabilities]);

  // Handle metric toggle
  const handleMetricToggle = useCallback(
    (metricKey: string, checked: boolean) => {
      const newMetrics = checked
        ? [...config.selectedMetrics, metricKey]
        : config.selectedMetrics.filter((m) => m !== metricKey);
      onConfigChange({ selectedMetrics: newMetrics });
    },
    [config.selectedMetrics, onConfigChange]
  );

  // Select all defaults
  const handleSelectDefaults = useCallback(() => {
    if (capabilities) {
      onConfigChange({ selectedMetrics: [...capabilities.defaultMetrics] });
    }
  }, [capabilities, onConfigChange]);

  // Select all
  const handleSelectAll = useCallback(() => {
    if (capabilities) {
      onConfigChange({ selectedMetrics: [...capabilities.supportedMetrics] });
    }
  }, [capabilities, onConfigChange]);

  // Clear all
  const handleClearAll = useCallback(() => {
    onConfigChange({ selectedMetrics: [] });
  }, [onConfigChange]);

  // No upstream model
  if (!capabilities) {
    return (
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        <div className="flex flex-col items-center justify-center py-8">
          <AlertCircle className="w-12 h-12 text-yellow-500 mb-4" />
          <h3 className="text-sm font-medium text-white mb-2">
            No Model Connected
          </h3>
          <p className="text-xs text-zinc-400 text-center">
            Connect this node to a Model node to see available evaluation metrics.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar">
      {/* Algorithm Info */}
      <Section
        title="Connected Model"
        icon={<span className="text-lg">🤖</span>}
        defaultOpen={true}
      >
        {algorithmConfig && (
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <div className="flex items-center gap-2">
              <span>{algorithmConfig.metadata.icon}</span>
              <span className="text-sm font-medium text-white">
                {algorithmConfig.metadata.name}
              </span>
            </div>
            <p className="text-xs text-zinc-500 mt-1">
              {capabilities.supportedMetrics.length} metrics available
            </p>
          </div>
        )}
      </Section>

      {/* Metrics Selection */}
      <Section
        title="Evaluation Metrics"
        icon={<span className="text-lg">📈</span>}
        defaultOpen={true}
        badge={
          <span className="text-xs text-zinc-400">
            {config.selectedMetrics.length} selected
          </span>
        }
      >
        {/* Quick actions */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={handleSelectDefaults}
            className="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded hover:bg-blue-500/30 transition-colors"
          >
            Select Defaults
          </button>
          <button
            onClick={handleSelectAll}
            className="px-2 py-1 text-xs bg-white/10 text-zinc-300 rounded hover:bg-white/20 transition-colors"
          >
            Select All
          </button>
          <button
            onClick={handleClearAll}
            className="px-2 py-1 text-xs bg-white/10 text-zinc-300 rounded hover:bg-white/20 transition-colors"
          >
            Clear
          </button>
        </div>

        {/* Primary metrics */}
        {metricGroups.primary.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-zinc-400 uppercase tracking-wider">
              Recommended
            </p>
            {metricGroups.primary.map((metric) => (
              <MetricCheckbox
                key={metric.key}
                metricKey={metric.key}
                definition={metric.definition}
                checked={config.selectedMetrics.includes(metric.key)}
                onChange={(checked) => handleMetricToggle(metric.key, checked)}
              />
            ))}
          </div>
        )}

        {/* Secondary metrics */}
        {metricGroups.secondary.length > 0 && (
          <div className="space-y-2 mt-4">
            <p className="text-xs text-zinc-400 uppercase tracking-wider">
              Additional
            </p>
            {metricGroups.secondary.map((metric) => (
              <MetricCheckbox
                key={metric.key}
                metricKey={metric.key}
                definition={metric.definition}
                checked={config.selectedMetrics.includes(metric.key)}
                onChange={(checked) => handleMetricToggle(metric.key, checked)}
              />
            ))}
          </div>
        )}
      </Section>

      {/* Additional Options */}
      <Section
        title="Options"
        icon={<span className="text-lg">⚙️</span>}
        defaultOpen={false}
      >
        <div className="space-y-3">
          <label className="flex items-center justify-between">
            <div>
              <span className="text-sm text-white">Confidence Intervals</span>
              <p className="text-xs text-zinc-500">
                Show 95% CI for each metric
              </p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={config.showConfidenceIntervals}
              onClick={() =>
                onConfigChange({
                  showConfidenceIntervals: !config.showConfidenceIntervals,
                })
              }
              className={cn(
                "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full",
                "transition-colors duration-200 ease-in-out",
                config.showConfidenceIntervals ? "bg-blue-500" : "bg-zinc-600"
              )}
            >
              <span
                className={cn(
                  "pointer-events-none inline-block h-4 w-4 transform rounded-full",
                  "bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
                  "mt-0.5",
                  config.showConfidenceIntervals
                    ? "translate-x-4 ml-0.5"
                    : "translate-x-0.5"
                )}
              />
            </button>
          </label>

          <label className="flex items-center justify-between">
            <div>
              <span className="text-sm text-white">Compare with Baseline</span>
              <p className="text-xs text-zinc-500">
                Compare against a dummy classifier
              </p>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={config.compareWithBaseline}
              onClick={() =>
                onConfigChange({
                  compareWithBaseline: !config.compareWithBaseline,
                })
              }
              className={cn(
                "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full",
                "transition-colors duration-200 ease-in-out",
                config.compareWithBaseline ? "bg-blue-500" : "bg-zinc-600"
              )}
            >
              <span
                className={cn(
                  "pointer-events-none inline-block h-4 w-4 transform rounded-full",
                  "bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
                  "mt-0.5",
                  config.compareWithBaseline
                    ? "translate-x-4 ml-0.5"
                    : "translate-x-0.5"
                )}
              />
            </button>
          </label>
        </div>
      </Section>

      {/* Info */}
      <div className="p-4">
        <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs text-blue-300">
                Metrics will be calculated after model training completes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
