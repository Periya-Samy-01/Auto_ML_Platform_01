"use client";

/**
 * View Toggle
 * Toggle between table and card views
 */

import { LayoutGrid, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ViewMode = "table" | "grid";

interface ViewToggleProps {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
}

export function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="flex items-center rounded-lg border bg-muted/50 p-1">
      <Button
        variant="ghost"
        size="sm"
        className={cn(
          "h-8 px-3",
          value === "table" && "bg-background shadow-sm"
        )}
        onClick={() => onChange("table")}
      >
        <List className="h-4 w-4" />
        <span className="sr-only">Table view</span>
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={cn(
          "h-8 px-3",
          value === "grid" && "bg-background shadow-sm"
        )}
        onClick={() => onChange("grid")}
      >
        <LayoutGrid className="h-4 w-4" />
        <span className="sr-only">Grid view</span>
      </Button>
    </div>
  );
}
