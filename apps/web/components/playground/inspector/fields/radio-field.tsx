"use client";

import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";
import type { RadioField as RadioFieldType } from "@/configs/algorithms/types";

interface RadioFieldProps {
  field: RadioFieldType;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function RadioField({ field, value, onChange, disabled }: RadioFieldProps) {
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
      <div className="space-y-1">
        {field.options.map((option) => (
          <label
            key={option.value}
            className={cn(
              "flex items-start gap-3 p-2.5 rounded-lg cursor-pointer transition-all",
              "border",
              value === option.value
                ? "bg-primary/10 border-primary/30"
                : "bg-muted/30 border-border hover:bg-muted/50",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            <input
              type="radio"
              name={field.key}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              disabled={disabled}
              className="mt-0.5 w-4 h-4 accent-primary"
            />
            <div className="flex-1 min-w-0">
              <span className="text-sm text-foreground">{option.label}</span>
              {option.description && (
                <p className="text-xs text-muted-foreground mt-0.5">{option.description}</p>
              )}
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}
