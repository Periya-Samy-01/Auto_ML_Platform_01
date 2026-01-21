"use client";

import { CheckCircle2, XCircle, Loader2, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { NodeExecutionStatus } from "@/hooks/use-workflow-execution";

interface NodeStatusOverlayProps {
  status: NodeExecutionStatus["status"];
  error?: string;
  className?: string;
}

export function NodeStatusOverlay({ status, error, className }: NodeStatusOverlayProps) {
  if (status === "pending") {
    return null;
  }

  return (
    <div
      className={cn(
        "absolute inset-0 flex items-center justify-center rounded-lg pointer-events-none",
        status === "running" && "bg-primary/10 ring-2 ring-primary animate-pulse",
        status === "completed" && "bg-green-500/10 ring-2 ring-green-500",
        status === "failed" && "bg-destructive/10 ring-2 ring-destructive",
        status === "skipped" && "bg-muted/50",
        className
      )}
    >
      <div
        className={cn(
          "absolute -top-2 -right-2 p-1 rounded-full",
          status === "running" && "bg-primary text-primary-foreground",
          status === "completed" && "bg-green-500 text-white",
          status === "failed" && "bg-destructive text-destructive-foreground",
          status === "skipped" && "bg-muted text-muted-foreground"
        )}
      >
        {status === "running" && <Loader2 className="h-4 w-4 animate-spin" />}
        {status === "completed" && <CheckCircle2 className="h-4 w-4" />}
        {status === "failed" && <XCircle className="h-4 w-4" />}
        {status === "skipped" && <Clock className="h-4 w-4" />}
      </div>
    </div>
  );
}

/**
 * Hook to get the overlay props for a node based on execution status
 */
export function getNodeStatusOverlayProps(
  nodeId: string,
  nodeStatuses: Record<string, NodeExecutionStatus>
): NodeStatusOverlayProps | null {
  const status = nodeStatuses[nodeId];
  if (!status || status.status === "pending") {
    return null;
  }
  return {
    status: status.status,
    error: status.error,
  };
}
