/**
 * Algorithm Renderer Utilities
 *
 * This module provides functions for dynamic rendering of algorithm configurations.
 * It handles field rendering, validation, and cost calculation based on config files.
 */

import type {
  HyperparameterField,
  AlgorithmId,
  AlgorithmConfig,
} from "@/configs/algorithms/types";
import {
  getAlgorithmConfig,
  getDefaultHyperparameters,
  validateHyperparameters,
  calculateTrainingCost,
} from "@/configs/algorithms";

// Re-export for convenience
export {
  getAlgorithmConfig,
  getDefaultHyperparameters,
  validateHyperparameters,
  calculateTrainingCost,
};

/**
 * Get hyperparameter fields for an algorithm, optionally filtered by section
 */
export function getHyperparameterFields(
  algorithmId: AlgorithmId,
  section?: "main" | "advanced"
): HyperparameterField[] {
  const config = getAlgorithmConfig(algorithmId);
  if (!config) return [];

  if (section === "main") {
    return config.model.hyperparameters.filter((f) => !f.advanced);
  }
  if (section === "advanced") {
    return config.model.hyperparameters.filter((f) => f.advanced);
  }
  return config.model.hyperparameters;
}

/**
 * Check if a field should be visible based on its dependsOn condition
 */
export function isFieldVisible(
  field: HyperparameterField,
  currentValues: Record<string, unknown>
): boolean {
  if (!field.dependsOn) return true;
  return currentValues[field.dependsOn.field] === field.dependsOn.value;
}

/**
 * Get visible fields based on current hyperparameter values
 */
export function getVisibleFields(
  algorithmId: AlgorithmId,
  currentValues: Record<string, unknown>,
  section?: "main" | "advanced"
): HyperparameterField[] {
  const fields = getHyperparameterFields(algorithmId, section);
  return fields.filter((field) => isFieldVisible(field, currentValues));
}

/**
 * Get validation errors with context
 */
export interface ValidationResult {
  valid: boolean;
  errors: Record<string, string>;
  warnings: string[];
}

export function validateWithContext(
  algorithmId: AlgorithmId,
  values: Record<string, unknown>,
  context?: { datasetSize?: number; hasImbalancedClasses?: boolean }
): ValidationResult {
  const result = validateHyperparameters(algorithmId, values);
  const warnings: string[] = [];
  const config = getAlgorithmConfig(algorithmId);

  if (config && context) {
    // Add contextual warnings
    if (context.hasImbalancedClasses && values.class_weight === "none") {
      warnings.push(
        "Your dataset has imbalanced classes. Consider using 'Balanced' class weight."
      );
    }

    if (
      context.datasetSize &&
      context.datasetSize > 10000 &&
      values.solver === "liblinear"
    ) {
      warnings.push(
        "For large datasets (>10k samples), 'SAGA' or 'LBFGS' solver may be faster."
      );
    }
  }

  return {
    ...result,
    warnings,
  };
}

/**
 * Get algorithm capabilities
 */
export function getAlgorithmCapabilities(algorithmId: AlgorithmId) {
  const config = getAlgorithmConfig(algorithmId);
  if (!config) return null;

  return {
    algorithm: algorithmId,
    ...config.capabilities,
    supportedMetrics: config.evaluate.supportedMetrics,
    defaultMetrics: config.evaluate.defaultMetrics,
    supportedPlots: config.visualize.supportedPlots,
    defaultPlots: config.visualize.defaultPlots,
  };
}

/**
 * Get supported metrics for an algorithm
 */
export function getSupportedMetrics(algorithmId: AlgorithmId) {
  const config = getAlgorithmConfig(algorithmId);
  if (!config) return { supported: [], defaults: [], definitions: {} };

  return {
    supported: config.evaluate.supportedMetrics,
    defaults: config.evaluate.defaultMetrics,
    definitions: config.evaluate.metricDefinitions,
  };
}

/**
 * Get supported plots for an algorithm
 */
export function getSupportedPlots(algorithmId: AlgorithmId) {
  const config = getAlgorithmConfig(algorithmId);
  if (!config) return { supported: [], defaults: [], definitions: {} };

  return {
    supported: config.visualize.supportedPlots,
    defaults: config.visualize.defaultPlots,
    definitions: config.visualize.plotDefinitions,
  };
}

/**
 * Calculate total cost for a workflow configuration
 */
export interface WorkflowCostOptions {
  algorithmId: AlgorithmId;
  sampleCount: number;
  useCrossValidation: boolean;
  useOptuna: boolean;
  optunaTrials?: number;
  selectedMetrics?: string[];
  selectedPlots?: string[];
}

export function calculateWorkflowCost(options: WorkflowCostOptions): number {
  const {
    algorithmId,
    sampleCount,
    useCrossValidation,
    useOptuna,
    optunaTrials,
    selectedPlots = [],
  } = options;

  // Base training cost
  let totalCost = calculateTrainingCost(algorithmId, {
    sampleCount,
    useCrossValidation,
    useOptuna,
    optunaTrials,
  });

  // Add plot costs
  const config = getAlgorithmConfig(algorithmId);
  if (config) {
    for (const plotKey of selectedPlots) {
      const plotDef = config.visualize.plotDefinitions[plotKey as keyof typeof config.visualize.plotDefinitions];
      if (plotDef) {
        totalCost += plotDef.cost;
      }
    }
  }

  return Math.ceil(totalCost);
}

/**
 * Get algorithm metadata for display
 */
export function getAlgorithmMetadata(algorithmId: AlgorithmId) {
  const config = getAlgorithmConfig(algorithmId);
  if (!config) return null;

  return config.metadata;
}

/**
 * Get all available algorithms with their metadata
 */
export function getAllAlgorithmsWithMetadata(): Array<{
  id: AlgorithmId;
  name: string;
  shortName: string;
  description: string;
  icon: string;
  category: string;
  problemTypes: string[];
}> {
  const { algorithmRegistry } = require("@/configs/algorithms");

  return Object.entries(algorithmRegistry).map(([id, config]) => {
    const cfg = config as AlgorithmConfig;
    return {
      id: id as AlgorithmId,
      name: cfg.metadata.name,
      shortName: cfg.metadata.shortName,
      description: cfg.metadata.description,
      icon: cfg.metadata.icon,
      category: cfg.metadata.category,
      problemTypes: cfg.capabilities.problemTypes,
    };
  });
}
