"use client";

import { useState, useMemo, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  AlertCircle,
  Info,
  Coins,
  Check,
  BarChart3,
  LineChart,
  PieChart,
  ScatterChart,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { VisualizeConfig } from "./visualize-node";
import type { ModelCapabilities } from "@/lib/workflowUtils";
import { getAlgorithmConfig } from "@/configs/algorithms";
import type { PlotType, PlotDefinition } from "@/configs/algorithms/types";

interface VisualizeInspectorProps {
  nodeId: string;
  config: VisualizeConfig;
  onConfigChange: (config: Partial<VisualizeConfig>) => void;
  capabilities: ModelCapabilities | null;
}

// Plot icon mapping
const plotIcons: Record<string, React.ReactNode> = {
  confusion_matrix: <PieChart className="w-4 h-4" />,
  roc_curve: <LineChart className="w-4 h-4" />,
  precision_recall_curve: <LineChart className="w-4 h-4" />,
  learning_curve: <LineChart className="w-4 h-4" />,
  feature_importance: <BarChart3 className="w-4 h-4" />,
  coefficient_plot: <BarChart3 className="w-4 h-4" />,
  residual_plot: <ScatterChart className="w-4 h-4" />,
  prediction_vs_actual: <ScatterChart className="w-4 h-4" />,
  probability_calibration: <LineChart className="w-4 h-4" />,
  shap_summary: <BarChart3 className="w-4 h-4" />,
  shap_waterfall: <BarChart3 className="w-4 h-4" />,
  partial_dependence: <LineChart className="w-4 h-4" />,
};

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

// Plot checkbox component
function PlotCheckbox({
  plotKey,
  definition,
  checked,
  onChange,
}: {
  plotKey: PlotType;
  definition: PlotDefinition;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all",
        "border",
        checked
          ? "bg-purple-500/10 border-purple-500/30"
          : "bg-white/5 border-white/10 hover:bg-white/8"
      )}
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
            checked
              ? "bg-purple-500 border-purple-500"
              : "bg-transparent border-zinc-500"
          )}
        >
          {checked && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-purple-400">
            {plotIcons[plotKey] || <BarChart3 className="w-4 h-4" />}
          </span>
          <span className="text-sm font-medium text-white">{definition.name}</span>
          <span className="text-xs text-yellow-400 flex items-center gap-1">
            <Coins className="w-3 h-3" />
            {definition.cost}
          </span>
        </div>
        <p className="text-xs text-zinc-500 mt-0.5">{definition.description}</p>
      </div>
    </label>
  );
}

export function VisualizeInspector({
  nodeId,
  config,
  onConfigChange,
  capabilities,
}: VisualizeInspectorProps) {
  // Get algorithm config if we have capabilities
  const algorithmConfig = capabilities?.algorithm
    ? getAlgorithmConfig(capabilities.algorithm)
    : null;

  // Get available plots from capabilities
  const availablePlots = useMemo(() => {
    if (!capabilities || !algorithmConfig) return [];
    return capabilities.supportedPlots
      .map((key) => ({
        key: key as PlotType,
        definition: algorithmConfig.visualize.plotDefinitions[key as PlotType],
      }))
      .filter((p) => p.definition);
  }, [capabilities, algorithmConfig]);

  // Group plots
  const plotGroups = useMemo(() => {
    const groups: Record<string, typeof availablePlots> = {
      recommended: [],
      explainability: [],
      performance: [],
    };

    availablePlots.forEach((plot) => {
      if (capabilities?.defaultPlots.includes(plot.key)) {
        groups.recommended.push(plot);
      } else if (plot.key.includes("shap") || plot.key.includes("partial")) {
        groups.explainability.push(plot);
      } else {
        groups.performance.push(plot);
      }
    });

    return groups;
  }, [availablePlots, capabilities]);

  // Calculate total cost
  const totalCost = useMemo(() => {
    if (!algorithmConfig) return 0;
    return config.selectedPlots.reduce((sum, plotKey) => {
      const def = algorithmConfig.visualize.plotDefinitions[plotKey as PlotType];
      return sum + (def?.cost || 0);
    }, 0);
  }, [config.selectedPlots, algorithmConfig]);

  // Handle plot toggle
  const handlePlotToggle = useCallback(
    (plotKey: string, checked: boolean) => {
      const newPlots = checked
        ? [...config.selectedPlots, plotKey]
        : config.selectedPlots.filter((p) => p !== plotKey);
      onConfigChange({ selectedPlots: newPlots });
    },
    [config.selectedPlots, onConfigChange]
  );

  // Select all defaults
  const handleSelectDefaults = useCallback(() => {
    if (capabilities) {
      onConfigChange({ selectedPlots: [...capabilities.defaultPlots] });
    }
  }, [capabilities, onConfigChange]);

  // Select all
  const handleSelectAll = useCallback(() => {
    if (capabilities) {
      onConfigChange({ selectedPlots: [...capabilities.supportedPlots] });
    }
  }, [capabilities, onConfigChange]);

  // Clear all
  const handleClearAll = useCallback(() => {
    onConfigChange({ selectedPlots: [] });
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
            Connect this node to a Model node to see available visualizations.
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
              {capabilities.supportedPlots.length} visualizations available
            </p>
          </div>
        )}
      </Section>

      {/* Plot Selection */}
      <Section
        title="Visualizations"
        icon={<span className="text-lg">📊</span>}
        defaultOpen={true}
        badge={
          <span className="text-xs text-zinc-400">
            {config.selectedPlots.length} selected
          </span>
        }
      >
        {/* Quick actions */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={handleSelectDefaults}
            className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded hover:bg-purple-500/30 transition-colors"
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

        {/* Recommended plots */}
        {plotGroups.recommended.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-zinc-400 uppercase tracking-wider">
              Recommended
            </p>
            {plotGroups.recommended.map((plot) => (
              <PlotCheckbox
                key={plot.key}
                plotKey={plot.key}
                definition={plot.definition}
                checked={config.selectedPlots.includes(plot.key)}
                onChange={(checked) => handlePlotToggle(plot.key, checked)}
              />
            ))}
          </div>
        )}

        {/* Performance plots */}
        {plotGroups.performance.length > 0 && (
          <div className="space-y-2 mt-4">
            <p className="text-xs text-zinc-400 uppercase tracking-wider">
              Performance
            </p>
            {plotGroups.performance.map((plot) => (
              <PlotCheckbox
                key={plot.key}
                plotKey={plot.key}
                definition={plot.definition}
                checked={config.selectedPlots.includes(plot.key)}
                onChange={(checked) => handlePlotToggle(plot.key, checked)}
              />
            ))}
          </div>
        )}

        {/* Explainability plots */}
        {plotGroups.explainability.length > 0 && (
          <div className="space-y-2 mt-4">
            <p className="text-xs text-zinc-400 uppercase tracking-wider">
              Explainability
            </p>
            {plotGroups.explainability.map((plot) => (
              <PlotCheckbox
                key={plot.key}
                plotKey={plot.key}
                definition={plot.definition}
                checked={config.selectedPlots.includes(plot.key)}
                onChange={(checked) => handlePlotToggle(plot.key, checked)}
              />
            ))}
          </div>
        )}
      </Section>

      {/* Cost Summary */}
      <Section
        title="Cost Summary"
        icon={<Coins className="w-4 h-4 text-yellow-400" />}
        defaultOpen={true}
      >
        <div className="p-3 rounded-lg bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20">
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-300">
              Visualization Credits
            </span>
            <span className="text-lg font-bold text-yellow-400">{totalCost}</span>
          </div>
          <p className="text-xs text-zinc-500 mt-1">
            {config.selectedPlots.length} plots selected
          </p>
        </div>
      </Section>

      {/* Info */}
      <div className="p-4">
        <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs text-purple-300">
                Visualizations will be generated after model evaluation completes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
