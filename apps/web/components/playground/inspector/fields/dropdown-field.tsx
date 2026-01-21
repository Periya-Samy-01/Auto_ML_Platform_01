"use client";

import { cn } from "@/lib/utils";
import { HelpCircle, ChevronDown } from "lucide-react";
import type { SelectField as DropdownFieldType } from "@/configs/algorithms/types";

interface DropdownFieldProps {
  field: DropdownFieldType;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function DropdownField({ field, value, onChange, disabled }: DropdownFieldProps) {
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
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className={cn(
            "w-full px-3 py-2 pr-8 rounded-lg text-sm appearance-none",
            "bg-input border border-border text-foreground",
            "hover:border-border/80",
            "focus:outline-none focus:ring-2 focus:ring-ring/50",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          {field.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
      </div>
    </div>
  );
}
