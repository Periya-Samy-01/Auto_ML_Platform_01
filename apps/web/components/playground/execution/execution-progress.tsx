"use client";

import { useEffect, useState } from "react";
import { X, CheckCircle2, XCircle, Clock, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { WorkflowStatus, NodeExecutionStatus } from "@/hooks/use-workflow-execution";

interface ExecutionProgressProps {
  status: WorkflowStatus;
  nodeStatuses: Record<string, NodeExecutionStatus>;
  nodeNames: Record<string, string>;
  executionOrder: string[];
  error?: string | null;
  onCancel: () => void;
  onClose: () => void;
}

function formatElapsedTime(seconds: number): string {
  if (seconds < 60) {
    return `${Math.floor(seconds)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}m ${secs}s`;
}

function getStatusIcon(status: NodeExecutionStatus["status"]) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "running":
      return <Loader2 className="h-4 w-4 text-primary animate-spin" />;
    case "failed":
      return <XCircle className="h-4 w-4 text-destructive" />;
    case "skipped":
      return <AlertCircle className="h-4 w-4 text-muted-foreground" />;
    case "pending":
    default:
      return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

function getStatusText(status: WorkflowStatus): string {
  switch (status) {
    case "pending":
      return "Preparing...";
    case "validating":
      return "Validating workflow...";
    case "running":
      return "Executing workflow...";
    case "completed":
      return "Workflow completed!";
    case "failed":
      return "Workflow failed";
    case "cancelled":
      return "Workflow cancelled";
    default:
      return "Unknown status";
  }
}

export function ExecutionProgress({
  status,
  nodeStatuses,
  nodeNames,
  executionOrder,
  error,
  onCancel,
  onClose,
}: ExecutionProgressProps) {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  // Elapsed time counter
  useEffect(() => {
    if (status !== "running" && status !== "validating") {
      return;
    }

    const interval = setInterval(() => {
      setElapsedTime((Date.now() - startTime) / 1000);
    }, 100);

    return () => clearInterval(interval);
  }, [status, startTime]);

  // Calculate progress
  const completedCount = Object.values(nodeStatuses).filter(
    (s) => s.status === "completed"
  ).length;
  const totalNodes = executionOrder.length;
  const progressPercent = totalNodes > 0 ? (completedCount / totalNodes) * 100 : 0;

  const isFinished = status === "completed" || status === "failed" || status === "cancelled";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-lg border border-border bg-card p-6 shadow-lg">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-foreground">
            {getStatusText(status)}
          </h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">
              {completedCount} of {totalNodes} nodes
            </span>
            <span className="text-muted-foreground">
              {formatElapsedTime(elapsedTime)}
            </span>
          </div>
          <Progress value={progressPercent} className="h-2" />
        </div>

        {/* Node Status List */}
        <div className="space-y-2 max-h-64 overflow-y-auto mb-4">
          {executionOrder.map((nodeId) => {
            const nodeStatus = nodeStatuses[nodeId];
            const nodeName = nodeNames[nodeId] || nodeId;
            const statusValue = nodeStatus?.status || "pending";

            return (
              <div
                key={nodeId}
                className={cn(
                  "flex items-center gap-3 p-2 rounded-md",
                  statusValue === "running" && "bg-primary/10",
                  statusValue === "failed" && "bg-destructive/10"
                )}
              >
                {getStatusIcon(statusValue)}
                <span
                  className={cn(
                    "text-sm flex-1",
                    statusValue === "running" && "text-foreground font-medium",
                    statusValue === "completed" && "text-muted-foreground",
                    statusValue === "failed" && "text-destructive",
                    statusValue === "pending" && "text-muted-foreground"
                  )}
                >
                  {nodeName}
                </span>
                {nodeStatus?.error && (
                  <span className="text-xs text-destructive truncate max-w-[150px]">
                    {nodeStatus.error}
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 mb-4">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-2">
          {!isFinished ? (
            <Button variant="destructive" onClick={onCancel}>
              Cancel
            </Button>
          ) : (
            <Button onClick={onClose}>
              {status === "completed" ? "View Results" : "Close"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
