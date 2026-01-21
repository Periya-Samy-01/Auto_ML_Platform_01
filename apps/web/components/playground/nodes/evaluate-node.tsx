"use client";

import { memo } from "react";
import { BaseNode, type BaseNodeData, type NodeStatus } from "./base-node";

export interface EvaluateConfig {
  selectedMetrics: string[];
  showConfidenceIntervals: boolean;
  compareWithBaseline: boolean;
  [key: string]: unknown;
}

export interface EvaluateNodeData {
  config: EvaluateConfig;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface EvaluateNodeProps {
  data: EvaluateNodeData;
  selected?: boolean;
}

export const defaultEvaluateConfig: EvaluateConfig = {
  selectedMetrics: [],
  showConfidenceIntervals: false,
  compareWithBaseline: false,
};

function generateSummaryLines(config: EvaluateConfig): string[] {
  if (config.selectedMetrics.length === 0) {
    return ["No metrics selected"];
  }

  const lines: string[] = [];

  // Show metrics count
  lines.push(`${config.selectedMetrics.length} metrics selected`);

  // Show first few metrics
  const displayMetrics = config.selectedMetrics.slice(0, 3);
  lines.push(displayMetrics.join(", "));

  if (config.selectedMetrics.length > 3) {
    lines.push(`+${config.selectedMetrics.length - 3} more`);
  }

  return lines;
}

function getNodeStatus(config: EvaluateConfig): NodeStatus {
  if (config.selectedMetrics.length === 0) {
    return "not-configured";
  }
  return "ready";
}

function EvaluateNodeComponent({ data, selected }: EvaluateNodeProps) {
  const { config, onDelete } = data;

  const baseNodeData: BaseNodeData = {
    icon: "📊",
    title: "Evaluate Node",
    summaryLines: generateSummaryLines(config),
    status: getNodeStatus(config),
    showInputHandle: true,
    showOutputHandle: true,
    onDelete,
  };

  return <BaseNode data={baseNodeData} selected={selected} />;
}

export const EvaluateNode = memo(EvaluateNodeComponent);
