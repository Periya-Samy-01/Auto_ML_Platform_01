"use client";

import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";
import type { SwitchField as SwitchFieldType } from "@/configs/algorithms/types";

interface SwitchFieldProps {
  field: SwitchFieldType;
  value: boolean;
  onChange: (value: boolean) => void;
  disabled?: boolean;
}

export function SwitchField({ field, value, onChange, disabled }: SwitchFieldProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-foreground">{field.label}</label>
          {field.tooltip && (
            <div className="group relative">
              <HelpCircle className="w-3 h-3 text-muted-foreground cursor-help" />
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-popover border border-border rounded-lg text-xs text-popover-foreground shadow-lg z-10">
                {field.tooltip}
              </div>
            </div>
          )}
        </div>
        {field.description && (
          <p className="text-xs text-muted-foreground mt-1">{field.description}</p>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={value}
        onClick={() => onChange(!value)}
        disabled={disabled}
        className={cn(
          "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full",
          "transition-colors duration-200 ease-in-out",
          "focus:outline-none focus:ring-2 focus:ring-ring/50 focus:ring-offset-2 focus:ring-offset-background",
          value ? "bg-primary" : "bg-muted",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <span
          className={cn(
            "pointer-events-none inline-block h-4 w-4 transform rounded-full",
            "bg-white shadow-lg ring-0 transition duration-200 ease-in-out",
            "mt-0.5",
            value ? "translate-x-4 ml-0.5" : "translate-x-0.5"
          )}
        />
      </button>
    </div>
  );
}
