"use client";

import { memo } from "react";
import { BaseNode, type BaseNodeData, type NodeStatus } from "./base-node";

export interface DatasetConfig {
  datasetId: string | null;
  datasetName: string | null;
  isSample: boolean;
  targetColumn: string | null;
  problemType: string | null;
  rows?: number;
  columns?: number;
  error?: {
    type: "not_found" | "load_failed" | "too_large";
    message: string;
  };
  [key: string]: unknown;
}

export interface DatasetNodeData {
  config: DatasetConfig;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface DatasetNodeProps {
  data: DatasetNodeData;
  selected?: boolean;
}

function generateSummaryLines(config: DatasetConfig): string[] {
  // Error state
  if (config.error) {
    return ["⚠ Failed to load", config.error.message];
  }

  // Not configured state
  if (!config.datasetId || !config.datasetName) {
    return ["No dataset selected"];
  }

  // Ready state
  const icon = config.isSample ? "🎓" : "📄";
  const filename = `${icon} ${config.datasetName}`;
  const target = config.targetColumn
    ? `Target: ${config.targetColumn}`
    : "No target";
  const status = "✓ Ready to use";

  return [filename, target, status];
}

function getNodeStatus(config: DatasetConfig): NodeStatus {
  if (config.error) {
    return "error";
  }
  if (!config.datasetId) {
    return "not-configured";
  }
  return "ready";
}

function DatasetNodeComponent({ data, selected }: DatasetNodeProps) {
  const { config, onDelete } = data;

  const baseNodeData: BaseNodeData = {
    icon: "📊",
    title: "Dataset Node",
    summaryLines: generateSummaryLines(config),
    status: getNodeStatus(config),
    showInputHandle: false,
    showOutputHandle: true,
    onDelete,
  };

  return <BaseNode data={baseNodeData} selected={selected} />;
}

export const DatasetNode = memo(DatasetNodeComponent);
