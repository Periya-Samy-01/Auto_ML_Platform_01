"use client";

import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";
import type { NumberField as NumberFieldType } from "@/configs/algorithms/types";

interface NumberFieldProps {
  field: NumberFieldType;
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
  error?: string;
}

export function NumberField({ field, value, onChange, disabled, error }: NumberFieldProps) {
  return (
    <div className="space-y-2">
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
        <p className="text-xs text-muted-foreground">{field.description}</p>
      )}
      <input
        type="number"
        min={field.min}
        max={field.max}
        step={field.step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        placeholder={field.placeholder}
        disabled={disabled}
        className={cn(
          "w-full px-3 py-2 rounded-lg text-sm",
          "bg-input border text-foreground",
          "placeholder:text-muted-foreground",
          "focus:outline-none focus:ring-2 focus:ring-ring/50",
          error
            ? "border-destructive/50"
            : "border-border hover:border-border/80",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      />
      {error && (
        <p className="text-xs text-destructive">{error}</p>
      )}
    </div>
  );
}
