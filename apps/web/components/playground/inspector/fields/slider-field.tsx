"use client";

import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";
import type { SliderField as SliderFieldType } from "@/configs/algorithms/types";

interface SliderFieldProps {
  field: SliderFieldType;
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export function SliderField({ field, value, onChange, disabled }: SliderFieldProps) {
  const displayValue = field.displayFormat
    ? field.displayFormat(value)
    : `${value}${field.unit || ""}`;

  // Calculate percentage for gradient
  const percentage = ((value - field.min) / (field.max - field.min)) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
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
        <span className="text-xs font-mono text-primary">{displayValue}</span>
      </div>
      {field.description && (
        <p className="text-xs text-muted-foreground">{field.description}</p>
      )}
      <div className="relative">
        <input
          type="range"
          min={field.min}
          max={field.max}
          step={field.step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          disabled={disabled}
          className={cn(
            "w-full h-2 rounded-full appearance-none cursor-pointer",
            "bg-muted",
            "[&::-webkit-slider-thumb]:appearance-none",
            "[&::-webkit-slider-thumb]:w-4",
            "[&::-webkit-slider-thumb]:h-4",
            "[&::-webkit-slider-thumb]:rounded-full",
            "[&::-webkit-slider-thumb]:bg-primary",
            "[&::-webkit-slider-thumb]:cursor-pointer",
            "[&::-webkit-slider-thumb]:shadow-lg",
            "[&::-webkit-slider-thumb]:transition-transform",
            "[&::-webkit-slider-thumb]:hover:scale-110",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          style={{
            background: `linear-gradient(to right, hsl(var(--primary)) 0%, hsl(var(--primary)) ${percentage}%, hsl(var(--muted)) ${percentage}%, hsl(var(--muted)) 100%)`,
          }}
        />
        <div className="flex justify-between mt-1">
          <span className="text-[10px] text-muted-foreground">{field.min}{field.unit || ""}</span>
          <span className="text-[10px] text-muted-foreground">{field.max}{field.unit || ""}</span>
        </div>
      </div>
    </div>
  );
}
