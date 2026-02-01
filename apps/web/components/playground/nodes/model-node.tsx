"use client";

import { memo } from "react";
import { BaseNode, type BaseNodeData, type NodeStatus } from "./base-node";
import type { AlgorithmId } from "@/configs/algorithms/types";
import type { ModelCapabilities } from "@/lib/workflowUtils";
import { getAlgorithmMetadata } from "@/lib/algorithmRenderer";

export interface ModelConfig {
  algorithm: AlgorithmId | null;
  hyperparameters: Record<string, unknown>;
  useCrossValidation: boolean;
  cvFolds: number;
  [key: string]: unknown;
}

export interface ModelNodeData {
  config: ModelConfig;
  capabilities?: ModelCapabilities | null;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface ModelNodeProps {
  data: ModelNodeData;
  selected?: boolean;
}

export const defaultModelConfig: ModelConfig = {
  algorithm: null,
  hyperparameters: {},
  useCrossValidation: false,
  cvFolds: 5,
};

function generateSummaryLines(config: ModelConfig): string[] {
  // Not configured state
  if (!config.algorithm) {
    return ["No algorithm selected"];
  }

  const metadata = getAlgorithmMetadata(config.algorithm);
  if (!metadata) {
    return ["Invalid algorithm"];
  }

  const lines: string[] = [];

  // Algorithm name
  lines.push(`${metadata.icon} ${metadata.shortName}`);

  // Training mode
  if (config.useCrossValidation) {
    lines.push(`${config.cvFolds}-Fold Cross-Validation`);
  } else {
    lines.push("Single train/test split");
  }

  // Status
  lines.push("✓ Ready to train");

  return lines;
}

function getNodeStatus(config: ModelConfig): NodeStatus {
  if (!config.algorithm) {
    return "not-configured";
  }
  return "ready";
}

function ModelNodeComponent({ data, selected }: ModelNodeProps) {
  const { config, onDelete } = data;

  const baseNodeData: BaseNodeData = {
    icon: "🤖",
    title: "Model Node",
    summaryLines: generateSummaryLines(config),
    status: getNodeStatus(config),
    showInputHandle: true,
    showOutputHandle: true,
    onDelete,
  };

  return <BaseNode data={baseNodeData} selected={selected} />;
}

export const ModelNode = memo(ModelNodeComponent);
