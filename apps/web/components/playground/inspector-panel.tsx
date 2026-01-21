"use client";

import { useRef, useState, useCallback, useEffect, useMemo } from "react";
import { MousePointer2, GripHorizontal, Minimize2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkflowStore } from "@/stores";
import { DatasetInspector } from "./nodes/dataset-inspector";
import { TrainTestSplitInspector } from "./nodes/train-test-split-inspector";
import { PreprocessingInspector } from "./nodes/preprocessing-inspector";
import { FeatureEngineeringInspector } from "./nodes/feature-engineering-inspector";
import { ModelInspector } from "./nodes/model-inspector";
import { EvaluateInspector } from "./nodes/evaluate-inspector";
import { VisualizeInspector } from "./nodes/visualize-inspector";
import type { DatasetConfig } from "./nodes/dataset-node";
import type { TrainTestSplitConfig } from "./nodes/train-test-split-node";
import type { PreprocessingConfig } from "./nodes/preprocessing-node";
import type { FeatureEngineeringConfig } from "./nodes/feature-engineering-node";
import type { ModelConfig } from "./nodes/model-node";
import type { EvaluateConfig } from "./nodes/evaluate-node";
import type { VisualizeConfig } from "./nodes/visualize-node";
import { getUpstreamCapabilities, type ModelCapabilities } from "@/lib/workflowUtils";

interface InspectorPanelProps {
  canvasBounds?: { width: number; height: number };
}

export function InspectorPanel({ canvasBounds }: InspectorPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const {
    selectedNodeId,
    nodes,
    edges,
    inspectorMinimized,
    inspectorPosition,
    setInspectorPosition,
    setInspectorMinimized,
    updateNode,
  } = useWorkflowStore();

  // Find selected node directly from store nodes
  const selectedNode = selectedNodeId ? nodes.find(n => n.id === selectedNodeId) : null;

  // Get upstream capabilities for Evaluate and Visualize nodes
  const upstreamCapabilities = useMemo(() => {
    if (!selectedNode) return null;
    if (selectedNode.type === "evaluate" || selectedNode.type === "visualize") {
      return getUpstreamCapabilities(selectedNode.id, nodes, edges);
    }
    return null;
  }, [selectedNode, nodes, edges]);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (headerRef.current?.contains(e.target as Node)) {
        setIsDragging(true);
        setDragOffset({
          x: e.clientX - inspectorPosition.x,
          y: e.clientY - inspectorPosition.y,
        });
      }
    },
    [inspectorPosition]
  );

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (isDragging) {
        let newX = e.clientX - dragOffset.x;
        let newY = e.clientY - dragOffset.y;

        // Constrain to canvas bounds
        const panelWidth = 380;
        const panelHeight = panelRef.current?.offsetHeight || 400;

        if (canvasBounds) {
          newX = Math.max(0, Math.min(newX, canvasBounds.width - panelWidth));
          newY = Math.max(0, Math.min(newY, canvasBounds.height - panelHeight));
        }

        setInspectorPosition({ x: newX, y: newY });
      }
    },
    [isDragging, dragOffset, canvasBounds, setInspectorPosition]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      return () => {
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Handler to update dataset node config
  const handleDatasetConfigChange = useCallback(
    (configUpdate: Partial<DatasetConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: DatasetConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update train/test split node config
  const handleTrainTestSplitConfigChange = useCallback(
    (configUpdate: Partial<TrainTestSplitConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: TrainTestSplitConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update preprocessing node config
  const handlePreprocessingConfigChange = useCallback(
    (configUpdate: Partial<PreprocessingConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: PreprocessingConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update feature engineering node config
  const handleFeatureEngineeringConfigChange = useCallback(
    (configUpdate: Partial<FeatureEngineeringConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: FeatureEngineeringConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update model node config
  const handleModelConfigChange = useCallback(
    (configUpdate: Partial<ModelConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: ModelConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update model node capabilities
  const handleModelCapabilitiesChange = useCallback(
    (capabilities: ModelCapabilities | null) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          capabilities,
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update evaluate node config
  const handleEvaluateConfigChange = useCallback(
    (configUpdate: Partial<EvaluateConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: EvaluateConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Handler to update visualize node config
  const handleVisualizeConfigChange = useCallback(
    (configUpdate: Partial<VisualizeConfig>) => {
      if (!selectedNode) return;

      updateNode(selectedNode.id, {
        data: {
          ...selectedNode.data,
          config: {
            ...(selectedNode.data as { config: VisualizeConfig }).config,
            ...configUpdate,
          },
        },
      });
    },
    [selectedNode, updateNode]
  );

  // Minimized button
  if (inspectorMinimized) {
    return (
      <button
        onClick={() => setInspectorMinimized(false)}
        className={cn(
          "absolute left-5 top-1/2 -translate-y-1/2 z-50",
          "w-12 h-44 rounded-xl",
          "bg-card/95 backdrop-blur-xl",
          "border border-border",
          "shadow-[0_8px_32px_rgba(125,167,255,0.2)]",
          "flex flex-col items-center justify-center gap-2",
          "hover:bg-accent transition-colors",
          "cursor-pointer"
        )}
        style={{ writingMode: "vertical-rl", textOrientation: "mixed" }}
      >
        <MousePointer2 className="w-4 h-4 text-muted-foreground rotate-90" />
        <span className="text-xs font-medium text-foreground">Inspector</span>
      </button>
    );
  }

  // Get title and icon based on node type
  const getNodeTitle = () => {
    if (!selectedNode) return { title: "Inspector", icon: "📋" };
    if (selectedNode.type === "dataset") return { title: "Dataset Configuration", icon: "📊" };
    if (selectedNode.type === "trainTestSplit") return { title: "Train/Test Split", icon: "✂️" };
    if (selectedNode.type === "preprocessing") return { title: "Preprocessing", icon: "🧹" };
    if (selectedNode.type === "featureEngineering") return { title: "Feature Engineering", icon: "🔧" };
    if (selectedNode.type === "model") return { title: "Model Configuration", icon: "🤖" };
    if (selectedNode.type === "evaluate") return { title: "Evaluation Metrics", icon: "📊" };
    if (selectedNode.type === "visualize") return { title: "Visualizations", icon: "📉" };
    const nodeData = selectedNode.data as { title?: string; icon?: string };
    return { title: nodeData.title || "Node", icon: nodeData.icon || "📦" };
  };

  const { title: panelTitle, icon: panelIcon } = getNodeTitle();

  // Determine which inspector content to show based on node type
  const renderInspectorContent = () => {
    if (!selectedNode) {
      return (
        <div className="flex flex-col items-center justify-center py-16 px-8">
          <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mb-4">
            <MousePointer2 className="w-8 h-8 text-muted-foreground" />
          </div>
          <p className="text-sm text-muted-foreground text-center">
            Select a node on the canvas to configure
          </p>
        </div>
      );
    }

    // Dataset node inspector
    if (selectedNode.type === "dataset") {
      const nodeData = selectedNode.data as { config: DatasetConfig };
      return (
        <DatasetInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handleDatasetConfigChange}
        />
      );
    }

    // Train/Test Split node inspector
    if (selectedNode.type === "trainTestSplit") {
      const nodeData = selectedNode.data as { config: TrainTestSplitConfig };
      return (
        <TrainTestSplitInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handleTrainTestSplitConfigChange}
        />
      );
    }

    // Preprocessing node inspector
    if (selectedNode.type === "preprocessing") {
      const nodeData = selectedNode.data as { config: PreprocessingConfig };
      return (
        <PreprocessingInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handlePreprocessingConfigChange}
        />
      );
    }

    // Feature Engineering node inspector
    if (selectedNode.type === "featureEngineering") {
      const nodeData = selectedNode.data as { config: FeatureEngineeringConfig };
      return (
        <FeatureEngineeringInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handleFeatureEngineeringConfigChange}
        />
      );
    }

    // Model node inspector
    if (selectedNode.type === "model") {
      const nodeData = selectedNode.data as { config: ModelConfig };
      return (
        <ModelInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handleModelConfigChange}
          onCapabilitiesChange={handleModelCapabilitiesChange}
        />
      );
    }

    // Evaluate node inspector
    if (selectedNode.type === "evaluate") {
      const nodeData = selectedNode.data as { config: EvaluateConfig };
      return (
        <EvaluateInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handleEvaluateConfigChange}
          capabilities={upstreamCapabilities}
        />
      );
    }

    // Visualize node inspector
    if (selectedNode.type === "visualize") {
      const nodeData = selectedNode.data as { config: VisualizeConfig };
      return (
        <VisualizeInspector
          nodeId={selectedNode.id}
          config={nodeData.config}
          onConfigChange={handleVisualizeConfigChange}
          capabilities={upstreamCapabilities}
        />
      );
    }

    // Default inspector for other node types (BaseNode)
    const nodeData = selectedNode.data as {
      icon?: string;
      title?: string;
      status?: string;
    };

    return (
      <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
        <div className="space-y-3">
          <p className="text-sm text-zinc-500">
            Node configuration options will appear here.
          </p>
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-xs text-zinc-400">Node ID</p>
            <p className="text-sm text-zinc-300 font-mono">{selectedNode.id}</p>
          </div>
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-xs text-zinc-400">Type</p>
            <p className="text-sm text-zinc-300">{selectedNode.type}</p>
          </div>
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-xs text-zinc-400">Status</p>
            <p className="text-sm text-zinc-300">{nodeData.status || "not-configured"}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div
      ref={panelRef}
      className={cn(
        "absolute z-50 w-[380px] min-h-[500px] max-h-[calc(100vh-100px)]",
        "bg-[rgba(15,15,15,0.95)] backdrop-blur-xl",
        "border border-white/10 rounded-2xl",
        "shadow-[0_8px_32px_rgba(0,0,0,0.5)]",
        "flex flex-col overflow-hidden"
      )}
      style={{
        left: inspectorPosition.x,
        top: inspectorPosition.y,
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Common Draggable Header */}
      <div
        ref={headerRef}
        className={cn(
          "flex items-center justify-between px-4 py-3 border-b border-border",
          "bg-accent/30 cursor-move select-none flex-shrink-0"
        )}
      >
        <div className="flex items-center gap-3">
          <GripHorizontal className="w-4 h-4 text-muted-foreground" />
          <span className="text-lg">{panelIcon}</span>
          <span className="text-sm font-semibold text-foreground">{panelTitle}</span>
        </div>
        <button
          onClick={() => setInspectorMinimized(true)}
          className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-accent transition-colors"
        >
          <Minimize2 className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {renderInspectorContent()}
      </div>
    </div>
  );
}
