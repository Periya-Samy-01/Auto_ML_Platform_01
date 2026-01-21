"use client";

import { Play, Square, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { WorkflowStatus } from "@/hooks/use-workflow-execution";

interface ExecutionButtonProps {
  status: WorkflowStatus;
  isExecuting: boolean;
  disabled?: boolean;
  onExecute: () => void;
  onCancel: () => void;
  className?: string;
}

export function ExecutionButton({
  status,
  isExecuting,
  disabled = false,
  onExecute,
  onCancel,
  className,
}: ExecutionButtonProps) {
  const isRunning = isExecuting || status === "running" || status === "validating";
  const tooltipText = isRunning
    ? "Cancel execution"
    : disabled
    ? "Configure all nodes to run workflow"
    : "Run workflow (Ctrl+Enter)";

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={isRunning ? "destructive" : "default"}
            size="sm"
            onClick={isRunning ? onCancel : onExecute}
            disabled={disabled && !isRunning}
            className={cn(
              "gap-2 px-4 font-medium transition-all",
              isRunning && "bg-destructive hover:bg-destructive/90",
              !isRunning && !disabled && "bg-primary hover:bg-primary/90",
              className
            )}
          >
            {isRunning ? (
              <>
                {status === "validating" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Square className="h-4 w-4" />
                )}
                <span>{status === "validating" ? "Validating..." : "Cancel"}</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                <span>Run</span>
              </>
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">
          <p>{tooltipText}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
