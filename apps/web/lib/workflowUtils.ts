/**
 * Workflow Utilities
 *
 * Functions for working with React Flow nodes and edges,
 * particularly for reading capabilities from upstream nodes.
 */

import type { Node, Edge } from "@xyflow/react";
import type { AlgorithmId } from "@/configs/algorithms/types";
import { getAlgorithmCapabilities } from "./algorithmRenderer";

/**
 * Model Node Capabilities - stored in node.data when algorithm is selected
 */
export interface ModelCapabilities {
  algorithm: AlgorithmId;
  problemTypes: string[];
  supportsMulticlass: boolean;
  supportsProbabilities: boolean;
  supportsFeatureImportance: boolean;
  supportsExplainability: boolean;
  handlesImbalanced: boolean;
  handlesMissingValues: boolean;
  requiresScaling: boolean;
  supportsWarmStart: boolean;
  supportedMetrics: string[];
  defaultMetrics: string[];
  supportedPlots: string[];
  defaultPlots: string[];
}

/**
 * Find the upstream model node connected to a given node
 */
export function findUpstreamModelNode(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): Node | null {
  // Find edge where this node is the target
  const incomingEdge = edges.find((e) => e.target === nodeId);
  if (!incomingEdge) return null;

  // Get the source node
  const sourceNode = nodes.find((n) => n.id === incomingEdge.source);
  if (!sourceNode) return null;

  // If it's a model node, return it
  if (sourceNode.type === "model") {
    return sourceNode;
  }

  // Otherwise, recursively search upstream
  return findUpstreamModelNode(sourceNode.id, nodes, edges);
}

/**
 * Get capabilities from the upstream model node
 */
export function getUpstreamCapabilities(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): ModelCapabilities | null {
  const modelNode = findUpstreamModelNode(nodeId, nodes, edges);
  if (!modelNode) return null;

  const nodeData = modelNode.data as { capabilities?: ModelCapabilities };
  return nodeData.capabilities || null;
}

/**
 * Check if a node has a valid upstream model connection
 */
export function hasUpstreamModel(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): boolean {
  const modelNode = findUpstreamModelNode(nodeId, nodes, edges);
  if (!modelNode) return false;

  const nodeData = modelNode.data as { algorithm?: AlgorithmId };
  return !!nodeData.algorithm;
}

/**
 * Get the algorithm ID from upstream model node
 */
export function getUpstreamAlgorithm(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): AlgorithmId | null {
  const modelNode = findUpstreamModelNode(nodeId, nodes, edges);
  if (!modelNode) return null;

  const nodeData = modelNode.data as { algorithm?: AlgorithmId };
  return nodeData.algorithm || null;
}

/**
 * Update capabilities on a model node when algorithm changes
 */
export function buildModelCapabilities(
  algorithmId: AlgorithmId
): ModelCapabilities | null {
  return getAlgorithmCapabilities(algorithmId);
}

/**
 * Find all downstream nodes connected to a given node
 */
export function findDownstreamNodes(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): Node[] {
  const downstream: Node[] = [];

  const outgoingEdges = edges.filter((e) => e.source === nodeId);
  for (const edge of outgoingEdges) {
    const targetNode = nodes.find((n) => n.id === edge.target);
    if (targetNode) {
      downstream.push(targetNode);
      // Recursively find downstream
      downstream.push(...findDownstreamNodes(targetNode.id, nodes, edges));
    }
  }

  return downstream;
}

/**
 * Get dataset info from upstream dataset node
 */
export interface DatasetInfo {
  datasetId: string | null;
  datasetName: string | null;
  targetColumn: string | null;
  problemType: "classification" | "regression" | null;
  sampleCount?: number;
  featureCount?: number;
}

export function getUpstreamDatasetInfo(
  nodeId: string,
  nodes: Node[],
  edges: Edge[]
): DatasetInfo | null {
  // Find dataset node by traversing upstream
  const visited = new Set<string>();

  function findDatasetNode(currentId: string): Node | null {
    if (visited.has(currentId)) return null;
    visited.add(currentId);

    const currentNode = nodes.find((n) => n.id === currentId);
    if (!currentNode) return null;

    if (currentNode.type === "dataset") {
      return currentNode;
    }

    // Find incoming edges
    const incomingEdge = edges.find((e) => e.target === currentId);
    if (incomingEdge) {
      return findDatasetNode(incomingEdge.source);
    }

    return null;
  }

  const datasetNode = findDatasetNode(nodeId);
  if (!datasetNode) return null;

  const nodeData = datasetNode.data as {
    config?: {
      datasetId: string | null;
      datasetName: string | null;
      targetColumn: string | null;
      problemType: "classification" | "regression" | null;
    };
  };

  if (!nodeData.config) return null;

  return {
    datasetId: nodeData.config.datasetId,
    datasetName: nodeData.config.datasetName,
    targetColumn: nodeData.config.targetColumn,
    problemType: nodeData.config.problemType,
  };
}

/**
 * Check if the workflow has required nodes before the current node
 */
export interface WorkflowValidation {
  hasDataset: boolean;
  hasModel: boolean;
  hasSplit: boolean;
  errors: string[];
}

export function validateWorkflowUpstream(
  nodeId: string,
  nodeType: string,
  nodes: Node[],
  edges: Edge[]
): WorkflowValidation {
  const result: WorkflowValidation = {
    hasDataset: false,
    hasModel: false,
    hasSplit: false,
    errors: [],
  };

  const visited = new Set<string>();

  function checkUpstream(currentId: string) {
    if (visited.has(currentId)) return;
    visited.add(currentId);

    const node = nodes.find((n) => n.id === currentId);
    if (!node) return;

    if (node.type === "dataset") result.hasDataset = true;
    if (node.type === "model") result.hasModel = true;
    if (node.type === "trainTestSplit") result.hasSplit = true;

    const incomingEdge = edges.find((e) => e.target === currentId);
    if (incomingEdge) {
      checkUpstream(incomingEdge.source);
    }
  }

  checkUpstream(nodeId);

  // Validate based on node type
  if (nodeType === "model") {
    if (!result.hasDataset) {
      result.errors.push("Model node requires a Dataset node upstream");
    }
  }

  if (nodeType === "evaluate" || nodeType === "visualize") {
    if (!result.hasModel) {
      result.errors.push("This node requires a Model node upstream");
    }
  }

  return result;
}
