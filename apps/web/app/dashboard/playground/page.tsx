"use client";

import { useCallback, useRef, useState, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  BackgroundVariant,
  type ReactFlowInstance,
  type ColorMode,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useWorkflowStore, useWorkflowHistory } from "@/stores";
import { useWorkflowExecution } from "@/hooks/use-workflow-execution";
import { getExecutionOrder, getNodeNames, validateWorkflow } from "@/lib/workflow/validation";
import {
  InspectorPanel,
  CanvasToolbar,
  CanvasStatusBar,
  AlgorithmSelectModal,
  type NodeType,
} from "@/components/playground";
import {
  ExecutionProgress,
  ResultsPanel,
  ValidationErrors,
} from "@/components/playground/execution";
import {
  BaseNode,
  DatasetNode,
  TrainTestSplitNode,
  PreprocessingNode,
  FeatureEngineeringNode,
  ModelNode,
  EvaluateNode,
  VisualizeNode,
  type BaseNodeData,
  type DatasetNodeData,
  type DatasetConfig,
  type TrainTestSplitNodeData,
  type PreprocessingNodeData,
  type FeatureEngineeringNodeData,
  type ModelNodeData,
  type EvaluateNodeData,
  type VisualizeNodeData,
  defaultTrainTestSplitConfig,
  defaultPreprocessingConfig,
  defaultFeatureEngineeringConfig,
  defaultModelConfig,
  defaultEvaluateConfig,
  defaultVisualizeConfig,
} from "@/components/playground/nodes";
import type { AlgorithmId } from "@/configs/algorithms/types";
import { getDefaultHyperparameters } from "@/configs/algorithms";
import { buildModelCapabilities } from "@/lib/workflowUtils";

// Default dataset config
const defaultDatasetConfig: DatasetConfig = {
  datasetId: null,
  datasetName: null,
  isSample: false,
  targetColumn: null,
  problemType: null,
};

// Node ID counter - persisted in module scope
let nodeIdCounter = 10;
const getId = (type: string) => `${type}-${++nodeIdCounter}`;

export default function PlaygroundPage() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [canvasBounds, setCanvasBounds] = useState({ width: 0, height: 0 });
  const [colorMode, setColorMode] = useState<ColorMode>("dark");
  const [showAlgorithmModal, setShowAlgorithmModal] = useState(false);

  // Get state and actions directly from Zustand store (single source of truth)
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    deleteNode,
    selectNode,
    deselectNode,
    showProgressModal,
    showResultsPanel,
    executionResults,
    setShowProgressModal,
    setShowResultsPanel,
    startExecution,
    completeExecution,
    failExecution,
    setAllNodeExecutionStatuses,
  } = useWorkflowStore();

  // Undo/redo from temporal middleware
  const { undo, redo, canUndo, canRedo } = useWorkflowHistory();

  // Workflow execution hook
  const workflowExecution = useWorkflowExecution();

  // Register custom node types
  const nodeTypes = useMemo(
    () => ({
      base: BaseNode,
      dataset: DatasetNode,
      trainTestSplit: TrainTestSplitNode,
      preprocessing: PreprocessingNode,
      featureEngineering: FeatureEngineeringNode,
      model: ModelNode,
      evaluate: EvaluateNode,
      visualize: VisualizeNode,
    }),
    []
  );

  // Add onDelete callback to node data
  const nodesWithCallbacks = useMemo(() => {
    return nodes.map((node) => ({
      ...node,
      data: {
        ...node.data,
        onDelete: () => {
          deleteNode(node.id);
        },
      },
    }));
  }, [nodes, deleteNode]);

  // Update canvas bounds on resize
  useEffect(() => {
    const updateBounds = () => {
      if (reactFlowWrapper.current) {
        setCanvasBounds({
          width: reactFlowWrapper.current.offsetWidth,
          height: reactFlowWrapper.current.offsetHeight,
        });
      }
    };

    updateBounds();
    window.addEventListener("resize", updateBounds);
    return () => window.removeEventListener("resize", updateBounds);
  }, []);

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      selectNode(node.id);
    },
    [selectNode]
  );

  const onPaneClick = useCallback(() => {
    deselectNode();
  }, [deselectNode]);

  // Add node from menu (places in center of viewport)
  const handleAddNode = useCallback(
    (nodeType: NodeType) => {
      if (!reactFlowInstance) return;

      // Get the center of the current viewport
      const { x, y, zoom } = reactFlowInstance.getViewport();
      const centerX = (-x + canvasBounds.width / 2) / zoom;
      const centerY = (-y + canvasBounds.height / 2) / zoom;

      let newNode: Node;

      // Create Dataset node with specific config
      if (nodeType.type === "dataset") {
        newNode = {
          id: getId("dataset"),
          type: "dataset",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultDatasetConfig },
          } as DatasetNodeData,
        };
      } else if (nodeType.type === "split") {
        // Create Train/Test Split node
        newNode = {
          id: getId("split"),
          type: "trainTestSplit",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultTrainTestSplitConfig },
          } as TrainTestSplitNodeData,
        };
      } else if (nodeType.type === "preprocessing") {
        // Create Preprocessing node
        newNode = {
          id: getId("preprocessing"),
          type: "preprocessing",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultPreprocessingConfig },
          } as PreprocessingNodeData,
        };
      } else if (nodeType.type === "feature") {
        // Create Feature Engineering node
        newNode = {
          id: getId("feature"),
          type: "featureEngineering",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultFeatureEngineeringConfig },
          } as FeatureEngineeringNodeData,
        };
      } else if (nodeType.type === "model") {
        // Create Model node
        newNode = {
          id: getId("model"),
          type: "model",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultModelConfig },
            capabilities: null,
          } as ModelNodeData,
        };
      } else if (nodeType.type === "evaluate") {
        // Create Evaluate node
        newNode = {
          id: getId("evaluate"),
          type: "evaluate",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultEvaluateConfig },
          } as EvaluateNodeData,
        };
      } else if (nodeType.type === "visualize") {
        // Create Visualize node
        newNode = {
          id: getId("visualize"),
          type: "visualize",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            config: { ...defaultVisualizeConfig },
          } as VisualizeNodeData,
        };
      } else {
        // Create BaseNode for other types
        newNode = {
          id: getId(nodeType.type),
          type: "base",
          position: { x: centerX - 110, y: centerY - 60 },
          data: {
            icon: nodeType.icon,
            title: nodeType.label,
            summaryLines: ["Not configured"],
            status: "not-configured",
            showInputHandle: true,
            showOutputHandle: nodeType.type !== "save",
          } as BaseNodeData,
        };
      }

      addNode(newNode);
      selectNode(newNode.id);
    },
    [reactFlowInstance, canvasBounds, addNode, selectNode]
  );

  // Handle model node request - show algorithm selection modal
  const handleModelNodeRequest = useCallback(() => {
    setShowAlgorithmModal(true);
  }, []);

  // Handle algorithm selection from modal
  const handleAlgorithmSelect = useCallback(
    (algorithmId: AlgorithmId) => {
      if (!reactFlowInstance) {
        setShowAlgorithmModal(false);
        return;
      }

      // Get the center of the current viewport
      const { x, y, zoom } = reactFlowInstance.getViewport();
      const centerX = (-x + canvasBounds.width / 2) / zoom;
      const centerY = (-y + canvasBounds.height / 2) / zoom;

      // Get default hyperparameters and capabilities for the selected algorithm
      const defaults = getDefaultHyperparameters(algorithmId);
      const capabilities = buildModelCapabilities(algorithmId);

      // Create Model node with pre-configured algorithm
      const newNode: Node = {
        id: getId("model"),
        type: "model",
        position: { x: centerX - 110, y: centerY - 60 },
        data: {
          config: {
            ...defaultModelConfig,
            algorithm: algorithmId,
            hyperparameters: defaults,
          },
          capabilities,
        } as ModelNodeData,
      };

      addNode(newNode);
      selectNode(newNode.id);
      setShowAlgorithmModal(false);
    },
    [reactFlowInstance, canvasBounds, addNode, selectNode]
  );

  // Sync execution status from hook to store
  useEffect(() => {
    if (workflowExecution.nodeStatuses) {
      setAllNodeExecutionStatuses(workflowExecution.nodeStatuses);
    }
  }, [workflowExecution.nodeStatuses, setAllNodeExecutionStatuses]);

  useEffect(() => {
    if (workflowExecution.isCompleted && workflowExecution.results) {
      completeExecution(workflowExecution.results);
    }
  }, [workflowExecution.isCompleted, workflowExecution.results, completeExecution]);

  useEffect(() => {
    if (workflowExecution.isFailed && workflowExecution.error) {
      failExecution(workflowExecution.error);
    }
  }, [workflowExecution.isFailed, workflowExecution.error, failExecution]);

  // Compute execution order and node names
  const executionOrder = useMemo(() => getExecutionOrder(nodes, edges), [nodes, edges]);
  const nodeNames = useMemo(() => getNodeNames(nodes), [nodes]);
  const [showValidationPanel, setShowValidationPanel] = useState(false);

  // Validation result
  const validationResult = useMemo(() => validateWorkflow(nodes, edges), [nodes, edges]);

  // Handle workflow execution
  const handleExecute = useCallback(async () => {
    if (!validationResult.valid) {
      setShowValidationPanel(true);
      return;
    }

    setShowProgressModal(true);
    const jobId = await workflowExecution.execute(nodes, edges);
    if (jobId) {
      startExecution(jobId);
    }
  }, [nodes, edges, validationResult.valid, workflowExecution, setShowProgressModal, startExecution]);

  const handleCancel = useCallback(() => {
    workflowExecution.cancel();
    setShowProgressModal(false);
  }, [workflowExecution, setShowProgressModal]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      if (event.key === "Escape") {
        deselectNode();
        setShowValidationPanel(false);
      }
      // Ctrl+Enter to run workflow
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        handleExecute();
      }
      // Ctrl+Z to undo
      if ((event.ctrlKey || event.metaKey) && event.key === "z" && !event.shiftKey) {
        event.preventDefault();
        if (canUndo) undo();
      }
      // Ctrl+Shift+Z or Ctrl+Y to redo
      if (
        (event.ctrlKey || event.metaKey) &&
        (event.key === "Z" || event.key === "y") &&
        (event.shiftKey || event.key === "y")
      ) {
        event.preventDefault();
        if (canRedo) redo();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [deselectNode, handleExecute, canUndo, canRedo, undo, redo]);

  return (
    <div className={`h-screen w-full relative ${colorMode === "light" ? "bg-white" : "bg-[#1a1a1a]"}`}>
      <div ref={reactFlowWrapper} className="absolute inset-0">
        <ReactFlow
          nodes={nodesWithCallbacks}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          colorMode={colorMode}
          fitView
          minZoom={0.25}
          maxZoom={2}
          defaultEdgeOptions={{
            type: "smoothstep",
            animated: true,
            style: { stroke: "#3b82f6", strokeWidth: 2 },
          }}
          proOptions={{ hideAttribution: true }}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={2}
            color={colorMode === "light" ? "rgba(0, 0, 0, 0.1)" : "rgba(255, 255, 255, 0.1)"}
          />
          <Controls
            position="bottom-right"
            orientation="horizontal"
            className={`!rounded-lg !shadow-lg ${colorMode === "light"
              ? "!bg-white !border-gray-200 [&>button]:!bg-white [&>button]:!border-gray-200 [&>button]:hover:!bg-gray-100 [&>button>svg]:!fill-gray-700"
              : "!bg-[#1a1a1a] !border-[#333] [&>button]:!bg-[#1a1a1a] [&>button]:!border-[#333] [&>button]:hover:!bg-[#2a2a2a] [&>button>svg]:!fill-white"
              }`}
            style={{ bottom: 16, right: 230 }}
          />
          <MiniMap
            position="bottom-right"
            className={`!rounded-lg ${colorMode === "light"
              ? "!bg-white !border-gray-200"
              : "!bg-[#1a1a1a] !border-[#333]"
              }`}
            nodeColor={colorMode === "light" ? "rgba(59, 130, 246, 0.8)" : "rgba(125, 167, 255, 0.6)"}
            maskColor={colorMode === "light" ? "rgba(255, 255, 255, 0.8)" : "rgba(26, 26, 26, 0.8)"}
            style={{ bottom: 16, right: 16, width: 200, height: 120 }}
          />
        </ReactFlow>

        {/* Empty state hint */}
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p className="text-xl text-muted-foreground font-medium">
              Click the menu to add nodes
            </p>
          </div>
        )}
      </div>

      {/* Overlay UI elements */}
      <CanvasToolbar
        onAddNode={handleAddNode}
        onModelNodeRequest={handleModelNodeRequest}
        colorMode={colorMode}
        onColorModeChange={setColorMode}
        executionStatus={workflowExecution.status}
        isExecuting={workflowExecution.isExecuting}
        onExecute={handleExecute}
        onCancel={handleCancel}
        onValidationClick={() => setShowValidationPanel(!showValidationPanel)}
        onUndo={canUndo ? undo : undefined}
        onRedo={canRedo ? redo : undefined}
        canUndo={canUndo}
        canRedo={canRedo}
      />
      <InspectorPanel canvasBounds={canvasBounds} />
      <CanvasStatusBar />

      {/* Validation Errors Panel */}
      {showValidationPanel && (
        <div className="absolute top-20 left-4 z-40 w-80">
          <ValidationErrors
            errors={validationResult.errors}
            warnings={validationResult.warnings}
            onNodeClick={(nodeId) => {
              selectNode(nodeId);
              setShowValidationPanel(false);
            }}
          />
        </div>
      )}

      {/* Execution Progress Modal */}
      {showProgressModal && (
        <ExecutionProgress
          status={workflowExecution.status}
          nodeStatuses={workflowExecution.nodeStatuses}
          nodeNames={nodeNames}
          executionOrder={executionOrder}
          error={workflowExecution.error}
          onCancel={handleCancel}
          onClose={() => setShowProgressModal(false)}
        />
      )}

      {/* Results Panel */}
      {showResultsPanel && executionResults && (
        <ResultsPanel
          results={executionResults}
          onClose={() => setShowResultsPanel(false)}
        />
      )}

      {/* Algorithm Selection Modal */}
      <AlgorithmSelectModal
        isOpen={showAlgorithmModal}
        onClose={() => setShowAlgorithmModal(false)}
        onSelect={handleAlgorithmSelect}
      />
    </div>
  );
}
