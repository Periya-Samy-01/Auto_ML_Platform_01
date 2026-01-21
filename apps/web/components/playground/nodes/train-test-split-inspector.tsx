"use client";

import { useState, useMemo, useCallback, useEffect } from "react";
import {
  ChevronDown,
  ChevronRight,
  AlertCircle,
  RefreshCw,
  Lightbulb,
  Info,
  AlertTriangle,
  Database,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import type { TrainTestSplitConfig } from "./train-test-split-node";

interface TrainTestSplitInspectorProps {
  nodeId: string;
  config: TrainTestSplitConfig;
  onConfigChange: (config: Partial<TrainTestSplitConfig>) => void;
}

// Collapsible Section Component
function CollapsibleSection({
  title,
  defaultOpen = false,
  badge,
  children,
}: {
  title: string;
  defaultOpen?: boolean;
  badge?: number;
  children: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-white/5 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isOpen ? (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-zinc-400" />
          )}
          <span className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
            {title}
          </span>
        </div>
        {badge !== undefined && badge > 0 && (
          <span className="px-2 py-0.5 text-xs font-medium bg-amber-500/20 text-amber-400 rounded-full">
            {badge}
          </span>
        )}
      </button>
      {isOpen && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

// Warning Card Component
function WarningCard({
  type,
  title,
  message,
}: {
  type: "warning" | "tip" | "info";
  title: string;
  message: string;
}) {
  const styles = {
    warning: {
      bg: "bg-amber-500/5",
      border: "border-l-amber-500",
      icon: <AlertTriangle className="w-4 h-4 text-amber-500" />,
    },
    tip: {
      bg: "bg-blue-500/5",
      border: "border-l-blue-500",
      icon: <Lightbulb className="w-4 h-4 text-blue-500" />,
    },
    info: {
      bg: "bg-blue-500/5",
      border: "border-l-blue-500",
      icon: <Info className="w-4 h-4 text-blue-500" />,
    },
  };

  const style = styles[type];

  return (
    <div
      className={cn(
        "rounded-lg p-3 border-l-[3px] mb-3 last:mb-0",
        style.bg,
        style.border
      )}
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0 mt-0.5">{style.icon}</div>
        <div>
          <p className="text-[13px] font-semibold text-white mb-1">{title}</p>
          <p className="text-xs text-zinc-400">{message}</p>
        </div>
      </div>
    </div>
  );
}

export function TrainTestSplitInspector({
  nodeId,
  config,
  onConfigChange,
}: TrainTestSplitInspectorProps) {
  const [localTestSize, setLocalTestSize] = useState(config.testSize);

  // Sync local state with config
  useEffect(() => {
    setLocalTestSize(config.testSize);
  }, [config.testSize]);

  // Calculate row counts
  const trainRows = useMemo(() => {
    if (!config.totalRows) return null;
    return Math.ceil(config.totalRows * ((100 - localTestSize) / 100));
  }, [config.totalRows, localTestSize]);

  const testRows = useMemo(() => {
    if (!config.totalRows) return null;
    return Math.floor(config.totalRows * (localTestSize / 100));
  }, [config.totalRows, localTestSize]);

  // Generate warnings
  const warnings = useMemo(() => {
    const result: Array<{ type: "warning" | "tip" | "info"; title: string; message: string }> = [];

    if (testRows !== null && testRows < 30) {
      result.push({
        type: "warning",
        title: "Small test set",
        message: `Test set is very small (${testRows} rows). Consider increasing the split percentage for better evaluation.`,
      });
    }

    if (
      config.problemType === "classification" &&
      !config.stratify &&
      config.classDistribution
    ) {
      const counts = config.classDistribution.map((c) => c.total);
      const max = Math.max(...counts);
      const min = Math.min(...counts);
      if (max / min >= 2) {
        result.push({
          type: "tip",
          title: "Enable stratification",
          message:
            "Your dataset has imbalanced classes. Stratification will ensure better representation in both sets.",
        });
      }
    }

    if (!config.shuffle) {
      result.push({
        type: "info",
        title: "Shuffle is disabled",
        message: "Make sure your data is not ordered by target variable.",
      });
    }

    return result;
  }, [testRows, config.problemType, config.stratify, config.shuffle, config.classDistribution]);

  // Handlers
  const handleSliderChange = useCallback((value: number[]) => {
    setLocalTestSize(value[0]);
  }, []);

  const handleSliderCommit = useCallback(
    (value: number[]) => {
      const newTestSize = value[0];
      const newTrainRows = config.totalRows
        ? Math.ceil(config.totalRows * ((100 - newTestSize) / 100))
        : null;
      const newTestRows = config.totalRows
        ? Math.floor(config.totalRows * (newTestSize / 100))
        : null;

      onConfigChange({
        testSize: newTestSize,
        trainRows: newTrainRows,
        testRows: newTestRows,
      });
    },
    [config.totalRows, onConfigChange]
  );

  const handlePresetClick = useCallback(
    (testPercent: number) => {
      setLocalTestSize(testPercent);
      const newTrainRows = config.totalRows
        ? Math.ceil(config.totalRows * ((100 - testPercent) / 100))
        : null;
      const newTestRows = config.totalRows
        ? Math.floor(config.totalRows * (testPercent / 100))
        : null;

      onConfigChange({
        testSize: testPercent,
        trainRows: newTrainRows,
        testRows: newTestRows,
      });
    },
    [config.totalRows, onConfigChange]
  );

  const handleStratifyChange = useCallback(
    (checked: boolean) => {
      onConfigChange({ stratify: checked });
    },
    [onConfigChange]
  );

  const handleShuffleChange = useCallback(
    (checked: boolean) => {
      onConfigChange({ shuffle: checked });
    },
    [onConfigChange]
  );

  const handleSeedChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = parseInt(e.target.value, 10);
      if (!isNaN(value) && value >= 0 && value <= 9999) {
        onConfigChange({ randomSeed: value });
      }
    },
    [onConfigChange]
  );

  const handleRegenerateSeed = useCallback(() => {
    const newSeed = Math.floor(Math.random() * 10000);
    onConfigChange({ randomSeed: newSeed });
  }, [onConfigChange]);

  const hasInput = !!config.inputDatasetId;
  const isClassification = config.problemType === "classification";

  return (
    <div className="flex flex-col h-full overflow-y-auto custom-scrollbar">
      {/* Empty State */}
      {!hasInput && (
        <div className="flex flex-col items-center justify-center py-8 px-6 border-b border-white/5">
          <div className="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center mb-3">
            <AlertCircle className="w-6 h-6 text-amber-500" />
          </div>
          <p className="text-sm font-semibold text-amber-500 mb-1">
            No Input Connected
          </p>
          <p className="text-xs text-zinc-400 text-center">
            Connect a Dataset Node to configure the train/test split.
          </p>
        </div>
      )}

      {/* Section 1: Input Dataset */}
      <CollapsibleSection title="Input Dataset" defaultOpen={hasInput}>
        {hasInput ? (
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                <Database className="w-4 h-4 text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">
                  {config.inputDatasetName || "Dataset"}
                </p>
                <p className="text-xs text-zinc-400">
                  {config.totalRows} rows • {config.targetColumn || "No target"}
                </p>
                {config.problemType && (
                  <p className="text-xs text-zinc-500 capitalize mt-0.5">
                    {config.problemType}
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-zinc-500 italic">No dataset connected</p>
        )}
      </CollapsibleSection>

      {/* Section 2: Split Configuration */}
      <CollapsibleSection title="Split Configuration" defaultOpen={true}>
        <div className={cn(!hasInput && "opacity-50 pointer-events-none")}>
          <label className="block text-xs font-medium text-zinc-300 mb-3">
            Test Split Size
          </label>

          {/* Slider with percentage display */}
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1">
              <Slider
                value={[localTestSize]}
                onValueChange={handleSliderChange}
                onValueCommit={handleSliderCommit}
                min={10}
                max={50}
                step={1}
                disabled={!hasInput}
                className="w-full"
              />
            </div>
            <span className="text-lg font-bold text-white w-12 text-right">
              {localTestSize}%
            </span>
          </div>

          {/* Preset Buttons */}
          <div className="mb-3">
            <p className="text-xs text-zinc-500 mb-2">Quick Presets:</p>
            <div className="flex gap-2">
              {[
                { label: "80/20", value: 20 },
                { label: "70/30", value: 30 },
                { label: "90/10", value: 10 },
              ].map((preset) => (
                <button
                  key={preset.value}
                  onClick={() => handlePresetClick(preset.value)}
                  disabled={!hasInput}
                  className={cn(
                    "flex-1 h-9 rounded-lg text-[13px] font-medium transition-all",
                    "bg-white/5 border border-white/10",
                    "hover:bg-blue-500/10 hover:border-blue-500",
                    localTestSize === preset.value &&
                      "bg-blue-500/20 border-blue-500 border-2"
                  )}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <p className="text-[11px] text-zinc-500 italic">Range: 10% - 50%</p>
        </div>
      </CollapsibleSection>

      {/* Section 3: Options */}
      <CollapsibleSection title="Options" defaultOpen={true}>
        <div className={cn(!hasInput && "opacity-50 pointer-events-none", "space-y-4")}>
          {/* Stratify Checkbox */}
          <div>
            <div className="flex items-start gap-3">
              <Checkbox
                id="stratify"
                checked={config.stratify}
                onCheckedChange={handleStratifyChange}
                disabled={!hasInput || !isClassification}
                className="mt-0.5"
              />
              <div className="flex-1">
                <label
                  htmlFor="stratify"
                  className={cn(
                    "text-sm font-medium cursor-pointer",
                    !isClassification ? "text-zinc-500" : "text-white"
                  )}
                >
                  Stratify split
                </label>
                <p className="text-xs text-zinc-500 mt-1">
                  Maintains class distribution in train and test sets.
                </p>
              </div>
            </div>
            {isClassification && (
              <div className="mt-2 p-2 rounded-lg bg-blue-500/5 border-l-[3px] border-l-blue-500">
                <div className="flex items-center gap-2">
                  <Info className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-[11px] text-zinc-400">
                    Recommended for classification tasks.
                  </span>
                </div>
              </div>
            )}
            {!isClassification && config.problemType && (
              <p className="text-[11px] text-zinc-500 mt-1 italic">
                Stratification only available for classification tasks.
              </p>
            )}
          </div>

          {/* Shuffle Checkbox */}
          <div className="flex items-start gap-3">
            <Checkbox
              id="shuffle"
              checked={config.shuffle}
              onCheckedChange={handleShuffleChange}
              disabled={!hasInput}
              className="mt-0.5"
            />
            <div className="flex-1">
              <label
                htmlFor="shuffle"
                className="text-sm font-medium text-white cursor-pointer"
              >
                Shuffle before split
              </label>
              <p className="text-xs text-zinc-500 mt-1">
                Randomizes data order before splitting. Disable for time series
                data.
              </p>
            </div>
          </div>

          {/* Random Seed */}
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Random Seed
            </label>
            <div className="flex gap-2">
              <Input
                type="number"
                value={config.randomSeed}
                onChange={handleSeedChange}
                min={0}
                max={9999}
                disabled={!hasInput}
                className="flex-1 h-10 bg-white/5 border-white/10"
                placeholder="42"
              />
              <button
                onClick={handleRegenerateSeed}
                disabled={!hasInput}
                className={cn(
                  "w-10 h-10 flex items-center justify-center rounded-lg",
                  "bg-white/5 border border-white/10",
                  "hover:bg-blue-500/10 hover:border-blue-500 transition-colors",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
                title="Generate new random seed"
              >
                <RefreshCw className="w-4 h-4 text-blue-400" />
              </button>
            </div>
            <p className="text-[11px] text-zinc-500 mt-1">
              Set for reproducibility
            </p>
          </div>
        </div>
      </CollapsibleSection>

      {/* Section 4: Preview */}
      {hasInput && (
        <CollapsibleSection title="Split Preview" defaultOpen={true}>
          {/* Visual Split Bar */}
          <div className="mb-4">
            <div className="flex w-full h-6 rounded-xl overflow-hidden">
              <div
                className="bg-blue-500 transition-all duration-200"
                style={{ width: `${100 - localTestSize}%` }}
              />
              <div
                className="bg-amber-500 transition-all duration-200"
                style={{ width: `${localTestSize}%` }}
              />
            </div>
          </div>

          {/* Original Dataset */}
          <div className="flex items-center gap-2 mb-4">
            <Database className="w-4 h-4 text-zinc-500" />
            <span className="text-[13px] text-zinc-400">
              Original Dataset: {config.totalRows} rows
            </span>
          </div>

          {/* After Split */}
          <div className="space-y-2 mb-4">
            <p className="text-xs text-zinc-500 uppercase tracking-wider">
              After Split:
            </p>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-sm">
                <span className="text-blue-400 font-medium">Train:</span>{" "}
                <span className="text-white">
                  {trainRows} rows ({100 - localTestSize}%)
                </span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-sm">
                <span className="text-amber-400 font-medium">Test:</span>{" "}
                <span className="text-white">
                  {testRows} rows ({localTestSize}%)
                </span>
              </span>
            </div>
          </div>

          {/* Class Distribution (if stratified) */}
          {config.stratify && config.classDistribution && (
            <div>
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
                Class Distribution:
              </p>
              <div className="space-y-1.5">
                {config.classDistribution.map((cls) => (
                  <div key={cls.name} className="text-[13px] text-zinc-300">
                    <span className="text-zinc-500">•</span> {cls.name}:{" "}
                    {cls.total} →{" "}
                    <span className="text-blue-400 font-semibold">
                      {cls.train}
                    </span>{" "}
                    /{" "}
                    <span className="text-amber-400 font-semibold">
                      {cls.test}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CollapsibleSection>
      )}

      {/* Section 5: Warnings */}
      {warnings.length > 0 && (
        <CollapsibleSection
          title="Warnings"
          defaultOpen={true}
          badge={warnings.length}
        >
          {warnings.map((warning, index) => (
            <WarningCard
              key={index}
              type={warning.type}
              title={warning.title}
              message={warning.message}
            />
          ))}
        </CollapsibleSection>
      )}
    </div>
  );
}
