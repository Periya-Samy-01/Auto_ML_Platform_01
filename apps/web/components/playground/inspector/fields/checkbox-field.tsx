"use client";

import { cn } from "@/lib/utils";
import { HelpCircle, Check } from "lucide-react";

interface CheckboxFieldProps {
  id: string;
  label: string;
  description?: string;
  tooltip?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export function CheckboxField({
  id,
  label,
  description,
  tooltip,
  checked,
  onChange,
  disabled,
}: CheckboxFieldProps) {
  return (
    <label
      htmlFor={id}
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all",
        "border",
        checked
          ? "bg-primary/10 border-primary/30"
          : "bg-muted/30 border-border hover:bg-muted/50",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <div className="relative flex-shrink-0 mt-0.5">
        <input
          type="checkbox"
          id={id}
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only"
        />
        <div
          className={cn(
            "w-5 h-5 rounded border-2 transition-all flex items-center justify-center",
            checked
              ? "bg-primary border-primary"
              : "bg-transparent border-muted-foreground"
          )}
        >
          {checked && <Check className="w-3 h-3 text-primary-foreground" strokeWidth={3} />}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-foreground">{label}</span>
          {tooltip && (
            <div className="group relative">
              <HelpCircle className="w-3 h-3 text-muted-foreground cursor-help" />
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-popover border border-border rounded-lg text-xs text-popover-foreground shadow-lg z-10">
                {tooltip}
              </div>
            </div>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
        )}
      </div>
    </label>
  );
}
