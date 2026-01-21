"use client";

import { AlertTriangle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { ValidationError } from "@/lib/workflow/validation";

interface ValidationErrorsProps {
  errors: ValidationError[];
  warnings: ValidationError[];
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

export function ValidationErrors({
  errors,
  warnings,
  onNodeClick,
  className,
}: ValidationErrorsProps) {
  const [expanded, setExpanded] = useState(true);

  if (errors.length === 0 && warnings.length === 0) {
    return null;
  }

  const total = errors.length + warnings.length;

  return (
    <div
      className={cn(
        "rounded-lg border bg-card shadow-sm overflow-hidden",
        errors.length > 0 ? "border-destructive/50" : "border-yellow-500/50",
        className
      )}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className={cn(
          "w-full flex items-center justify-between px-3 py-2",
          errors.length > 0 ? "bg-destructive/10" : "bg-yellow-500/10"
        )}
      >
        <div className="flex items-center gap-2">
          {errors.length > 0 ? (
            <XCircle className="h-4 w-4 text-destructive" />
          ) : (
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          )}
          <span className="text-sm font-medium text-foreground">
            {errors.length > 0
              ? `${errors.length} error${errors.length > 1 ? "s" : ""}`
              : `${warnings.length} warning${warnings.length > 1 ? "s" : ""}`}
            {errors.length > 0 && warnings.length > 0 && `, ${warnings.length} warning${warnings.length > 1 ? "s" : ""}`}
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {/* Content */}
      {expanded && (
        <div className="p-2 space-y-1 max-h-48 overflow-y-auto">
          {/* Errors first */}
          {errors.map((error, index) => (
            <ValidationItem
              key={`error-${index}`}
              item={error}
              onNodeClick={onNodeClick}
            />
          ))}
          {/* Then warnings */}
          {warnings.map((warning, index) => (
            <ValidationItem
              key={`warning-${index}`}
              item={warning}
              onNodeClick={onNodeClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ValidationItem({
  item,
  onNodeClick,
}: {
  item: ValidationError;
  onNodeClick?: (nodeId: string) => void;
}) {
  const isError = item.severity === "error";

  return (
    <div
      className={cn(
        "flex items-start gap-2 p-2 rounded text-sm",
        isError ? "bg-destructive/5" : "bg-yellow-500/5",
        item.nodeId && onNodeClick && "cursor-pointer hover:bg-muted"
      )}
      onClick={() => item.nodeId && onNodeClick?.(item.nodeId)}
    >
      {isError ? (
        <XCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
      ) : (
        <AlertTriangle className="h-4 w-4 text-yellow-500 shrink-0 mt-0.5" />
      )}
      <span className={cn(isError ? "text-destructive" : "text-yellow-600 dark:text-yellow-400")}>
        {item.message}
      </span>
    </div>
  );
}

/**
 * Compact validation indicator for toolbar
 */
interface ValidationIndicatorProps {
  errors: ValidationError[];
  warnings: ValidationError[];
  onClick?: () => void;
}

export function ValidationIndicator({ errors, warnings, onClick }: ValidationIndicatorProps) {
  if (errors.length === 0 && warnings.length === 0) {
    return null;
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-1.5 px-2 py-1 rounded-md text-sm font-medium transition-colors",
        errors.length > 0
          ? "bg-destructive/10 text-destructive hover:bg-destructive/20"
          : "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 hover:bg-yellow-500/20"
      )}
    >
      {errors.length > 0 ? (
        <>
          <XCircle className="h-3.5 w-3.5" />
          <span>{errors.length}</span>
        </>
      ) : (
        <>
          <AlertTriangle className="h-3.5 w-3.5" />
          <span>{warnings.length}</span>
        </>
      )}
    </button>
  );
}
