"use client";

import { cn } from "@/lib/utils";
import { HelpCircle } from "lucide-react";

interface RangeFieldProps {
  label: string;
  description?: string;
  tooltip?: string;
  minValue: number;
  maxValue: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (minValue: number, maxValue: number) => void;
  disabled?: boolean;
}

export function RangeField({
  label,
  description,
  tooltip,
  minValue,
  maxValue,
  min,
  max,
  step = 1,
  unit = "",
  onChange,
  disabled,
}: RangeFieldProps) {
  const minPercent = ((minValue - min) / (max - min)) * 100;
  const maxPercent = ((maxValue - min) / (max - min)) * 100;

  const handleMinChange = (newMin: number) => {
    // Ensure min doesn't exceed max
    const clampedMin = Math.min(newMin, maxValue);
    onChange(clampedMin, maxValue);
  };

  const handleMaxChange = (newMax: number) => {
    // Ensure max doesn't go below min
    const clampedMax = Math.max(newMax, minValue);
    onChange(minValue, clampedMax);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-foreground">{label}</label>
          {tooltip && (
            <div className="group relative">
              <HelpCircle className="w-3 h-3 text-muted-foreground cursor-help" />
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-popover border border-border rounded-lg text-xs text-popover-foreground shadow-lg z-10">
                {tooltip}
              </div>
            </div>
          )}
        </div>
        <span className="text-xs font-mono text-primary">
          {minValue}{unit} - {maxValue}{unit}
        </span>
      </div>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}

      {/* Dual range slider container */}
      <div className="relative h-6 pt-2">
        {/* Track background */}
        <div className="absolute w-full h-2 bg-muted rounded-full" />

        {/* Active range highlight */}
        <div
          className="absolute h-2 bg-primary/60 rounded-full"
          style={{
            left: `${minPercent}%`,
            width: `${maxPercent - minPercent}%`,
          }}
        />

        {/* Min slider */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={minValue}
          onChange={(e) => handleMinChange(parseFloat(e.target.value))}
          disabled={disabled}
          className={cn(
            "absolute w-full h-2 appearance-none bg-transparent cursor-pointer z-10",
            "[&::-webkit-slider-thumb]:appearance-none",
            "[&::-webkit-slider-thumb]:w-4",
            "[&::-webkit-slider-thumb]:h-4",
            "[&::-webkit-slider-thumb]:rounded-full",
            "[&::-webkit-slider-thumb]:bg-primary",
            "[&::-webkit-slider-thumb]:cursor-pointer",
            "[&::-webkit-slider-thumb]:shadow-lg",
            "[&::-webkit-slider-thumb]:transition-transform",
            "[&::-webkit-slider-thumb]:hover:scale-110",
            "[&::-webkit-slider-thumb]:relative",
            "[&::-webkit-slider-thumb]:z-20",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        />

        {/* Max slider */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={maxValue}
          onChange={(e) => handleMaxChange(parseFloat(e.target.value))}
          disabled={disabled}
          className={cn(
            "absolute w-full h-2 appearance-none bg-transparent cursor-pointer z-10",
            "[&::-webkit-slider-thumb]:appearance-none",
            "[&::-webkit-slider-thumb]:w-4",
            "[&::-webkit-slider-thumb]:h-4",
            "[&::-webkit-slider-thumb]:rounded-full",
            "[&::-webkit-slider-thumb]:bg-primary",
            "[&::-webkit-slider-thumb]:cursor-pointer",
            "[&::-webkit-slider-thumb]:shadow-lg",
            "[&::-webkit-slider-thumb]:transition-transform",
            "[&::-webkit-slider-thumb]:hover:scale-110",
            "[&::-webkit-slider-thumb]:relative",
            "[&::-webkit-slider-thumb]:z-20",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        />
      </div>

      {/* Range labels */}
      <div className="flex justify-between">
        <span className="text-[10px] text-muted-foreground">{min}{unit}</span>
        <span className="text-[10px] text-muted-foreground">{max}{unit}</span>
      </div>

      {/* Manual input fields */}
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <label className="text-[10px] text-muted-foreground block mb-1">Min</label>
          <input
            type="number"
            min={min}
            max={maxValue}
            step={step}
            value={minValue}
            onChange={(e) => handleMinChange(parseFloat(e.target.value))}
            disabled={disabled}
            className={cn(
              "w-full px-2 py-1 rounded text-xs",
              "bg-input border border-border text-foreground",
              "focus:outline-none focus:ring-1 focus:ring-ring/50",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          />
        </div>
        <span className="text-muted-foreground mt-4">-</span>
        <div className="flex-1">
          <label className="text-[10px] text-muted-foreground block mb-1">Max</label>
          <input
            type="number"
            min={minValue}
            max={max}
            step={step}
            value={maxValue}
            onChange={(e) => handleMaxChange(parseFloat(e.target.value))}
            disabled={disabled}
            className={cn(
              "w-full px-2 py-1 rounded text-xs",
              "bg-input border border-border text-foreground",
              "focus:outline-none focus:ring-1 focus:ring-ring/50",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          />
        </div>
      </div>
    </div>
  );
}
