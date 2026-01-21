/**
 * Workflow Store
 * Zustand store for workflow canvas state management
 *
 * Features:
 * - Single source of truth for React Flow state
 * - Persistence to localStorage
 * - Undo/Redo via zundo temporal middleware
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { temporal } from "zundo";
import {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge as rfAddEdge,
  type Node,
  type Edge,
  type NodeChange,
  type EdgeChange,
  type Connection,
} from "@xyflow/react";
import type { NodeExecutionStatus, WorkflowResults } from "@/hooks/use-workflow-execution";

// ============================================================================
// Types
// ============================================================================

export type NodeStatus = "not-configured" | "configured" | "running" | "error" | "success";

export interface InspectorPosition {
  x: number;
  y: number;
}

export type ExecutionStatus = "idle" | "validating" | "running" | "completed" | "failed" | "cancelled";

// State that should be persisted and tracked for undo/redo
interface WorkflowPersistentState {
  nodes: Node[];
  edges: Edge[];
  workflowName: string;
}

// Transient state (not persisted, not tracked for undo)
interface WorkflowTransientState {
  selectedNodeId: string | null;
  inspectorVisible: boolean;
  inspectorMinimized: boolean;
  inspectorPosition: InspectorPosition;
  executionStatus: ExecutionStatus;
  executionJobId: string | null;
  nodeExecutionStatuses: Record<string, NodeExecutionStatus>;
  executionResults: WorkflowResults | null;
  executionError: string | null;
  showResultsPanel: boolean;
  showProgressModal: boolean;
}

type WorkflowState = WorkflowPersistentState & WorkflowTransientState;

interface WorkflowActions {
  // React Flow change handlers (main interface for React Flow)
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;

  // Node actions
  setNodes: (nodes: Node[]) => void;
  addNode: (node: Node) => void;
  deleteNode: (id: string) => void;
  updateNode: (id: string, data: Partial<Node>) => void;
  updateNodeData: (id: string, data: Record<string, unknown>) => void;

  // Edge actions
  setEdges: (edges: Edge[]) => void;
  addEdge: (edge: Edge) => void;
  deleteEdge: (id: string) => void;

  // Selection actions
  selectNode: (id: string | null) => void;
  deselectNode: () => void;

  // Inspector actions
  toggleInspector: () => void;
  setInspectorVisible: (visible: boolean) => void;
  setInspectorMinimized: (minimized: boolean) => void;
  setInspectorPosition: (position: InspectorPosition) => void;

  // Workflow actions
  setWorkflowName: (name: string) => void;
  clearCanvas: () => void;

  // Execution actions
  setExecutionStatus: (status: ExecutionStatus) => void;
  setExecutionJobId: (jobId: string | null) => void;
  setNodeExecutionStatus: (nodeId: string, status: NodeExecutionStatus) => void;
  setAllNodeExecutionStatuses: (statuses: Record<string, NodeExecutionStatus>) => void;
  setExecutionResults: (results: WorkflowResults | null) => void;
  setExecutionError: (error: string | null) => void;
  setShowResultsPanel: (show: boolean) => void;
  setShowProgressModal: (show: boolean) => void;
  resetExecution: () => void;
  startExecution: (jobId: string) => void;
  completeExecution: (results: WorkflowResults) => void;
  failExecution: (error: string) => void;

  // Computed
  getSelectedNode: () => Node | undefined;
  isExecuting: () => boolean;
}

type WorkflowStore = WorkflowState & WorkflowActions;

// ============================================================================
// Initial State
// ============================================================================

const initialPersistentState: WorkflowPersistentState = {
  nodes: [],
  edges: [],
  workflowName: "Untitled Workflow",
};

const initialTransientState: WorkflowTransientState = {
  selectedNodeId: null,
  inspectorVisible: true,
  inspectorMinimized: true,
  inspectorPosition: { x: 320, y: 100 },
  executionStatus: "idle",
  executionJobId: null,
  nodeExecutionStatuses: {},
  executionResults: null,
  executionError: null,
  showResultsPanel: false,
  showProgressModal: false,
};

const initialState: WorkflowState = {
  ...initialPersistentState,
  ...initialTransientState,
};

// ============================================================================
// Default edge options
// ============================================================================

const defaultEdgeOptions = {
  type: "smoothstep",
  animated: true,
  style: { stroke: "#3b82f6", strokeWidth: 2 },
};

// ============================================================================
// Store Definition
// ============================================================================

// Create the base store with actions
const createWorkflowStore = (
  set: (partial: Partial<WorkflowState> | ((state: WorkflowState) => Partial<WorkflowState>)) => void,
  get: () => WorkflowState
): WorkflowStore => ({
  ...initialState,

  // React Flow change handlers
  onNodesChange: (changes) => {
    set((state) => ({
      nodes: applyNodeChanges(changes, state.nodes),
    }));
  },

  onEdgesChange: (changes) => {
    set((state) => ({
      edges: applyEdgeChanges(changes, state.edges),
    }));
  },

  onConnect: (connection) => {
    set((state) => {
      // Add the new edge
      const newEdges = rfAddEdge(
        {
          ...connection,
          ...defaultEdgeOptions,
        },
        state.edges
      );

      // Propagate upstream data to the target node
      const sourceNode = state.nodes.find((n) => n.id === connection.source);
      const targetNode = state.nodes.find((n) => n.id === connection.target);

      if (!sourceNode || !targetNode) {
        return { edges: newEdges };
      }

      // Get upstream dataset info from source node
      let datasetInfo: {
        datasetId: string | null;
        datasetName: string | null;
        targetColumn: string | null;
        problemType: string | null;
        totalRows: number | null;
        columns: number | null;
      } | null = null;

      // If source is a dataset node, extract its config
      if (sourceNode.type === "dataset") {
        const sourceData = sourceNode.data as { config?: Record<string, unknown> };
        if (sourceData.config) {
          datasetInfo = {
            datasetId: (sourceData.config.datasetId as string) || null,
            datasetName: (sourceData.config.datasetName as string) || null,
            targetColumn: (sourceData.config.targetColumn as string) || null,
            problemType: (sourceData.config.problemType as string) || null,
            totalRows: (sourceData.config.rows as number) || null,
            columns: (sourceData.config.columns as number) || null,
          };
        }
      }
      // If source is a pass-through node (split, preprocessing), carry forward its input
      else if (
        sourceNode.type === "trainTestSplit" ||
        sourceNode.type === "preprocessing" ||
        sourceNode.type === "featureEngineering"
      ) {
        const sourceData = sourceNode.data as { config?: Record<string, unknown> };
        if (sourceData.config) {
          datasetInfo = {
            datasetId: (sourceData.config.inputDatasetId as string) || null,
            datasetName: (sourceData.config.inputDatasetName as string) || null,
            targetColumn: (sourceData.config.targetColumn as string) || null,
            problemType: (sourceData.config.problemType as string) || null,
            totalRows: (sourceData.config.totalRows as number) || null,
            columns: null,
          };
        }
      }

      // If we have dataset info and target needs it, update the target node
      if (datasetInfo && datasetInfo.datasetId) {
        const targetNodeTypes = [
          "trainTestSplit",
          "preprocessing",
          "featureEngineering",
          "model",
        ];

        if (targetNodeTypes.includes(targetNode.type || "")) {
          const updatedNodes = state.nodes.map((node) => {
            if (node.id === targetNode.id) {
              const currentConfig = (node.data as { config?: Record<string, unknown> }).config || {};
              return {
                ...node,
                data: {
                  ...node.data,
                  config: {
                    ...currentConfig,
                    inputDatasetId: datasetInfo!.datasetId,
                    inputDatasetName: datasetInfo!.datasetName,
                    targetColumn: datasetInfo!.targetColumn,
                    problemType: datasetInfo!.problemType,
                    totalRows: datasetInfo!.totalRows,
                  },
                },
              };
            }
            return node;
          });

          return { edges: newEdges, nodes: updatedNodes };
        }
      }

      return { edges: newEdges };
    });
  },

  // Node actions
  setNodes: (nodes) => set({ nodes }),

  addNode: (node) => {
    set((state) => ({
      nodes: [...state.nodes, node],
    }));
  },

  deleteNode: (id) => {
    set((state) => ({
      nodes: state.nodes.filter((node) => node.id !== id),
      edges: state.edges.filter((edge) => edge.source !== id && edge.target !== id),
      selectedNodeId: state.selectedNodeId === id ? null : state.selectedNodeId,
    }));
  },

  updateNode: (id, data) => {
    set((state) => {
      const updatedNodes = state.nodes.map((node) =>
        node.id === id ? { ...node, ...data } : node
      );

      // If this is a dataset node and data contains config, propagate to downstream nodes
      const updatedNode = updatedNodes.find((n) => n.id === id);
      if (updatedNode?.type === "dataset") {
        const nodeData = data.data as { config?: Record<string, unknown> } | undefined;
        if (nodeData?.config) {
          const config = nodeData.config;

          // Find all directly connected downstream nodes
          const downstreamEdges = state.edges.filter((e) => e.source === id);

          if (downstreamEdges.length > 0) {
            const datasetInfo = {
              inputDatasetId: (config.datasetId as string) || null,
              inputDatasetName: (config.datasetName as string) || null,
              targetColumn: (config.targetColumn as string) || null,
              problemType: (config.problemType as string) || null,
              totalRows: (config.rows as number) || null,
            };

            const targetNodeTypes = [
              "trainTestSplit",
              "preprocessing",
              "featureEngineering",
              "model",
            ];

            const finalNodes = updatedNodes.map((node) => {
              const isDownstream = downstreamEdges.some((e) => e.target === node.id);
              if (isDownstream && targetNodeTypes.includes(node.type || "")) {
                const currentConfig = (node.data as { config?: Record<string, unknown> }).config || {};
                return {
                  ...node,
                  data: {
                    ...node.data,
                    config: {
                      ...currentConfig,
                      ...datasetInfo,
                    },
                  },
                };
              }
              return node;
            });

            return { nodes: finalNodes };
          }
        }
      }

      return { nodes: updatedNodes };
    });
  },

  updateNodeData: (id, data) => {
    set((state) => {
      const updatedNodes = state.nodes.map((node) =>
        node.id === id ? { ...node, data: { ...node.data, ...data } } : node
      );

      // If this is a dataset node and config changed, propagate to downstream nodes
      const updatedNode = updatedNodes.find((n) => n.id === id);
      if (updatedNode?.type === "dataset" && data.config) {
        const config = data.config as Record<string, unknown>;

        // Find all directly connected downstream nodes
        const downstreamEdges = state.edges.filter((e) => e.source === id);

        if (downstreamEdges.length > 0) {
          const datasetInfo = {
            inputDatasetId: (config.datasetId as string) || null,
            inputDatasetName: (config.datasetName as string) || null,
            targetColumn: (config.targetColumn as string) || null,
            problemType: (config.problemType as string) || null,
            totalRows: (config.rows as number) || null,
          };

          const targetNodeTypes = [
            "trainTestSplit",
            "preprocessing",
            "featureEngineering",
            "model",
          ];

          const finalNodes = updatedNodes.map((node) => {
            const isDownstream = downstreamEdges.some((e) => e.target === node.id);
            if (isDownstream && targetNodeTypes.includes(node.type || "")) {
              const currentConfig = (node.data as { config?: Record<string, unknown> }).config || {};
              return {
                ...node,
                data: {
                  ...node.data,
                  config: {
                    ...currentConfig,
                    ...datasetInfo,
                  },
                },
              };
            }
            return node;
          });

          return { nodes: finalNodes };
        }
      }

      return { nodes: updatedNodes };
    });
  },

  // Edge actions
  setEdges: (edges) => set({ edges }),

  addEdge: (edge) => {
    set((state) => ({
      edges: [...state.edges, { ...edge, ...defaultEdgeOptions }],
    }));
  },

  deleteEdge: (id) => {
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== id),
    }));
  },

  // Selection actions
  selectNode: (id) => {
    set({
      selectedNodeId: id,
      inspectorMinimized: id === null,
    });
  },

  deselectNode: () => {
    set({
      selectedNodeId: null,
      inspectorMinimized: true,
    });
  },

  // Inspector actions
  toggleInspector: () => {
    set((state) => ({
      inspectorMinimized: !state.inspectorMinimized,
    }));
  },

  setInspectorVisible: (visible) => set({ inspectorVisible: visible }),

  setInspectorMinimized: (minimized) => set({ inspectorMinimized: minimized }),

  setInspectorPosition: (position) => set({ inspectorPosition: position }),

  // Workflow actions
  setWorkflowName: (name) => set({ workflowName: name }),

  clearCanvas: () => {
    set({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      inspectorMinimized: true,
      executionStatus: "idle",
      executionJobId: null,
      nodeExecutionStatuses: {},
      executionResults: null,
      executionError: null,
      showResultsPanel: false,
      showProgressModal: false,
    });
  },

  // Execution actions
  setExecutionStatus: (status) => set({ executionStatus: status }),

  setExecutionJobId: (jobId) => set({ executionJobId: jobId }),

  setNodeExecutionStatus: (nodeId, status) => {
    set((state) => ({
      nodeExecutionStatuses: {
        ...state.nodeExecutionStatuses,
        [nodeId]: status,
      },
    }));
  },

  setAllNodeExecutionStatuses: (statuses) => set({ nodeExecutionStatuses: statuses }),

  setExecutionResults: (results) => set({ executionResults: results }),

  setExecutionError: (error) => set({ executionError: error }),

  setShowResultsPanel: (show) => set({ showResultsPanel: show }),

  setShowProgressModal: (show) => set({ showProgressModal: show }),

  resetExecution: () => {
    set({
      executionStatus: "idle",
      executionJobId: null,
      nodeExecutionStatuses: {},
      executionResults: null,
      executionError: null,
      showResultsPanel: false,
      showProgressModal: false,
    });
  },

  startExecution: (jobId) => {
    set({
      executionStatus: "running",
      executionJobId: jobId,
      nodeExecutionStatuses: {},
      executionResults: null,
      executionError: null,
      showProgressModal: true,
    });
  },

  completeExecution: (results) => {
    set({
      executionStatus: "completed",
      executionResults: results,
      showProgressModal: false,
      showResultsPanel: true,
    });
  },

  failExecution: (error) => {
    set({
      executionStatus: "failed",
      executionError: error,
    });
  },

  // Computed
  getSelectedNode: () => {
    const state = get();
    return state.nodes.find((node) => node.id === state.selectedNodeId);
  },

  isExecuting: () => {
    const status = get().executionStatus;
    return status === "validating" || status === "running";
  },
});

// ============================================================================
// Store with Middleware
// ============================================================================

// Store with persist and temporal (undo/redo) middleware
export const useWorkflowStore = create<WorkflowStore>()(
  persist(
    temporal(
      (set, get) => createWorkflowStore(set, get),
      {
        // Undo/redo configuration
        limit: 50, // Keep last 50 states
        // Only track changes to persistent state (nodes, edges, workflowName)
        partialize: (state) => ({
          nodes: state.nodes,
          edges: state.edges,
          workflowName: state.workflowName,
        }),
        // Equality check to avoid tracking identical states
        equality: (pastState, currentState) =>
          JSON.stringify(pastState) === JSON.stringify(currentState),
      }
    ),
    {
      name: "automl-workflow",
      // Only persist workflow data, not UI state or execution state
      partialize: (state) => ({
        nodes: state.nodes,
        edges: state.edges,
        workflowName: state.workflowName,
      }),
      // Merge persisted state with initial transient state
      merge: (persistedState, currentState) => ({
        ...currentState,
        ...(persistedState as Partial<WorkflowState>),
        // Always use fresh transient state
        ...initialTransientState,
      }),
    }
  )
);

// ============================================================================
// Undo/Redo Helpers
// ============================================================================

/**
 * Hook to access undo/redo functionality
 * Returns { undo, redo, canUndo, canRedo }
 */
export const useWorkflowHistory = () => {
  const { undo, redo, pastStates, futureStates } = useWorkflowStore.temporal.getState();

  return {
    undo,
    redo,
    canUndo: pastStates.length > 0,
    canRedo: futureStates.length > 0,
    historyLength: pastStates.length,
    futureLength: futureStates.length,
  };
};

// ============================================================================
// Type Exports
// ============================================================================

export type { NodeExecutionStatus, WorkflowResults };
