"use client";

import { useState, useMemo, useCallback } from "react";
import {
  ChevronDown,
  ChevronRight,
  Plus,
  AlertCircle,
  GripVertical,
  ChevronUp,
  Settings,
  X,
  AlertTriangle,
  Lightbulb,
  Info,
  Database,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  OPERATION_TYPES,
  OPERATION_NAMES,
  OPERATION_CATEGORIES,
  DEFAULT_CONFIGS,
  createOperation,
  type Operation,
  type OperationType,
  type FillMissingConfig,
  type ScaleConfig,
  type EncodeConfig,
  type RemoveDuplicatesConfig,
  type RemoveOutliersConfig,
  type DropColumnsConfig,
} from "./preprocessing-types";
import type { PreprocessingConfig } from "./preprocessing-node";

interface PreprocessingInspectorProps {
  nodeId: string;
  config: PreprocessingConfig;
  onConfigChange: (config: Partial<PreprocessingConfig>) => void;
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
    <div className="border-b border-purple-700/30 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-purple-700/20 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isOpen ? (
            <ChevronDown className="w-4 h-4 text-purple-300/70" />
          ) : (
            <ChevronRight className="w-4 h-4 text-purple-300/70" />
          )}
          <span className="text-xs font-semibold text-white/90 uppercase tracking-wider">
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
  operation: Operation;
  index: number;
  isFirst: boolean;
  isLast: boolean;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onDelete: () => void;
  onToggleExpand: () => void;
  onConfigChange: (config: Operation["config"]) => void;
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
        <button onClick={onToggleExpand} className="p-0.5 hover:bg-white/10 rounded">
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
          <button
            onClick={onDelete}
            className="p-1 rounded hover:bg-red-500/20"
          >
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
  operation: Operation;
  onConfigChange: (config: Operation["config"]) => void;
}) {
  const config = operation.config;

  // Fill Missing Values Configuration
  if (operation.type === OPERATION_TYPES.FILL_MISSING) {
    const fillConfig = config as FillMissingConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Strategy</label>
          <div className="grid grid-cols-2 gap-2">
            {(["mean", "median", "mode", "constant"] as const).map((strategy) => (
              <button
                key={strategy}
                onClick={() => onConfigChange({ ...fillConfig, strategy })}
                className={cn(
                  "px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  fillConfig.strategy === strategy
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {strategy.charAt(0).toUpperCase() + strategy.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Apply to</label>
          <select
            value={typeof fillConfig.columns === "string" ? fillConfig.columns : "custom"}
            onChange={(e) =>
              onConfigChange({ ...fillConfig, columns: e.target.value as "all_numeric" | "all_categorical" })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="all_numeric">All numeric columns</option>
            <option value="all_categorical">All categorical columns</option>
          </select>
        </div>
      </div>
    );
  }

  // Scale Configuration
  if (
    operation.type === OPERATION_TYPES.SCALE_STANDARD ||
    operation.type === OPERATION_TYPES.SCALE_MINMAX ||
    operation.type === OPERATION_TYPES.SCALE_ROBUST
  ) {
    const scaleConfig = config as ScaleConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Apply to</label>
          <select
            value={typeof scaleConfig.columns === "string" ? scaleConfig.columns : "custom"}
            onChange={(e) =>
              onConfigChange({ ...scaleConfig, columns: e.target.value as "all_numeric" })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="all_numeric">All numeric columns</option>
          </select>
        </div>
        {operation.type === OPERATION_TYPES.SCALE_STANDARD && (
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={scaleConfig.withMean ?? true}
                onChange={(e) =>
                  onConfigChange({ ...scaleConfig, withMean: e.target.checked })
                }
                className="rounded bg-white/5 border-white/10"
              />
              <span className="text-xs text-zinc-300">Center data (subtract mean)</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={scaleConfig.withStd ?? true}
                onChange={(e) =>
                  onConfigChange({ ...scaleConfig, withStd: e.target.checked })
                }
                className="rounded bg-white/5 border-white/10"
              />
              <span className="text-xs text-zinc-300">Scale to unit variance</span>
            </label>
          </div>
        )}
      </div>
    );
  }

  // Encode Configuration
  if (
    operation.type === OPERATION_TYPES.ENCODE_ONEHOT ||
    operation.type === OPERATION_TYPES.ENCODE_LABEL
  ) {
    const encodeConfig = config as EncodeConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Apply to</label>
          <select
            value={typeof encodeConfig.columns === "string" ? encodeConfig.columns : "custom"}
            onChange={(e) =>
              onConfigChange({ ...encodeConfig, columns: e.target.value as "all_categorical" })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="all_categorical">All categorical columns</option>
          </select>
        </div>
        {operation.type === OPERATION_TYPES.ENCODE_ONEHOT && (
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={encodeConfig.dropFirst ?? true}
              onChange={(e) =>
                onConfigChange({ ...encodeConfig, dropFirst: e.target.checked })
              }
              className="rounded bg-white/5 border-white/10"
            />
            <span className="text-xs text-zinc-300">Drop first category (avoid multicollinearity)</span>
          </label>
        )}
      </div>
    );
  }

  // Remove Duplicates Configuration
  if (operation.type === OPERATION_TYPES.REMOVE_DUPLICATES) {
    const dupConfig = config as RemoveDuplicatesConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Consider columns</label>
          <select
            value={typeof dupConfig.columns === "string" ? dupConfig.columns : "custom"}
            onChange={(e) =>
              onConfigChange({ ...dupConfig, columns: e.target.value as "all" })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="all">All columns</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Keep strategy</label>
          <div className="flex gap-2">
            {(["first", "last"] as const).map((keep) => (
              <button
                key={keep}
                onClick={() => onConfigChange({ ...dupConfig, keep })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  dupConfig.keep === keep
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                Keep {keep}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Remove Outliers Configuration
  if (
    operation.type === OPERATION_TYPES.REMOVE_OUTLIERS_IQR ||
    operation.type === OPERATION_TYPES.REMOVE_OUTLIERS_ZSCORE
  ) {
    const outlierConfig = config as RemoveOutliersConfig;
    return (
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Apply to</label>
          <select
            value={typeof outlierConfig.columns === "string" ? outlierConfig.columns : "custom"}
            onChange={(e) =>
              onConfigChange({ ...outlierConfig, columns: e.target.value as "all_numeric" })
            }
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          >
            <option value="all_numeric">All numeric columns</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">
            {operation.type === OPERATION_TYPES.REMOVE_OUTLIERS_IQR
              ? "IQR Multiplier"
              : "Z-score Threshold"}
          </label>
          <input
            type="number"
            value={outlierConfig.threshold}
            onChange={(e) =>
              onConfigChange({ ...outlierConfig, threshold: parseFloat(e.target.value) || 1.5 })
            }
            step={0.5}
            min={0.5}
            max={10}
            className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-2">Action</label>
          <div className="flex gap-2">
            {(["remove", "clip"] as const).map((action) => (
              <button
                key={action}
                onClick={() => onConfigChange({ ...outlierConfig, action })}
                className={cn(
                  "flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                  "border",
                  outlierConfig.action === action
                    ? "bg-blue-500/20 border-blue-500 text-blue-400"
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10"
                )}
              >
                {action === "remove" ? "Remove rows" : "Clip values"}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Drop Columns Configuration
  if (operation.type === OPERATION_TYPES.DROP_COLUMNS) {
    return (
      <div className="space-y-3">
        <p className="text-xs text-zinc-500">
          Select columns to drop in the column selection below.
        </p>
      </div>
    );
  }

  return null;
}

// Add Operation Dropdown
function AddOperationDropdown({
  onAddOperation,
}: {
  onAddOperation: (type: OperationType) => void;
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
        <ChevronDown className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")} />
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
            {Object.entries(OPERATION_CATEGORIES).map(([category, { icon, operations }]) => (
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
                    {OPERATION_NAMES[opType]}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export function PreprocessingInspector({
  nodeId,
  config,
  onConfigChange,
}: PreprocessingInspectorProps) {
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

  // Handlers
  const handleAddOperation = useCallback(
    (type: OperationType) => {
      const newOperation = createOperation(type, config.operations.length);
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
    (operationId: string, newConfig: Operation["config"]) => {
      const updated = config.operations.map((op) =>
        op.id === operationId ? { ...op, config: newConfig } : op
      );
      onConfigChange({ operations: updated });
    },
    [config.operations, onConfigChange]
  );

  const handleQuickAdd = useCallback(
    (type: OperationType) => {
      handleAddOperation(type);
    },
    [handleAddOperation]
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
            Connect a Dataset or Split Node to configure preprocessing.
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
                  {config.totalRows} rows • {config.columns?.length || 0} columns
                </p>
                {config.columns && (
                  <p className="text-xs text-zinc-500 mt-0.5">
                    {config.columns.filter((c) => c.type === "numeric").length} numeric,{" "}
                    {config.columns.filter((c) => c.type === "categorical").length} categorical
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-zinc-500 italic">No dataset connected</p>
        )}
      </CollapsibleSection>

      {/* Section 2: Operations Pipeline */}
      <CollapsibleSection title="Operations Pipeline" defaultOpen={true}>
        <div className={cn(!hasInput && "opacity-50 pointer-events-none")}>
          {config.operations.length === 0 ? (
            /* Empty State */
            <div className="text-center py-6">
              <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🧹</span>
              </div>
              <p className="text-sm text-zinc-400 mb-1">No preprocessing configured</p>
              <p className="text-xs text-zinc-500 mb-4 px-4">
                Preprocessing transforms your data to improve model performance.
              </p>

              <AddOperationDropdown onAddOperation={handleAddOperation} />

              <div className="mt-4">
                <p className="text-xs text-zinc-500 mb-2">Quick Add:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <button
                    onClick={() => handleQuickAdd(OPERATION_TYPES.FILL_MISSING)}
                    className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-zinc-400 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    Fill Missing
                  </button>
                  <button
                    onClick={() => handleQuickAdd(OPERATION_TYPES.SCALE_STANDARD)}
                    className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-zinc-400 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    Scale
                  </button>
                  <button
                    onClick={() => handleQuickAdd(OPERATION_TYPES.ENCODE_ONEHOT)}
                    className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-zinc-400 hover:bg-white/10 hover:text-white transition-colors"
                  >
                    Encode
                  </button>
                </div>
              </div>
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
                Input: {config.totalRows} rows × {config.columns?.length || 0} columns
              </span>
            </div>

            <div className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
                Transformations:
              </p>
              <ul className="space-y-1">
                {config.operations.map((op, idx) => (
                  <li key={op.id} className="text-xs text-zinc-300 flex items-center gap-2">
                    <span className="text-blue-400">•</span>
                    {op.name}
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex items-center gap-2 text-xs text-green-400">
              <span className="text-lg">✓</span>
              <span>
                Output: {config.totalRows} rows × {config.columns?.length || 0} columns
                (estimated)
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
