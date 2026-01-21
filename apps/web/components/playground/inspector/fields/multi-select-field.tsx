"use client";

import { cn } from "@/lib/utils";
import { HelpCircle, Check, X } from "lucide-react";
import type { MultiSelectField as MultiSelectFieldType } from "@/configs/algorithms/types";

interface MultiSelectFieldProps {
  field: MultiSelectFieldType;
  value: string[];
  onChange: (value: string[]) => void;
  disabled?: boolean;
}

export function MultiSelectField({ field, value, onChange, disabled }: MultiSelectFieldProps) {
  const handleToggle = (optionValue: string) => {
    if (value.includes(optionValue)) {
      onChange(value.filter((v) => v !== optionValue));
    } else {
      onChange([...value, optionValue]);
    }
  };

  const handleClear = () => {
    onChange([]);
  };

  const selectedCount = value.length;

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
        {selectedCount > 0 && (
          <button
            type="button"
            onClick={handleClear}
            disabled={disabled}
            className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
          >
            <X className="w-3 h-3" />
            Clear ({selectedCount})
          </button>
        )}
      </div>
      {field.description && (
        <p className="text-xs text-muted-foreground">{field.description}</p>
      )}
      <div className="space-y-1.5 max-h-48 overflow-y-auto">
        {field.options.map((option) => {
          const isSelected = value.includes(option.value);
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => handleToggle(option.value)}
              disabled={disabled}
              className={cn(
                "w-full flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-all text-left",
                "border",
                isSelected
                  ? "bg-primary/10 border-primary/30"
                  : "bg-muted/30 border-border hover:bg-muted/50",
                disabled && "opacity-50 cursor-not-allowed"
              )}
            >
              <div
                className={cn(
                  "flex-shrink-0 w-4 h-4 rounded border transition-all flex items-center justify-center",
                  isSelected
                    ? "bg-primary border-primary"
                    : "bg-transparent border-muted-foreground"
                )}
              >
                {isSelected && <Check className="w-3 h-3 text-primary-foreground" strokeWidth={3} />}
              </div>
              <span className="text-sm text-foreground">{option.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
