"use client";

import { memo, useMemo } from "react";
import { Handle, Position } from "@xyflow/react";
import { Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { NodeStatus } from "./base-node";
import {
  type FeatureOperation,
  FEATURE_OPERATION_SHORT_NAMES,
} from "./feature-engineering-types";

export interface FeatureEngineeringConfig {
  operations: FeatureOperation[];
  // Input dataset info (populated when connected)
  inputDatasetId: string | null;
  inputDatasetName: string | null;
  totalRows: number | null;
  inputColumns: number | null;
  columns: Array<{
    name: string;
    type: "numeric" | "categorical" | "datetime";
    missing?: number;
  }> | null;
  [key: string]: unknown;
}

export interface FeatureEngineeringNodeData {
  config: FeatureEngineeringConfig;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface FeatureEngineeringNodeProps {
  data: FeatureEngineeringNodeData;
  selected?: boolean;
}

// Default config
export const defaultFeatureEngineeringConfig: FeatureEngineeringConfig = {
  operations: [],
  inputDatasetId: null,
  inputDatasetName: null,
  totalRows: null,
  inputColumns: null,
  columns: null,
};

function FeatureEngineeringNodeComponent({
  data,
  selected,
}: FeatureEngineeringNodeProps) {
  const nodeData = data;
  const config = nodeData.config || defaultFeatureEngineeringConfig;

  // Collect all warnings from operations
  const allWarnings = useMemo(() => {
    return config.operations.flatMap((op) => op.warnings);
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

  // Determine node status
  const status: NodeStatus = useMemo((): NodeStatus => {
    if (!config.inputDatasetId) return "not-configured";
    if (config.operations.length === 0) return "not-configured";

    const hasErrors = allWarnings.some((w) => w.type === "error");
    if (hasErrors) return "error";

    const hasWarnings = allWarnings.some((w) => w.type === "warning");
    if (hasWarnings) return "partial";

    return "ready";
  }, [config, allWarnings]);

  // Generate summary lines
  const summaryLines = useMemo(() => {
    if (!config.inputDatasetId) {
      return ["No input connected"];
    }

    if (config.operations.length === 0) {
      return ["No features created"];
    }

    // Line 1: Column transformation (5 → 12 columns)
    const inputCols = config.inputColumns || 0;
    const outputCols = outputColumns || inputCols;
    const line1 = `${inputCols} → ${outputCols} columns`;

    // Line 2: Operation count
    const line2 = `${config.operations.length} operation${config.operations.length !== 1 ? "s" : ""}`;

    // Line 3: Status
    const hasErrors = allWarnings.some((w) => w.type === "error");
    const hasWarnings = allWarnings.some((w) => w.type === "warning");

    let line3 = "✓ Ready";
    if (hasErrors) {
      line3 = "✗ Has errors";
    } else if (hasWarnings) {
      line3 = "⚠ Needs review";
    }

    return [line1, line2, line3];
  }, [config, allWarnings, outputColumns]);

  // Status-based border color
  const borderColor = useMemo(() => {
    const statusColorMap: Record<NodeStatus, string> = {
      "not-configured": "border-zinc-600",
      partial: "border-amber-500",
      ready: "border-green-500",
      running: "border-blue-500 animate-pulse-border",
      error: "border-red-500",
    };
    return statusColorMap[status] || "border-zinc-600";
  }, [status]);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    nodeData.onDelete?.();
  };

  return (
    <div
      className={cn(
        "relative w-[220px] min-h-[60px]",
        "bg-[rgba(30,30,30,0.95)] backdrop-blur-sm",
        "border-2 rounded-xl",
        "shadow-[0_4px_20px_rgba(0,0,0,0.4)]",
        "transition-all duration-200",
        borderColor,
        selected && "ring-2 ring-blue-500 ring-offset-2 ring-offset-zinc-950"
      )}
    >
      {/* Input Handle (left center) */}
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        className="!w-2 !h-2 !bg-blue-500 !border-2 !border-[rgba(30,30,30,0.95)]"
        style={{ top: "50%" }}
      />

      {/* Output Handle (right center) */}
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="!w-2 !h-2 !bg-blue-500 !border-2 !border-[rgba(30,30,30,0.95)]"
        style={{ top: "50%" }}
      />

      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-base">🔧</span>
          <span className="text-sm font-semibold text-white truncate">
            Feature Eng.
          </span>
        </div>
        <div className="flex items-center gap-1">
          {/* Status indicator */}
          <div
            className={cn("w-2 h-2 rounded-full", {
              "bg-green-500": status === "ready",
              "bg-zinc-500": status === "not-configured",
              "bg-amber-500": status === "partial",
              "bg-blue-500": status === "running",
              "bg-red-500": status === "error",
            })}
          />
          {/* Delete button */}
          <button
            onClick={handleDelete}
            className="w-6 h-6 flex items-center justify-center rounded hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100 hover:!opacity-100"
          >
            <Trash2 className="w-3.5 h-3.5 text-zinc-400 hover:text-red-400" />
          </button>
        </div>
      </div>

      {/* Body - Summary Lines */}
      <div className="px-3 py-2 space-y-0.5">
        {summaryLines.map((line, index) => (
          <p
            key={index}
            className={cn(
              "text-xs truncate",
              index === summaryLines.length - 1 && line.startsWith("✓")
                ? "text-green-400"
                : index === summaryLines.length - 1 && line.startsWith("✗")
                  ? "text-red-400"
                  : index === summaryLines.length - 1 && line.startsWith("⚠")
                    ? "text-amber-400"
                    : "text-zinc-400"
            )}
          >
            {line}
          </p>
        ))}
      </div>
    </div>
  );
}

export const FeatureEngineeringNode = memo(FeatureEngineeringNodeComponent);
