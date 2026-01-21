"use client";

import { memo } from "react";
import { BaseNode, type BaseNodeData, type NodeStatus } from "./base-node";

export interface TrainTestSplitConfig {
  testSize: number; // 10-50, default 20
  stratify: boolean;
  shuffle: boolean;
  randomSeed: number;
  // Calculated from input
  inputDatasetId: string | null;
  inputDatasetName: string | null;
  totalRows: number | null;
  trainRows: number | null;
  testRows: number | null;
  problemType: string | null;
  targetColumn: string | null;
  classDistribution: Array<{
    name: string;
    total: number;
    train: number;
    test: number;
  }> | null;
  [key: string]: unknown;
}

export interface TrainTestSplitNodeData {
  config: TrainTestSplitConfig;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface TrainTestSplitNodeProps {
  data: TrainTestSplitNodeData;
  selected?: boolean;
}

// Default config
export const defaultTrainTestSplitConfig: TrainTestSplitConfig = {
  testSize: 20,
  stratify: false,
  shuffle: true,
  randomSeed: 42,
  inputDatasetId: null,
  inputDatasetName: null,
  totalRows: null,
  trainRows: null,
  testRows: null,
  problemType: null,
  targetColumn: null,
  classDistribution: null,
};

function generateSummaryLines(config: TrainTestSplitConfig): string[] {
  if (!config.inputDatasetId) {
    return ["No input connected"];
  }

  const ratio = `${100 - config.testSize}% / ${config.testSize}%`;
  const counts = config.trainRows !== null && config.testRows !== null
    ? `${config.trainRows} / ${config.testRows} rows`
    : "Calculating...";

  const lines = [ratio, counts];

  if (config.trainRows !== null && config.testRows !== null) {
    lines.push("Ready to split");
  }

  return lines;
}

function getNodeStatus(config: TrainTestSplitConfig): NodeStatus {
  if (!config.inputDatasetId) return "not-configured";
  if (config.trainRows !== null && config.testRows !== null) return "ready";
  return "not-configured";
}

function TrainTestSplitNodeComponent({ data, selected }: TrainTestSplitNodeProps) {
  const { config = defaultTrainTestSplitConfig, onDelete } = data;

  const baseNodeData: BaseNodeData = {
    icon: "✂️",
    title: "Train/Test Split",
    summaryLines: generateSummaryLines(config),
    status: getNodeStatus(config),
    showInputHandle: true,
    showOutputHandle: true,
    onDelete,
  };

  return <BaseNode data={baseNodeData} selected={selected} />;
}

export const TrainTestSplitNode = memo(TrainTestSplitNodeComponent);
