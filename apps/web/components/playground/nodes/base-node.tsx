"use client";

import { memo, useState } from "react";
import { Handle, Position } from "@xyflow/react";
import {
  Trash2,
  Circle,
  AlertCircle,
  CheckCircle2,
  Loader2,
  XCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { DeleteConfirmModal } from "./delete-confirm-modal";

export type NodeStatus = "not-configured" | "partial" | "ready" | "running" | "error";

export interface BaseNodeData {
  icon: string;
  title: string;
  summaryLines: string[];
  status: NodeStatus;
  showInputHandle: boolean;
  showOutputHandle: boolean;
  onDelete?: () => void;
  [key: string]: unknown;
}

interface BaseNodeProps {
  data: BaseNodeData;
  selected?: boolean;
}

const statusColors: Record<NodeStatus, string> = {
  "not-configured": "border-gray-500",
  partial: "border-amber-500",
  ready: "border-emerald-500",
  running: "border-blue-500",
  error: "border-red-500",
};

const statusIcons: Record<NodeStatus, React.ReactNode> = {
  "not-configured": <Circle className="w-4 h-4 text-gray-500" />,
  partial: <AlertCircle className="w-4 h-4 text-amber-500" />,
  ready: <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
  running: <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />,
  error: <XCircle className="w-4 h-4 text-red-500" />,
};

function BaseNodeComponent({ data, selected }: BaseNodeProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const {
    icon = "⚙️",
    title = "Node",
    summaryLines = [],
    status = "not-configured",
    showInputHandle = true,
    showOutputHandle = true,
    onDelete,
  } = data;

  // Limit summary lines to 5
  const displayLines = summaryLines.slice(0, 5);

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = () => {
    setShowDeleteModal(false);
    onDelete?.();
  };

  return (
    <>
      <div
        className={cn(
          "workflow-node w-[220px] min-h-[60px] rounded-xl border-2 transition-all duration-200",
          "bg-[rgba(30,30,30,0.95)] dark:bg-[rgba(30,30,30,0.95)] light:bg-white",
          statusColors[status],
          selected
            ? "border-[3px] shadow-[0_0_0_3px_rgba(59,130,246,0.5)] z-10"
            : "shadow-[0_2px_8px_rgba(0,0,0,0.3)] light:shadow-[0_2px_8px_rgba(0,0,0,0.1)]",
          isHovered && !selected && "shadow-[0_4px_16px_rgba(0,0,0,0.5)] light:shadow-[0_4px_16px_rgba(0,0,0,0.15)]",
          status === "running" && "animate-pulse-border"
        )}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        aria-label={`${title} node, status: ${status}`}
      >
        {/* Header */}
        <div className="node-header h-9 flex items-center px-3 border-b border-white/10 relative">
          {/* Icon */}
          <span className="text-lg flex-shrink-0">{icon}</span>

          {/* Title */}
          <span className="node-title ml-2 text-sm font-semibold text-white truncate flex-1">
            {title}
          </span>

          {/* Status Badge */}
          <div className="flex-shrink-0 mr-1">{statusIcons[status]}</div>

          {/* Delete Button */}
          {onDelete && (
            <button
              onClick={handleDeleteClick}
              className={cn(
                "w-6 h-6 flex items-center justify-center rounded",
                "text-gray-500 hover:text-red-500 hover:bg-white/5",
                "transition-all duration-200",
                isHovered ? "opacity-100" : "opacity-0"
              )}
              aria-label="Delete node"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Summary Content - Flexible height based on content */}
        <div className="px-3 py-2 flex flex-col gap-0.5">
          {displayLines.length > 0 ? (
            displayLines.map((line, index) => {
              const isLastLine = index === displayLines.length - 1 && displayLines.length === 5;
              return (
                <p
                  key={index}
                  className={cn(
                    "node-summary-line truncate",
                    isLastLine
                      ? "text-[11px] font-medium text-zinc-400 leading-5"
                      : "text-[13px] text-zinc-200 leading-5"
                  )}
                >
                  {line}
                </p>
              );
            })
          ) : (
            <p className="text-[13px] text-zinc-500 italic leading-5">No configuration</p>
          )}
        </div>

        {/* Connection Handles */}
        {showInputHandle && (
          <Handle
            type="target"
            position={Position.Left}
            className={cn(
              "!w-2 !h-2 !bg-blue-500 !border-2 !border-[rgba(30,30,30,0.95)]",
              "transition-all duration-200",
              isHovered || selected ? "!opacity-100" : "!opacity-0",
              "hover:!w-2.5 hover:!h-2.5 hover:!bg-emerald-500 hover:!shadow-[0_0_8px_rgba(16,185,129,0.6)]"
            )}
            style={{ top: "50%", left: -4 }}
          />
        )}

        {showOutputHandle && (
          <Handle
            type="source"
            position={Position.Right}
            className={cn(
              "!w-2 !h-2 !bg-blue-500 !border-2 !border-[rgba(30,30,30,0.95)]",
              "transition-all duration-200",
              "hover:!w-2.5 hover:!h-2.5 hover:!bg-emerald-500 hover:!shadow-[0_0_8px_rgba(16,185,129,0.6)]"
            )}
            style={{ top: "50%", right: -4 }}
          />
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showDeleteModal}
        nodeName={title}
        onCancel={() => setShowDeleteModal(false)}
        onConfirm={handleConfirmDelete}
      />
    </>
  );
}

export const BaseNode = memo(BaseNodeComponent);
