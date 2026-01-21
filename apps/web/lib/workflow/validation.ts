/**
 * Workflow Validation
 *
 * Client-side validation for workflow graphs before execution.
 */

import type { Node, Edge } from "@xyflow/react";

export interface ValidationError {
  nodeId?: string;
  field?: string;
  message: string;
  severity: "error" | "warning";
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

interface NodeConfig {
  configured?: boolean;
  datasetId?: string;
  targetColumn?: string;
  algorithm?: string;
  [key: string]: unknown;
}

/**
 * Get node configuration from node data
 */
function getNodeConfig(node: Node): NodeConfig {
  return (node.data as { config?: NodeConfig })?.config || {};
}

/**
 * Get node type label
 */
function getNodeLabel(type: string): string {
  const labels: Record<string, string> = {
    dataset: "Dataset",
    preprocessing: "Preprocessing",
    split: "Train/Test Split",
    model: "Model",
    evaluate: "Evaluate",
    visualize: "Visualize",
    feature: "Feature Engineering",
  };
  return labels[type] || type;
}

/**
 * Check if a node has incoming connections
 */
function hasIncomingEdge(nodeId: string, edges: Edge[]): boolean {
  return edges.some((edge) => edge.target === nodeId);
}

/**
 * Check if a node has outgoing connections
 */
function hasOutgoingEdge(nodeId: string, edges: Edge[]): boolean {
  return edges.some((edge) => edge.source === nodeId);
}

/**
 * Find all upstream nodes (ancestors) for a given node
 */
function getUpstreamNodes(nodeId: string, edges: Edge[]): Set<string> {
  const upstream = new Set<string>();
  const queue = [nodeId];

  while (queue.length > 0) {
    const current = queue.shift()!;
    for (const edge of edges) {
      if (edge.target === current && !upstream.has(edge.source)) {
        upstream.add(edge.source);
        queue.push(edge.source);
      }
    }
  }

  return upstream;
}

/**
 * Check for cycles in the graph using DFS
 */
function detectCycle(nodes: Node[], edges: Edge[]): string[] | null {
  const visited = new Set<string>();
  const recursionStack = new Set<string>();
  const path: string[] = [];

  function dfs(nodeId: string): boolean {
    visited.add(nodeId);
    recursionStack.add(nodeId);
    path.push(nodeId);

    const outgoingEdges = edges.filter((e) => e.source === nodeId);
    for (const edge of outgoingEdges) {
      if (!visited.has(edge.target)) {
        if (dfs(edge.target)) {
          return true;
        }
      } else if (recursionStack.has(edge.target)) {
        // Found cycle
        const cycleStart = path.indexOf(edge.target);
        return true;
      }
    }

    recursionStack.delete(nodeId);
    path.pop();
    return false;
  }

  for (const node of nodes) {
    if (!visited.has(node.id)) {
      if (dfs(node.id)) {
        return path;
      }
    }
  }

  return null;
}

/**
 * Validate the workflow graph
 */
export function validateWorkflow(nodes: Node[], edges: Edge[]): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Check if workflow is empty
  if (nodes.length === 0) {
    errors.push({
      message: "Workflow is empty. Add at least one node.",
      severity: "error",
    });
    return { valid: false, errors, warnings };
  }

  // Group nodes by type
  const nodesByType = nodes.reduce((acc, node) => {
    const type = node.type || "unknown";
    if (!acc[type]) acc[type] = [];
    acc[type].push(node);
    return acc;
  }, {} as Record<string, Node[]>);

  // Check for required dataset node
  const datasetNodes = nodesByType["dataset"] || [];
  if (datasetNodes.length === 0) {
    errors.push({
      message: "Workflow must have at least one Dataset node.",
      severity: "error",
    });
  }

  // Validate each node
  for (const node of nodes) {
    const nodeType = node.type || "unknown";
    const config = getNodeConfig(node);
    const nodeLabel = getNodeLabel(nodeType);

    // Check dataset node configuration
    if (nodeType === "dataset") {
      if (!config.datasetId) {
        errors.push({
          nodeId: node.id,
          field: "datasetId",
          message: `${nodeLabel}: No dataset selected.`,
          severity: "error",
        });
      }
      if (!config.targetColumn && nodesByType["model"]?.length) {
        warnings.push({
          nodeId: node.id,
          field: "targetColumn",
          message: `${nodeLabel}: No target column selected. Required for supervised learning.`,
          severity: "warning",
        });
      }
    }

    // Check model node configuration
    if (nodeType === "model") {
      if (!config.algorithm) {
        errors.push({
          nodeId: node.id,
          field: "algorithm",
          message: `${nodeLabel}: No algorithm selected.`,
          severity: "error",
        });
      }

      // Check if model has upstream data
      const upstream = getUpstreamNodes(node.id, edges);
      const hasDatasetUpstream = [...upstream].some((id) => {
        const upstreamNode = nodes.find((n) => n.id === id);
        return upstreamNode?.type === "dataset";
      });

      if (!hasDatasetUpstream && !hasIncomingEdge(node.id, edges)) {
        errors.push({
          nodeId: node.id,
          message: `${nodeLabel}: Must be connected to a Dataset node (directly or through other nodes).`,
          severity: "error",
        });
      }
    }

    // Check evaluate node has upstream model
    if (nodeType === "evaluate") {
      const upstream = getUpstreamNodes(node.id, edges);
      const hasModelUpstream = [...upstream].some((id) => {
        const upstreamNode = nodes.find((n) => n.id === id);
        return upstreamNode?.type === "model";
      });

      if (!hasModelUpstream) {
        errors.push({
          nodeId: node.id,
          message: `${nodeLabel}: Must be connected after a Model node.`,
          severity: "error",
        });
      }
    }

    // Check visualize node has upstream model or evaluate
    if (nodeType === "visualize") {
      const upstream = getUpstreamNodes(node.id, edges);
      const hasModelOrEvalUpstream = [...upstream].some((id) => {
        const upstreamNode = nodes.find((n) => n.id === id);
        return upstreamNode?.type === "model" || upstreamNode?.type === "evaluate";
      });

      if (!hasModelOrEvalUpstream) {
        errors.push({
          nodeId: node.id,
          message: `${nodeLabel}: Must be connected after a Model or Evaluate node.`,
          severity: "error",
        });
      }
    }

    // Check for disconnected nodes (no edges at all)
    if (nodes.length > 1) {
      if (!hasIncomingEdge(node.id, edges) && !hasOutgoingEdge(node.id, edges)) {
        warnings.push({
          nodeId: node.id,
          message: `${nodeLabel}: Node is disconnected from the workflow.`,
          severity: "warning",
        });
      }
    }
  }

  // Check for circular dependencies
  const cycle = detectCycle(nodes, edges);
  if (cycle) {
    errors.push({
      message: "Workflow contains a circular dependency. Remove the cycle to continue.",
      severity: "error",
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Get execution order using topological sort (Kahn's algorithm)
 */
export function getExecutionOrder(nodes: Node[], edges: Edge[]): string[] {
  const inDegree = new Map<string, number>();
  const adjacency = new Map<string, string[]>();

  // Initialize
  for (const node of nodes) {
    inDegree.set(node.id, 0);
    adjacency.set(node.id, []);
  }

  // Build adjacency and calculate in-degrees
  for (const edge of edges) {
    adjacency.get(edge.source)?.push(edge.target);
    inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1);
  }

  // Find all nodes with no incoming edges
  const queue: string[] = [];
  for (const [nodeId, degree] of inDegree) {
    if (degree === 0) {
      queue.push(nodeId);
    }
  }

  // Process nodes
  const order: string[] = [];
  while (queue.length > 0) {
    const nodeId = queue.shift()!;
    order.push(nodeId);

    for (const neighbor of adjacency.get(nodeId) || []) {
      inDegree.set(neighbor, (inDegree.get(neighbor) || 0) - 1);
      if (inDegree.get(neighbor) === 0) {
        queue.push(neighbor);
      }
    }
  }

  return order;
}

/**
 * Get node names for display
 */
export function getNodeNames(nodes: Node[]): Record<string, string> {
  return nodes.reduce((acc, node) => {
    const type = node.type || "unknown";
    const label = getNodeLabel(type);
    const config = getNodeConfig(node);

    // Add algorithm name for model nodes
    if (type === "model" && config.algorithm) {
      acc[node.id] = `${label} (${config.algorithm})`;
    } else {
      acc[node.id] = label;
    }

    return acc;
  }, {} as Record<string, string>);
}
