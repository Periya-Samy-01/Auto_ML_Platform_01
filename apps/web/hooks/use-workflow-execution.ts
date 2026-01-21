/**
 * useWorkflowExecution Hook
 *
 * Handles workflow execution, status tracking, and WebSocket streaming.
 */

import { useState, useCallback, useEffect, useRef } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { Node, Edge } from "@xyflow/react";

// Types
export interface WorkflowNode {
  id: string;
  type: string;
  config: Record<string, unknown>;
  position?: { x: number; y: number };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export type NodeStatus = "pending" | "running" | "completed" | "failed" | "skipped";
export type WorkflowStatus = "pending" | "validating" | "running" | "completed" | "failed" | "cancelled";

export interface NodeExecutionStatus {
  nodeId: string;
  status: NodeStatus;
  startedAt?: string;
  completedAt?: string;
  error?: string;
  progress?: number;
}

export interface ValidationError {
  nodeId?: string;
  field?: string;
  message: string;
  severity: "error" | "warning";
}

export interface WorkflowValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

export interface MetricResult {
  key: string;
  name: string;
  value: number;
  confidenceInterval?: [number, number];
}

export interface PlotResult {
  key: string;
  name: string;
  url: string;
  thumbnailUrl?: string;
}

export interface WorkflowResults {
  algorithm: string;
  algorithmName: string;
  problemType: string;
  trainingMode: "single" | "cross_validation" | "optuna";
  trainingTimeSeconds: number;
  metrics: MetricResult[];
  plots: PlotResult[];
  modelPath?: string;
  trainSamples: number;
  testSamples: number;
  featuresCount: number;
}

export interface WorkflowStatusResponse {
  jobId: string;
  job_id?: string;  // Backend uses snake_case
  status: WorkflowStatus;
  nodeStatuses: Record<string, NodeExecutionStatus>;
  node_statuses?: Record<string, NodeExecutionStatus>;  // Backend uses snake_case
  startedAt?: string;
  started_at?: string;  // Backend uses snake_case
  completedAt?: string;
  completed_at?: string;  // Backend uses snake_case
  error?: string;
  results?: WorkflowResults;
}

// Map frontend node types to backend API types
const NODE_TYPE_MAP: Record<string, string> = {
  dataset: "dataset",
  trainTestSplit: "split",  // Frontend uses "trainTestSplit", backend expects "split"
  preprocessing: "preprocessing",
  featureEngineering: "preprocessing",  // Feature engineering is also a preprocessing type
  model: "model",
  evaluate: "evaluate",
  visualize: "visualize",
};

// Transform node config to backend format
function transformConfig(nodeType: string, config: Record<string, unknown>): Record<string, unknown> {
  const transformed: Record<string, unknown> = { ...config };

  // Handle trainTestSplit -> split node: convert testSize percentage to decimal
  if (nodeType === "trainTestSplit" || nodeType === "split") {
    if (typeof config.testSize === "number") {
      // Frontend stores as percentage (20), backend expects decimal (0.2)
      transformed.test_size = config.testSize / 100;
      delete transformed.testSize;
    }
    // Map other camelCase fields to snake_case
    if (config.randomSeed !== undefined) {
      transformed.random_seed = config.randomSeed;
      delete transformed.randomSeed;
    }
  }

  // Handle dataset node
  if (nodeType === "dataset") {
    if (config.datasetId !== undefined) {
      transformed.dataset_id = config.datasetId;
      delete transformed.datasetId;
    }
    if (config.datasetName !== undefined) {
      transformed.dataset_name = config.datasetName;
      delete transformed.datasetName;
    }
    if (config.isSample !== undefined) {
      transformed.is_sample = config.isSample;
      delete transformed.isSample;
    }
    if (config.targetColumn !== undefined) {
      transformed.target_column = config.targetColumn;
      delete transformed.targetColumn;
    }
    if (config.problemType !== undefined) {
      transformed.problem_type = config.problemType;
      delete transformed.problemType;
    }
  }

  // Handle evaluate node
  if (nodeType === "evaluate") {
    if (config.selectedMetrics !== undefined) {
      transformed.selected_metrics = config.selectedMetrics;
      delete transformed.selectedMetrics;
    }
  }

  // Handle visualize node
  if (nodeType === "visualize") {
    if (config.selectedPlots !== undefined) {
      transformed.selected_plots = config.selectedPlots;
      delete transformed.selectedPlots;
    }
  }

  return transformed;
}

// Convert React Flow nodes/edges to API format
function convertToApiFormat(nodes: Node[], edges: Edge[]): { nodes: WorkflowNode[]; edges: WorkflowEdge[] } {
  return {
    nodes: nodes.map((n) => {
      const nodeType = n.type || "unknown";
      const rawConfig = (n.data as { config?: Record<string, unknown> })?.config || {};
      return {
        id: n.id,
        type: NODE_TYPE_MAP[nodeType] || nodeType,
        config: transformConfig(nodeType, rawConfig),
        position: n.position,
      };
    }),
    edges: edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      sourceHandle: e.sourceHandle ?? undefined,
      targetHandle: e.targetHandle ?? undefined,
    })),
  };
}

// API functions
async function validateWorkflow(nodes: WorkflowNode[], edges: WorkflowEdge[]): Promise<WorkflowValidationResult> {
  const response = await api.post("/workflows/validate", { nodes, edges });
  return response.data;
}

async function executeWorkflow(nodes: WorkflowNode[], edges: WorkflowEdge[], dryRun = false): Promise<{ jobId: string; status: WorkflowStatus; message: string }> {
  const response = await api.post("/workflows/execute", { nodes, edges, dry_run: dryRun });
  return response.data;
}

async function getWorkflowStatus(jobId: string): Promise<WorkflowStatusResponse> {
  const response = await api.get(`/workflows/${jobId}/status`);
  return response.data;
}

async function cancelWorkflow(jobId: string): Promise<void> {
  await api.delete(`/workflows/${jobId}`);
}

/**
 * Hook for validating a workflow
 */
export function useWorkflowValidation() {
  return useMutation({
    mutationFn: ({ nodes, edges }: { nodes: Node[]; edges: Edge[] }) => {
      const { nodes: apiNodes, edges: apiEdges } = convertToApiFormat(nodes, edges);
      return validateWorkflow(apiNodes, apiEdges);
    },
  });
}

/**
 * Hook for workflow status polling
 */
export function useWorkflowStatus(jobId: string | null, options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ["workflow", "status", jobId],
    queryFn: () => getWorkflowStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: options?.refetchInterval ?? 2000,
  });
}

/**
 * Main hook for workflow execution with WebSocket streaming
 */
export function useWorkflowExecution() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<WorkflowStatus>("pending");
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, NodeExecutionStatus>>({});
  const [results, setResults] = useState<WorkflowResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Polling fallback for status updates (in case WebSocket doesn't work)
  useEffect(() => {
    if (!jobId || !isExecuting) return;

    const pollStatus = async () => {
      try {
        const statusData = await getWorkflowStatus(jobId);
        console.log("Poll status:", statusData);

        // Update status
        setStatus(statusData.status);

        // Update node statuses
        if (statusData.nodeStatuses) {
          setNodeStatuses(statusData.nodeStatuses);
        } else if (statusData.node_statuses) {
          // Handle snake_case from backend
          setNodeStatuses(statusData.node_statuses as unknown as Record<string, NodeExecutionStatus>);
        }

        // Check for completion
        if (statusData.status === "completed" || statusData.status === "failed" || statusData.status === "cancelled") {
          setIsExecuting(false);
          if (statusData.results) {
            setResults(statusData.results);
          }
          if (statusData.status === "failed" && statusData.error) {
            setError(statusData.error);
          }
        }
      } catch (e) {
        console.error("Failed to poll workflow status:", e);
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);

    // Also poll immediately
    pollStatus();

    return () => clearInterval(interval);
  }, [jobId, isExecuting]);

  // WebSocket disabled - using polling for status updates
  // The sync Redis pub/sub causes timeout issues
  /*
  useEffect(() => {
    if (!jobId || !isExecuting) return;
  
    // Use API URL for WebSocket connection (backend server)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const wsProtocol = apiUrl.startsWith("https") ? "wss:" : "ws:";
    const apiHost = apiUrl.replace(/^https?:\/\//, "");
    const wsUrl = `${wsProtocol}//${apiHost}/api/workflows/${jobId}/stream`;
  
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
  
    ws.onopen = () => {
      console.log("WebSocket connected for workflow:", jobId);
    };
  
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };
  
    ws.onerror = (event) => {
      console.error("WebSocket error:", event);
    };
  
    ws.onclose = () => {
      console.log("WebSocket closed for workflow:", jobId);
    };
  
    return () => {
      ws.close();
    };
  }, [jobId, isExecuting]);
  */

  const handleWebSocketMessage = useCallback((message: {
    type: string;
    jobId: string;
    data: Record<string, unknown>;
  }) => {
    switch (message.type) {
      case "status_update":
        setStatus(message.data.status as WorkflowStatus);
        if (message.data.node_statuses) {
          setNodeStatuses(message.data.node_statuses as Record<string, NodeExecutionStatus>);
        }
        break;

      case "node_started":
        setNodeStatuses((prev) => ({
          ...prev,
          [message.data.node_id as string]: {
            nodeId: message.data.node_id as string,
            status: "running",
          },
        }));
        break;

      case "node_completed":
        setNodeStatuses((prev) => ({
          ...prev,
          [message.data.node_id as string]: {
            nodeId: message.data.node_id as string,
            status: "completed",
          },
        }));
        break;

      case "node_failed":
        setNodeStatuses((prev) => ({
          ...prev,
          [message.data.node_id as string]: {
            nodeId: message.data.node_id as string,
            status: "failed",
            error: message.data.error as string,
          },
        }));
        break;

      case "result":
        setStatus("completed");
        setResults(message.data.results as WorkflowResults);
        setIsExecuting(false);
        break;

      case "error":
        setStatus("failed");
        setError(message.data.error as string);
        setIsExecuting(false);
        break;
    }
  }, []);

  const execute = useCallback(async (nodes: Node[], edges: Edge[]) => {
    setIsExecuting(true);
    setError(null);
    setResults(null);
    setStatus("pending");
    setNodeStatuses({});

    try {
      const { nodes: apiNodes, edges: apiEdges } = convertToApiFormat(nodes, edges);
      const response = await executeWorkflow(apiNodes, apiEdges);

      if (response.status === "failed") {
        setError(response.message);
        setStatus("failed");
        setIsExecuting(false);
        return null;
      }

      setJobId(response.jobId);
      setStatus(response.status);
      return response.jobId;
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to execute workflow";
      setError(message);
      setStatus("failed");
      setIsExecuting(false);
      return null;
    }
  }, []);

  const cancel = useCallback(async () => {
    if (!jobId) return;

    try {
      await cancelWorkflow(jobId);
      setStatus("cancelled");
      setIsExecuting(false);
    } catch (e) {
      console.error("Failed to cancel workflow:", e);
    }
  }, [jobId]);

  const reset = useCallback(() => {
    setJobId(null);
    setStatus("pending");
    setNodeStatuses({});
    setResults(null);
    setError(null);
    setIsExecuting(false);
    if (wsRef.current) {
      wsRef.current.close();
    }
  }, []);

  return {
    // State
    jobId,
    status,
    nodeStatuses,
    results,
    error,
    isExecuting,

    // Actions
    execute,
    cancel,
    reset,

    // Computed
    isCompleted: status === "completed",
    isFailed: status === "failed",
    isCancelled: status === "cancelled",
  };
}
