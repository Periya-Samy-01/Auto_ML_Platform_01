"use client";

import { memo, useMemo } from "react";
import { BaseNode, type BaseNodeData, type NodeStatus } from "./base-node";
import {
  type Operation,
  OPERATION_SHORT_NAMES,
} from "./preprocessing-types";

export interface PreprocessingConfig {
  operations: Operation[];
  // Input dataset info (populated when connected)
  inputDatasetId: string | null;
  inputDatasetName: string | null;
  totalRows: number | null;
  columns: Array<{
    name: string;
    type: "numeric" | "categorical" | "datetime";
    missing?: number;
  }> | null;
  [key: string]: unknown;
}

export interface PreprocessingNodeData {
  config: PreprocessingConfig;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface PreprocessingNodeProps {
  data: PreprocessingNodeData;
  selected?: boolean;
}

// Default config
export const defaultPreprocessingConfig: PreprocessingConfig = {
  operations: [],
  inputDatasetId: null,
  inputDatasetName: null,
  totalRows: null,
  columns: null,
};

function generateSummaryLines(config: PreprocessingConfig): string[] {
  if (!config.inputDatasetId) {
    return ["No input connected"];
  }

  if (config.operations.length === 0) {
    return ["No operations added"];
  }

  const allWarnings = config.operations.flatMap((op) => op.warnings);

  // Line 1: Operation names (truncated to 3)
  const names = config.operations.slice(0, 3).map((op) => OPERATION_SHORT_NAMES[op.type]);
  let line1 = names.join(", ");
  if (config.operations.length > 3) {
    line1 += `, +${config.operations.length - 3} more`;
  }

  // Line 2: Operation count
  const line2 = `${config.operations.length} operation${config.operations.length !== 1 ? "s" : ""}`;

  // Line 3: Status
  const hasErrors = allWarnings.some((w) => w.type === "error");
  const hasWarnings = allWarnings.some((w) => w.type === "warning");

  let line3 = "Ready";
  if (hasErrors) {
    line3 = "Has errors";
  } else if (hasWarnings) {
    line3 = "Needs review";
  }

  return [line1, line2, line3];
}

function getNodeStatus(config: PreprocessingConfig): NodeStatus {
  if (!config.inputDatasetId) return "not-configured";
  if (config.operations.length === 0) return "not-configured";

  const allWarnings = config.operations.flatMap((op) => op.warnings);
  const hasErrors = allWarnings.some((w) => w.type === "error");
  if (hasErrors) return "error";

  const hasWarnings = allWarnings.some((w) => w.type === "warning");
  if (hasWarnings) return "partial";

  return "ready";
}

function PreprocessingNodeComponent({ data, selected }: PreprocessingNodeProps) {
  const { config = defaultPreprocessingConfig, onDelete } = data;

  const baseNodeData: BaseNodeData = {
    icon: "🧹",
    title: "Preprocessing",
    summaryLines: generateSummaryLines(config),
    status: getNodeStatus(config),
    showInputHandle: true,
    showOutputHandle: true,
    onDelete,
  };

  return <BaseNode data={baseNodeData} selected={selected} />;
}

export const PreprocessingNode = memo(PreprocessingNodeComponent);
