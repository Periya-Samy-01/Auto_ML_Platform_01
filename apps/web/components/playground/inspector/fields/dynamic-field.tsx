"use client";

import type { HyperparameterField } from "@/configs/algorithms/types";
import { RadioField } from "./radio-field";
import { SliderField } from "./slider-field";
import { NumberField } from "./number-field";
import { SelectField } from "./select-field";
import { SwitchField } from "./switch-field";
import { TextField } from "./text-field";
import { MultiSelectField } from "./multi-select-field";

interface DynamicFieldProps {
  field: HyperparameterField;
  value: unknown;
  onChange: (value: unknown) => void;
  disabled?: boolean;
  error?: string;
  allValues?: Record<string, unknown>; // For dependsOn checking
}

/**
 * Renders any hyperparameter field based on its type.
 * This is the main component used by inspectors to render config-driven fields.
 */
export function DynamicField({
  field,
  value,
  onChange,
  disabled,
  error,
  allValues = {},
}: DynamicFieldProps) {
  // Check if this field should be shown based on dependsOn
  if (field.dependsOn) {
    const dependencyValue = allValues[field.dependsOn.field];
    if (dependencyValue !== field.dependsOn.value) {
      return null;
    }
  }

  switch (field.type) {
    case "radio":
      return (
        <RadioField
          field={field}
          value={value as string}
          onChange={onChange as (v: string) => void}
          disabled={disabled}
        />
      );

    case "slider":
      return (
        <SliderField
          field={field}
          value={value as number}
          onChange={onChange as (v: number) => void}
          disabled={disabled}
        />
      );

    case "number":
      return (
        <NumberField
          field={field}
          value={value as number}
          onChange={onChange as (v: number) => void}
          disabled={disabled}
          error={error}
        />
      );

    case "select":
      return (
        <SelectField
          field={field}
          value={value as string}
          onChange={onChange as (v: string) => void}
          disabled={disabled}
        />
      );

    case "switch":
      return (
        <SwitchField
          field={field}
          value={value as boolean}
          onChange={onChange as (v: boolean) => void}
          disabled={disabled}
        />
      );

    case "text":
      return (
        <TextField
          field={field}
          value={value as string}
          onChange={onChange as (v: string) => void}
          disabled={disabled}
          error={error}
        />
      );

    case "multiSelect":
      return (
        <MultiSelectField
          field={field}
          value={value as string[]}
          onChange={onChange as (v: string[]) => void}
          disabled={disabled}
        />
      );

    default:
      return null;
  }
}
