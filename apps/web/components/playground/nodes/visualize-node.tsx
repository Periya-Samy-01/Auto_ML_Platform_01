"use client";

import { memo } from "react";
import { BaseNode, type BaseNodeData, type NodeStatus } from "./base-node";

export interface VisualizeConfig {
  selectedPlots: string[];
  [key: string]: unknown;
}

export interface VisualizeNodeData {
  config: VisualizeConfig;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface VisualizeNodeProps {
  data: VisualizeNodeData;
  selected?: boolean;
}

export const defaultVisualizeConfig: VisualizeConfig = {
  selectedPlots: [],
};

function generateSummaryLines(config: VisualizeConfig): string[] {
  if (config.selectedPlots.length === 0) {
    return ["No plots selected"];
  }

  const lines: string[] = [];

  // Show plots count
  lines.push(`${config.selectedPlots.length} plots selected`);

  // Show first few plots
  const displayPlots = config.selectedPlots.slice(0, 2);
  lines.push(displayPlots.map((p) => p.replace(/_/g, " ")).join(", "));

  if (config.selectedPlots.length > 2) {
    lines.push(`+${config.selectedPlots.length - 2} more`);
  }

  return lines;
}

function getNodeStatus(config: VisualizeConfig): NodeStatus {
  if (config.selectedPlots.length === 0) {
    return "not-configured";
  }
  return "ready";
}

function VisualizeNodeComponent({ data, selected }: VisualizeNodeProps) {
  const { config, onDelete } = data;

  const baseNodeData: BaseNodeData = {
    icon: "📉",
    title: "Visualize Node",
    summaryLines: generateSummaryLines(config),
    status: getNodeStatus(config),
    showInputHandle: true,
    showOutputHandle: false, // Terminal node
    onDelete,
  };

  return <BaseNode data={baseNodeData} selected={selected} />;
}

export const VisualizeNode = memo(VisualizeNodeComponent);
