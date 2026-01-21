"use client";

import { useState, useMemo } from "react";
import { Save, Trash2, Pencil, Check, X, MoreVertical, Plus, Sun, Moon, Monitor, Undo2, Redo2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
  DropdownMenuPortal,
} from "@/components/ui/dropdown-menu";
import { useWorkflowStore } from "@/stores";
import { cn } from "@/lib/utils";
import { validateWorkflow, type ValidationError } from "@/lib/workflow/validation";
import { ExecutionButton, ValidationIndicator } from "@/components/playground/execution";
import type { ColorMode } from "@xyflow/react";
import type { WorkflowStatus } from "@/hooks/use-workflow-execution";

export interface NodeType {
  type: string;
  label: string;
  icon: string;
  description: string;
}

export const nodeTypes: NodeType[] = [
  { type: "dataset", label: "Dataset", icon: "📊", description: "Load a dataset" },
  { type: "split", label: "Train/Test Split", icon: "✂️", description: "Split data into train/test sets" },
  { type: "preprocessing", label: "Preprocessing", icon: "🔧", description: "Clean and preprocess data" },
  { type: "feature", label: "Feature Engineering", icon: "⚡", description: "Create new features" },
  { type: "model", label: "Model", icon: "🤖", description: "Train a model" },
  { type: "ensemble", label: "Ensemble", icon: "🎭", description: "Combine multiple models" },
  { type: "evaluate", label: "Evaluate", icon: "📈", description: "Evaluate performance" },
  { type: "visualize", label: "Visualize", icon: "📊", description: "Create visualizations" },
  { type: "save", label: "Save", icon: "💾", description: "Save model or results" },
];

interface CanvasToolbarProps {
  onAddNode?: (nodeType: NodeType) => void;
  onModelNodeRequest?: () => void;
  colorMode?: ColorMode;
  onColorModeChange?: (mode: ColorMode) => void;
  executionStatus?: WorkflowStatus;
  isExecuting?: boolean;
  onExecute?: () => void;
  onCancel?: () => void;
  onValidationClick?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
}

export function CanvasToolbar({
  onAddNode,
  onModelNodeRequest,
  colorMode,
  onColorModeChange,
  executionStatus = "pending",
  isExecuting = false,
  onExecute,
  onCancel,
  onValidationClick,
  onUndo,
  onRedo,
  canUndo = false,
  canRedo = false,
}: CanvasToolbarProps) {
  const { workflowName, setWorkflowName, clearCanvas, nodes, edges } = useWorkflowStore();
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(workflowName);

  // Run validation on nodes/edges change
  const validationResult = useMemo(() => {
    return validateWorkflow(nodes, edges);
  }, [nodes, edges]);

  const { errors, warnings } = validationResult;
  const canExecute = validationResult.valid && nodes.length > 0;

  const handleSave = () => {
    // TODO: Implement save workflow
    console.log("Saving workflow...", { nodes, edges, name: workflowName });
  };

  const handleClear = () => {
    if (nodes.length === 0 && edges.length === 0) return;
    if (confirm("Are you sure you want to clear the canvas? This action cannot be undone.")) {
      clearCanvas();
    }
  };

  const handleNameEdit = () => {
    setEditedName(workflowName);
    setIsEditing(true);
  };

  const handleNameSave = () => {
    if (editedName.trim()) {
      setWorkflowName(editedName.trim());
    }
    setIsEditing(false);
  };

  const handleNameCancel = () => {
    setEditedName(workflowName);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleNameSave();
    } else if (e.key === "Escape") {
      handleNameCancel();
    }
  };

  const handleAddNode = (nodeType: NodeType) => {
    // For model nodes, trigger the algorithm selection modal
    if (nodeType.type === "model" && onModelNodeRequest) {
      onModelNodeRequest();
      return;
    }
    onAddNode?.(nodeType);
  };

  return (
    <div className="absolute top-4 left-0 right-0 z-30 flex items-center justify-between px-4">
      {/* Left: Workflow Name */}
      <div className="flex items-center gap-3 ml-[20px]">
        {isEditing ? (
          <div className="flex items-center gap-2">
            <Input
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-64 h-9 bg-card/95 border-border text-foreground backdrop-blur-sm"
              autoFocus
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={handleNameSave}
              className="h-9 w-9 text-secondary hover:text-secondary/80 hover:bg-secondary/10"
            >
              <Check className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleNameCancel}
              className="h-9 w-9 text-muted-foreground hover:text-foreground hover:bg-muted"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ) : (
          <button
            onClick={handleNameEdit}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg",
              "bg-card/90 backdrop-blur-sm border border-border",
              "hover:bg-card transition-colors group"
            )}
          >
            <span className="text-base font-semibold text-foreground">{workflowName}</span>
            <Pencil className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>
        )}

        {/* Validation Indicator */}
        {(errors.length > 0 || warnings.length > 0) && (
          <ValidationIndicator
            errors={errors}
            warnings={warnings}
            onClick={onValidationClick}
          />
        )}
      </div>

      {/* Right: Undo/Redo + Run Button + Kebab Menu */}
      <div className="flex items-center gap-2">
        {/* Undo/Redo Buttons */}
        <div className="flex items-center gap-1 bg-card/90 backdrop-blur-sm border border-border rounded-lg p-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={onUndo}
            disabled={!canUndo}
            className={cn(
              "h-8 w-8 rounded-md",
              "text-foreground hover:bg-muted",
              !canUndo && "opacity-50 cursor-not-allowed"
            )}
            title="Undo (Ctrl+Z)"
          >
            <Undo2 className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onRedo}
            disabled={!canRedo}
            className={cn(
              "h-8 w-8 rounded-md",
              "text-foreground hover:bg-muted",
              !canRedo && "opacity-50 cursor-not-allowed"
            )}
            title="Redo (Ctrl+Shift+Z)"
          >
            <Redo2 className="w-4 h-4" />
          </Button>
        </div>

        {/* Execution Button */}
        {onExecute && onCancel && (
          <ExecutionButton
            status={executionStatus}
            isExecuting={isExecuting}
            disabled={!canExecute}
            onExecute={onExecute}
            onCancel={onCancel}
          />
        )}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "h-10 w-10 rounded-lg",
                "bg-card/90 backdrop-blur-sm border border-border",
                "hover:bg-card text-foreground"
              )}
            >
              <MoreVertical className="w-5 h-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 bg-card border-border">
            {/* Add Node Submenu */}
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="text-foreground focus:text-foreground focus:bg-accent">
                <Plus className="w-4 h-4 mr-2" />
                Add Node
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent className="w-56 bg-card border-border max-h-[400px] overflow-y-auto custom-scrollbar">
                  {nodeTypes.map((nodeType) => (
                    <DropdownMenuItem
                      key={nodeType.type}
                      onClick={() => handleAddNode(nodeType)}
                      className="text-foreground focus:text-foreground focus:bg-accent"
                    >
                      <span className="text-lg mr-3">{nodeType.icon}</span>
                      <div className="flex flex-col">
                        <span className="text-sm">{nodeType.label}</span>
                        <span className="text-xs text-muted-foreground">{nodeType.description}</span>
                      </div>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>

            {/* Theme Submenu */}
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="text-foreground focus:text-foreground focus:bg-accent">
                {colorMode === "dark" ? (
                  <Moon className="w-4 h-4 mr-2" />
                ) : colorMode === "light" ? (
                  <Sun className="w-4 h-4 mr-2" />
                ) : (
                  <Monitor className="w-4 h-4 mr-2" />
                )}
                Theme
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent className="w-40 bg-card border-border">
                  <DropdownMenuItem
                    onClick={() => onColorModeChange?.("dark")}
                    className={cn(
                      "text-foreground focus:text-foreground focus:bg-accent",
                      colorMode === "dark" && "bg-accent"
                    )}
                  >
                    <Moon className="w-4 h-4 mr-2" />
                    Dark
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onColorModeChange?.("light")}
                    className={cn(
                      "text-foreground focus:text-foreground focus:bg-accent",
                      colorMode === "light" && "bg-accent"
                    )}
                  >
                    <Sun className="w-4 h-4 mr-2" />
                    Light
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>
            <DropdownMenuSeparator className="bg-border" />
            <DropdownMenuItem
              onClick={handleSave}
              className="text-foreground focus:text-foreground focus:bg-accent"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Workflow
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-border" />
            <DropdownMenuItem
              onClick={handleClear}
              disabled={nodes.length === 0}
              className={cn(
                "text-destructive focus:text-destructive focus:bg-destructive/10",
                nodes.length === 0 && "opacity-50 cursor-not-allowed"
              )}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear Canvas
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
