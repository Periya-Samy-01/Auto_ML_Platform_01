"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface InspectorSectionProps {
  title: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
  className?: string;
}

/**
 * Collapsible section component for inspector panels.
 * Provides consistent styling across all inspector components.
 */
export function InspectorSection({
  title,
  icon,
  badge,
  defaultOpen = true,
  children,
  className,
}: InspectorSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={cn("border-b border-border last:border-b-0", className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-foreground">{title}</span>
          {badge}
        </div>
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        )}
      </button>
      {isOpen && <div className="px-4 pb-4 space-y-4">{children}</div>}
    </div>
  );
}

/**
 * Info box for displaying helpful tips in inspectors.
 */
export function InspectorInfoBox({
  children,
  variant = "info",
}: {
  children: React.ReactNode;
  variant?: "info" | "warning" | "error" | "success";
}) {
  const variantStyles = {
    info: "bg-primary/10 border-primary/20 text-primary",
    warning: "bg-yellow-500/10 border-yellow-500/20 text-yellow-500",
    error: "bg-destructive/10 border-destructive/20 text-destructive",
    success: "bg-emerald-500/10 border-emerald-500/20 text-emerald-500",
  };

  return (
    <div className={cn("p-3 rounded-lg border", variantStyles[variant])}>
      {children}
    </div>
  );
}

/**
 * Empty state component for inspectors when no upstream node is connected.
 */
export function InspectorEmptyState({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4">
      <div className="text-yellow-500 mb-4">{icon}</div>
      <h3 className="text-sm font-medium text-foreground mb-2">{title}</h3>
      <p className="text-xs text-muted-foreground text-center">{description}</p>
    </div>
  );
}
