"use client";

import { useState, useMemo, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  Plus,
  AlertCircle,
  GripVertical,
  ChevronUp,
  X,
  AlertTriangle,
  Lightbulb,
  Database,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  FEATURE_OPERATION_TYPES,
  FEATURE_OPERATION_NAMES,
  FEATURE_OPERATION_CATEGORIES,
  FEATURE_DEFAULT_CONFIGS,
  createFeatureOperation,
  type FeatureOperation,
  type FeatureOperationType,
  type LogTransformConfig,
  type PowerTransformConfig,
  type ExponentialTransformConfig,
  type ReciprocalTransformConfig,
  type PolynomialConfig,
  type InteractionConfig,
  type RatioConfig,
  type DifferenceConfig,
  type SumConfig,
  type BinningWidthConfig,
  type BinningFrequencyConfig,
  type BinningQuantileConfig,
} from "./feature-engineering-types";
import type { FeatureEngineeringConfig } from "./feature-engineering-node";

interface FeatureEngineeringInspectorProps {
  nodeId: string;
  config: FeatureEngineeringConfig;
  onConfigChange: (config: Partial<FeatureEngineeringConfig>) => void;
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
  type: "error" | "warning" | "tip";
  title: string;
  message: string;
}) {
  const styles = {
    error: {
      bg: "bg-red-500/5",
      border: "border-l-red-500",
      icon: <AlertTriangle className="w-4 h-4 text-red-500" />,
    },
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

// Operation Card Component
function OperationCard({
  operation,
  index,
  isFirst,
  isLast,
  onMoveUp,
  onMoveDown,
  onDelete,
  onToggleExpand,
  onConfigChange,
}: {
  operation: FeatureOperation;
  index: number;
  isFirst: boolean;
  isLast: boolean;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onDelete: () => void;
  onToggleExpand: () => void;
  onConfigChange: (config: FeatureOperation["config"]) => void;
}) {
  const hasWarnings = operation.warnings.length > 0;
  const hasErrors = operation.warnings.some((w) => w.type === "error");

  return (
    <div
      className={cn(
        "rounded-lg border mb-2 last:mb-0 transition-all",
        "bg-white/[0.03]",
        hasErrors
          ? "border-red-500/50"
          : hasWarnings
            ? "border-amber-500/50"
            : "border-white/[0.08]"
      )}
    >
      {/* Card Header */}
      <div className="flex items-center gap-2 px-3 py-2">
        {/* Drag Handle */}
        <GripVertical className="w-4 h-4 text-zinc-600 cursor-grab hover:text-zinc-400" />

        {/* Expand Toggle */}
        <button
          onClick={onToggleExpand}
          className="p-0.5 hover:bg-white/10 rounded"
        >
          {operation.expanded ? (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-zinc-400" />
          )}
        </button>

        {/* Number and Name */}
        <span className="text-[13px] text-zinc-500 font-bold">{index + 1}.</span>
        <span className="text-sm font-semibold text-white flex-1 truncate">
          {operation.name}
        </span>

        {/* Warning Icon */}
        {hasWarnings && (
          <AlertTriangle
            className={cn(
              "w-4 h-4",
              hasErrors ? "text-red-500" : "text-amber-500"
            )}
          />
        )}

        {/* Action Buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={onMoveUp}
            disabled={isFirst}
            className={cn(
              "p-1 rounded hover:bg-white/10",
              isFirst && "opacity-30 cursor-not-allowed"
            )}
          >
            <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />
          </button>
          <button
            onClick={onMoveDown}
            disabled={isLast}
            className={cn(
              "p-1 rounded hover:bg-white/10",
              isLast && "opacity-30 cursor-not-allowed"
            )}
          >
            <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
          </button>
          <button onClick={onDelete} className="p-1 rounded hover:bg-red-500/20">
            <X className="w-3.5 h-3.5 text-zinc-500 hover:text-red-400" />
          </button>
        </div>
      </div>

      {/* Expanded Configuration */}
      {operation.expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-white/5">
          <OperationConfigPanel
            operation={operation}
            onConfigChange={onConfigChange}
          />
        </div>
      )}
    </div>
  );
}

// Operation Configuration Panel
function OperationConfigPanel({
  operation,
  onConfigChange,
}: {
  operation: FeatureOperation;
  onConfigChange: (config: FeatureOperation["config"]) => void;
}) {
  const config = operation.config;

  // Log Transform Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.LOG_TRANSFORM) {
    const logConfig = config as LogTransformConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Transform Type</label>
          <div className="grid grid-cols-2 gap-2">
            {(["natural", "log10", "log2", "log1p"] as const).map((type) => (
              <button
                key={type}
                onClick={() => onConfigChange({ ...logConfig, logType: type })}
                className={cn(
                  "px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  logConfig.logType === type
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {type === "natural" ? "ln(x)" : type === "log1p" ? "ln(1+x)" : type}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Handle Negative Values
          </label>
          <select
            value={logConfig.handleNegative}
            onChange={(e) =>
              onConfigChange({
                ...logConfig,
                handleNegative: e.target.value as "skip" | "absolute" | "error",
              })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="skip">Skip column</option>
            <option value="absolute">Take absolute value</option>
            <option value="error">Error</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Suffix</label>
          <input
            type="text"
            value={logConfig.suffix}
            onChange={(e) =>
              onConfigChange({ ...logConfig, suffix: e.target.value })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
            placeholder="_log"
          />
        </div>
      </div>
    );
  }

  // Power Transform Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.POWER_TRANSFORM) {
    const powerConfig = config as PowerTransformConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Power</label>
          <div className="grid grid-cols-2 gap-2">
            {(["square", "cube", "sqrt"] as const).map((power) => (
              <button
                key={power}
                onClick={() => onConfigChange({ ...powerConfig, power })}
                className={cn(
                  "px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  powerConfig.power === power
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {power === "square" ? "x²" : power === "cube" ? "x³" : "√x"}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Handle Negative Values (for √x)
          </label>
          <select
            value={powerConfig.handleNegative}
            onChange={(e) =>
              onConfigChange({
                ...powerConfig,
                handleNegative: e.target.value as "skip" | "absolute" | "error",
              })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="skip">Skip column</option>
            <option value="absolute">Take absolute value</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>
    );
  }

  // Exponential Transform Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.EXPONENTIAL_TRANSFORM) {
    const expConfig = config as ExponentialTransformConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Handle Large Values
          </label>
          <select
            value={expConfig.handleLarge}
            onChange={(e) =>
              onConfigChange({
                ...expConfig,
                handleLarge: e.target.value as "clip" | "allow" | "error",
              })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="clip">Clip at 1e10</option>
            <option value="allow">Allow overflow</option>
            <option value="error">Error</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Suffix</label>
          <input
            type="text"
            value={expConfig.suffix}
            onChange={(e) =>
              onConfigChange({ ...expConfig, suffix: e.target.value })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
            placeholder="_exp"
          />
        </div>
      </div>
    );
  }

  // Reciprocal Transform Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.RECIPROCAL_TRANSFORM) {
    const recipConfig = config as ReciprocalTransformConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Handle Zero Values
          </label>
          <select
            value={recipConfig.handleZero}
            onChange={(e) =>
              onConfigChange({
                ...recipConfig,
                handleZero: e.target.value as "nan" | "skip" | "error",
              })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="nan">Replace with NaN</option>
            <option value="skip">Skip column</option>
            <option value="error">Error</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Add Constant Before Reciprocal
          </label>
          <input
            type="number"
            value={recipConfig.addConstant}
            onChange={(e) =>
              onConfigChange({
                ...recipConfig,
                addConstant: parseFloat(e.target.value) || 0,
              })
            }
            step={0.1}
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
            placeholder="0"
          />
        </div>
      </div>
    );
  }

  // Polynomial Features Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.POLYNOMIAL) {
    const polyConfig = config as PolynomialConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Degree</label>
          <div className="flex gap-2">
            {([2, 3] as const).map((degree) => (
              <button
                key={degree}
                onClick={() => onConfigChange({ ...polyConfig, degree })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  polyConfig.degree === degree
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {degree === 2 ? "2 (x²)" : "3 (x², x³)"}
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={polyConfig.includeX2}
              onChange={(e) =>
                onConfigChange({ ...polyConfig, includeX2: e.target.checked })
              }
              className="rounded bg-white/5 border-white/10"
            />
            <span className="text-xs text-zinc-300">Include x² terms</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={polyConfig.includeX3}
              onChange={(e) =>
                onConfigChange({ ...polyConfig, includeX3: e.target.checked })
              }
              className="rounded bg-white/5 border-white/10"
            />
            <span className="text-xs text-zinc-300">Include x³ terms</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={polyConfig.includeBias}
              onChange={(e) =>
                onConfigChange({ ...polyConfig, includeBias: e.target.checked })
              }
              className="rounded bg-white/5 border-white/10"
            />
            <span className="text-xs text-zinc-300">Include bias term</span>
          </label>
        </div>
      </div>
    );
  }

  // Interaction Features Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.INTERACTION) {
    const interConfig = config as InteractionConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Interaction Degree
          </label>
          <div className="flex gap-2">
            {([2, 3] as const).map((degree) => (
              <button
                key={degree}
                onClick={() => onConfigChange({ ...interConfig, degree })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  interConfig.degree === degree
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {degree === 2 ? "Pairwise (x₁ × x₂)" : "Triplets"}
              </button>
            ))}
          </div>
        </div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={interConfig.includePolynomial}
            onChange={(e) =>
              onConfigChange({
                ...interConfig,
                includePolynomial: e.target.checked,
              })
            }
            className="rounded bg-white/5 border-white/10"
          />
          <span className="text-xs text-zinc-300">
            Include polynomial interactions
          </span>
        </label>
      </div>
    );
  }

  // Ratio Features Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.RATIO) {
    const ratioConfig = config as RatioConfig;
    return (
      <div className="space-y-3">
        <p className="text-xs text-zinc-500">
          Create ratio features (x₁ / x₂). Select columns after connecting a
          dataset.
        </p>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Handle Zero Denominator
          </label>
          <select
            value={ratioConfig.handleZero}
            onChange={(e) =>
              onConfigChange({
                ...ratioConfig,
                handleZero: e.target.value as "nan" | "skip" | "error",
              })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="nan">Replace with NaN</option>
            <option value="skip">Skip</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>
    );
  }

  // Difference Features Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.DIFFERENCE) {
    const diffConfig = config as DifferenceConfig;
    return (
      <div className="space-y-3">
        <p className="text-xs text-zinc-500">
          Create difference features (x₁ - x₂). Select columns after connecting
          a dataset.
        </p>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={diffConfig.includeAbsolute}
            onChange={(e) =>
              onConfigChange({
                ...diffConfig,
                includeAbsolute: e.target.checked,
              })
            }
            className="rounded bg-white/5 border-white/10"
          />
          <span className="text-xs text-zinc-300">
            Also create absolute difference
          </span>
        </label>
      </div>
    );
  }

  // Sum Features Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.SUM) {
    const sumConfig = config as SumConfig;
    return (
      <div className="space-y-3">
        <p className="text-xs text-zinc-500">
          Sum selected columns into a single feature.
        </p>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Feature Name</label>
          <input
            type="text"
            value={sumConfig.featureName}
            onChange={(e) =>
              onConfigChange({ ...sumConfig, featureName: e.target.value })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
            placeholder="sum_selected"
          />
        </div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={sumConfig.includeAverage}
            onChange={(e) =>
              onConfigChange({ ...sumConfig, includeAverage: e.target.checked })
            }
            className="rounded bg-white/5 border-white/10"
          />
          <span className="text-xs text-zinc-300">Also create average</span>
        </label>
      </div>
    );
  }

  // Binning Width Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.BINNING_WIDTH) {
    const binConfig = config as BinningWidthConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Number of Bins</label>
          <input
            type="number"
            value={binConfig.bins}
            onChange={(e) =>
              onConfigChange({ ...binConfig, bins: parseInt(e.target.value) || 5 })
            }
            min={2}
            max={20}
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Encoding</label>
          <div className="flex gap-2">
            {(["ordinal", "onehot"] as const).map((encoding) => (
              <button
                key={encoding}
                onClick={() => onConfigChange({ ...binConfig, encoding })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  binConfig.encoding === encoding
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {encoding === "ordinal" ? "Ordinal (0,1,2...)" : "One-hot"}
              </button>
            ))}
          </div>
        </div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={binConfig.keepOriginal}
            onChange={(e) =>
              onConfigChange({ ...binConfig, keepOriginal: e.target.checked })
            }
            className="rounded bg-white/5 border-white/10"
          />
          <span className="text-xs text-zinc-300">Keep original column</span>
        </label>
      </div>
    );
  }

  // Binning Frequency Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.BINNING_FREQUENCY) {
    const binConfig = config as BinningFrequencyConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Number of Bins (Quantiles)
          </label>
          <input
            type="number"
            value={binConfig.bins}
            onChange={(e) =>
              onConfigChange({ ...binConfig, bins: parseInt(e.target.value) || 4 })
            }
            min={2}
            max={20}
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Encoding</label>
          <div className="flex gap-2">
            {(["ordinal", "onehot"] as const).map((encoding) => (
              <button
                key={encoding}
                onClick={() => onConfigChange({ ...binConfig, encoding })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  binConfig.encoding === encoding
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {encoding === "ordinal" ? "Ordinal" : "One-hot"}
              </button>
            ))}
          </div>
        </div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={binConfig.keepOriginal}
            onChange={(e) =>
              onConfigChange({ ...binConfig, keepOriginal: e.target.checked })
            }
            className="rounded bg-white/5 border-white/10"
          />
          <span className="text-xs text-zinc-300">Keep original column</span>
        </label>
      </div>
    );
  }

  // Binning Quantile Configuration
  if (operation.type === FEATURE_OPERATION_TYPES.BINNING_QUANTILE) {
    const binConfig = config as BinningQuantileConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            Quantiles (comma-separated)
          </label>
          <input
            type="text"
            value={binConfig.quantiles.join(", ")}
            onChange={(e) => {
              const quantiles = e.target.value
                .split(",")
                .map((q) => parseFloat(q.trim()))
                .filter((q) => !isNaN(q) && q > 0 && q < 1);
              onConfigChange({ ...binConfig, quantiles });
            }}
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
            placeholder="0.25, 0.5, 0.75"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Encoding</label>
          <div className="flex gap-2">
            {(["ordinal", "onehot"] as const).map((encoding) => (
              <button
                key={encoding}
                onClick={() => onConfigChange({ ...binConfig, encoding })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  binConfig.encoding === encoding
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {encoding === "ordinal" ? "Ordinal" : "One-hot"}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return null;
}

// Add Operation Dropdown
function AddOperationDropdown({
  onAddOperation,
}: {
  onAddOperation: (type: FeatureOperationType) => void;
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg",
          "bg-blue-500/10 border border-blue-500 text-blue-400",
          "hover:bg-blue-500/20 transition-colors",
          "text-sm font-medium"
        )}
      >
        <Plus className="w-4 h-4" />
        Add Operation
        <ChevronDown
          className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")}
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown Menu */}
          <div
            className={cn(
              "absolute top-full left-0 right-0 mt-1 z-50",
              "bg-[rgba(20,20,20,0.98)] border border-white/10 rounded-lg",
              "shadow-[0_8px_32px_rgba(0,0,0,0.4)]",
              "max-h-[400px] overflow-y-auto custom-scrollbar"
            )}
          >
            {Object.entries(FEATURE_OPERATION_CATEGORIES).map(
              ([category, { icon, operations }]) => (
                <div key={category}>
                  {/* Category Header */}
                  <div className="px-3 py-2 bg-white/[0.02] border-b border-white/5">
                    <span className="text-[11px] text-zinc-500 uppercase tracking-wider font-semibold">
                      {icon} {category}
                    </span>
                  </div>

                  {/* Operations */}
                  {operations.map((opType) => (
                    <button
                      key={opType}
                      onClick={() => {
                        onAddOperation(opType);
                        setIsOpen(false);
                      }}
                      className={cn(
                        "w-full text-left px-4 py-2.5 pl-6",
                        "text-[13px] text-zinc-300",
                        "hover:bg-blue-500/10 hover:text-white",
                        "transition-colors"
                      )}
                    >
                      {FEATURE_OPERATION_NAMES[opType]}
                    </button>
                  ))}
                </div>
              )
            )}
          </div>
        </>
      )}
    </div>
  );
}

export function FeatureEngineeringInspector({
  nodeId,
  config,
  onConfigChange,
}: FeatureEngineeringInspectorProps) {
  // Collect all warnings from operations
  const allWarnings = useMemo(() => {
    return config.operations.flatMap((op, idx) =>
      op.warnings.map((w) => ({
        ...w,
        operationName: op.name,
        operationIndex: idx,
      }))
    );
  }, [config.operations]);

  // Calculate output columns
  const outputColumns = useMemo(() => {
    if (!config.inputColumns) return null;
    let cols = config.inputColumns;
    config.operations.forEach((op) => {
      cols += op.newFeatures.length;
    });
    return cols;
  }, [config.inputColumns, config.operations]);

  // Handlers
  const handleAddOperation = useCallback(
    (type: FeatureOperationType) => {
      const newOperation = createFeatureOperation(type, config.operations.length);
      onConfigChange({
        operations: [...config.operations, newOperation],
      });
    },
    [config.operations, onConfigChange]
  );

  const handleRemoveOperation = useCallback(
    (operationId: string) => {
      const updated = config.operations
        .filter((op) => op.id !== operationId)
        .map((op, idx) => ({ ...op, order: idx }));
      onConfigChange({ operations: updated });
    },
    [config.operations, onConfigChange]
  );

  const handleMoveOperation = useCallback(
    (operationId: string, direction: "up" | "down") => {
      const index = config.operations.findIndex((op) => op.id === operationId);
      if (
        (direction === "up" && index === 0) ||
        (direction === "down" && index === config.operations.length - 1)
      ) {
        return;
      }

      const updated = [...config.operations];
      const swapIndex = direction === "up" ? index - 1 : index + 1;
      [updated[index], updated[swapIndex]] = [updated[swapIndex], updated[index]];

      const renumbered = updated.map((op, idx) => ({ ...op, order: idx }));
      onConfigChange({ operations: renumbered });
    },
    [config.operations, onConfigChange]
  );

  const handleToggleExpand = useCallback(
    (operationId: string) => {
      const updated = config.operations.map((op) =>
        op.id === operationId ? { ...op, expanded: !op.expanded } : op
      );
      onConfigChange({ operations: updated });
    },
    [config.operations, onConfigChange]
  );

  const handleOperationConfigChange = useCallback(
    (operationId: string, newConfig: FeatureOperation["config"]) => {
      const updated = config.operations.map((op) =>
        op.id === operationId ? { ...op, config: newConfig } : op
      );
      onConfigChange({ operations: updated });
    },
    [config.operations, onConfigChange]
  );

  const hasInput = !!config.inputDatasetId;

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
            Connect a Dataset, Split, or Preprocessing node to engineer features.
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
                  {config.totalRows} rows • {config.inputColumns || 0} columns
                </p>
                {config.columns && (
                  <p className="text-xs text-zinc-500 mt-0.5">
                    {config.columns.filter((c) => c.type === "numeric").length}{" "}
                    numeric,{" "}
                    {config.columns.filter((c) => c.type === "categorical").length}{" "}
                    categorical
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-zinc-500 italic">No dataset connected</p>
        )}
      </CollapsibleSection>

      {/* Section 2: Feature Operations */}
      <CollapsibleSection title="Feature Operations" defaultOpen={true}>
        <div className={cn(!hasInput && "opacity-50 pointer-events-none")}>
          {config.operations.length === 0 ? (
            /* Empty State */
            <div className="text-center py-6">
              <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🔧</span>
              </div>
              <p className="text-sm text-zinc-400 mb-1">
                No feature engineering configured
              </p>
              <p className="text-xs text-zinc-500 mb-4 px-4">
                Create new features from existing ones to improve model
                performance.
              </p>

              <AddOperationDropdown onAddOperation={handleAddOperation} />
            </div>
          ) : (
            /* Operations List */
            <div>
              <AddOperationDropdown onAddOperation={handleAddOperation} />

              <div className="mt-3 space-y-0">
                {config.operations.map((operation, index) => (
                  <OperationCard
                    key={operation.id}
                    operation={operation}
                    index={index}
                    isFirst={index === 0}
                    isLast={index === config.operations.length - 1}
                    onMoveUp={() => handleMoveOperation(operation.id, "up")}
                    onMoveDown={() => handleMoveOperation(operation.id, "down")}
                    onDelete={() => handleRemoveOperation(operation.id)}
                    onToggleExpand={() => handleToggleExpand(operation.id)}
                    onConfigChange={(newConfig) =>
                      handleOperationConfigChange(operation.id, newConfig)
                    }
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </CollapsibleSection>

      {/* Section 3: Preview */}
      {hasInput && config.operations.length > 0 && (
        <CollapsibleSection title="Preview" defaultOpen={true}>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <Database className="w-4 h-4" />
              <span>
                Input: {config.totalRows} rows × {config.inputColumns || 0}{" "}
                columns
              </span>
            </div>

            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
                Transformations:
              </p>
              <ul className="space-y-1">
                {config.operations.map((op) => (
                  <li
                    key={op.id}
                    className="text-xs text-zinc-300 flex items-center gap-2"
                  >
                    <span className="text-blue-400">•</span>
                    {op.name}
                    {op.newFeatures.length > 0 && (
                      <span className="text-zinc-500">
                        (+{op.newFeatures.length})
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex items-center gap-2 text-xs text-green-400">
              <span className="text-lg">✓</span>
              <span>
                Output: {config.totalRows} rows × {outputColumns || config.inputColumns}{" "}
                columns
              </span>
            </div>
          </div>
        </CollapsibleSection>
      )}

      {/* Section 4: Warnings */}
      {allWarnings.length > 0 && (
        <CollapsibleSection
          title="Warnings"
          defaultOpen={true}
          badge={allWarnings.length}
        >
          {allWarnings.map((warning, index) => (
            <WarningCard
              key={index}
              type={warning.type}
              title={`${warning.operationName}`}
              message={warning.message}
            />
          ))}
        </CollapsibleSection>
      )}
    </div>
  );
}
