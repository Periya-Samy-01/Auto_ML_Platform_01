/**
 * Algorithm Configuration Registry
 *
 * Central registry for all algorithm configurations.
 * Import algorithms here and add them to the registry.
 */

export * from "./types";

// Algorithm config exports
export { logisticRegressionConfig } from "./logisticRegression";
export { linearRegressionConfig } from "./linearRegression";
export { decisionTreeConfig } from "./decisionTree";
export { randomForestConfig } from "./randomForest";
export { xgboostConfig } from "./xgboost";
export { knnConfig } from "./knn";
export { naiveBayesConfig } from "./naiveBayes";
export { svmConfig } from "./svm";
export { neuralNetworkConfig } from "./neuralNetwork";
export { kmeansConfig } from "./kmeans";

import type { AlgorithmConfig, AlgorithmId, AlgorithmMetadata } from "./types";
import { logisticRegressionConfig } from "./logisticRegression";
import { linearRegressionConfig } from "./linearRegression";
import { decisionTreeConfig } from "./decisionTree";
import { randomForestConfig } from "./randomForest";
import { xgboostConfig } from "./xgboost";
import { knnConfig } from "./knn";
import { naiveBayesConfig } from "./naiveBayes";
import { svmConfig } from "./svm";
import { neuralNetworkConfig } from "./neuralNetwork";
import { kmeansConfig } from "./kmeans";

/**
 * Registry of all available algorithms.
 */
export const algorithmRegistry: Partial<Record<AlgorithmId, AlgorithmConfig>> = {
  logistic_regression: logisticRegressionConfig,
  linear_regression: linearRegressionConfig,
  decision_tree: decisionTreeConfig,
  random_forest: randomForestConfig,
  xgboost: xgboostConfig,
  knn: knnConfig,
  naive_bayes: naiveBayesConfig,
  svm: svmConfig,
  neural_network: neuralNetworkConfig,
  kmeans: kmeansConfig,
  // pca: pcaConfig, // Not implemented yet
};

/**
 * Get algorithm config by ID
 */
export function getAlgorithmConfig(id: AlgorithmId): AlgorithmConfig | undefined {
  return algorithmRegistry[id];
}

/**
 * Get all available algorithm IDs
 */
export function getAvailableAlgorithms(): AlgorithmId[] {
  return Object.keys(algorithmRegistry) as AlgorithmId[];
}

/**
 * Get algorithms filtered by problem type
 */
export function getAlgorithmsByProblemType(
  problemType: "classification" | "regression"
): AlgorithmId[] {
  return (Object.entries(algorithmRegistry) as [AlgorithmId, AlgorithmConfig][])
    .filter(([, config]) => config.capabilities.problemTypes.includes(problemType))
    .map(([id]) => id);
}

/**
 * Get all algorithms with their metadata
 */
export function getAllAlgorithmsWithMetadata(): Array<{
  id: AlgorithmId;
  metadata: AlgorithmMetadata;
  problemTypes: ("classification" | "regression")[];
}> {
  return (Object.entries(algorithmRegistry) as [AlgorithmId, AlgorithmConfig][]).map(
    ([id, config]) => ({
      id,
      metadata: config.metadata,
      problemTypes: config.capabilities.problemTypes,
    })
  );
}

/**
 * Get default hyperparameter values for an algorithm
 */
export function getDefaultHyperparameters(id: AlgorithmId): Record<string, unknown> {
  const config = algorithmRegistry[id];
  if (!config) return {};

  const defaults: Record<string, unknown> = {};
  for (const field of config.model.hyperparameters) {
    defaults[field.key] = field.default;
  }
  return defaults;
}

/**
 * Get hyperparameter fields for an algorithm
 */
export function getHyperparameterFields(
  id: AlgorithmId,
  section?: "main" | "advanced"
) {
  const config = algorithmRegistry[id];
  if (!config) return [];

  const fields = config.model.hyperparameters;

  if (section === "main") {
    return fields.filter((f) => !f.advanced);
  } else if (section === "advanced") {
    return fields.filter((f) => f.advanced);
  }

  return fields;
}

/**
 * Check if a field should be visible based on dependsOn
 */
export function isFieldVisible(
  field: { dependsOn?: { field: string; value: unknown } },
  currentValues: Record<string, unknown>
): boolean {
  if (!field.dependsOn) return true;

  const dependentValue = currentValues[field.dependsOn.field];

  // If dependsOn value is defined, check for exact match
  if (field.dependsOn.value !== undefined) {
    return dependentValue === field.dependsOn.value;
  }

  // Otherwise, check that dependent field has a truthy value
  return Boolean(dependentValue);
}

/**
 * Get visible fields based on current values
 */
export function getVisibleFields(
  id: AlgorithmId,
  currentValues: Record<string, unknown>,
  section?: "main" | "advanced"
) {
  const fields = getHyperparameterFields(id, section);
  return fields.filter((field) => isFieldVisible(field, currentValues));
}

/**
 * Validate hyperparameters for an algorithm
 */
export function validateHyperparameters(
  id: AlgorithmId,
  values: Record<string, unknown>
): { valid: boolean; errors: Record<string, string> } {
  const config = algorithmRegistry[id];
  if (!config) return { valid: false, errors: { _: "Unknown algorithm" } };

  const errors: Record<string, string> = {};

  // Field-level validation
  for (const fieldValidation of config.model.validation.fields) {
    const value = values[fieldValidation.field];
    for (const rule of fieldValidation.rules) {
      switch (rule.type) {
        case "required":
          if (value === undefined || value === null || value === "") {
            errors[fieldValidation.field] = rule.message;
          }
          break;
        case "min":
          if (typeof value === "number" && value < (rule.value as number)) {
            errors[fieldValidation.field] = rule.message;
          }
          break;
        case "max":
          if (typeof value === "number" && value > (rule.value as number)) {
            errors[fieldValidation.field] = rule.message;
          }
          break;
      }
    }
  }

  // Cross-field validation
  if (config.model.validation.crossField) {
    for (const crossValidation of config.model.validation.crossField) {
      const error = crossValidation.validate(values);
      if (error) {
        errors[crossValidation.fields.join("_")] = error;
      }
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Calculate training cost for an algorithm
 */
export function calculateTrainingCost(
  id: AlgorithmId,
  options: {
    sampleCount: number;
    useCrossValidation: boolean;
    cvFolds?: number;
    useOptuna: boolean;
    optunaTrials?: number;
  }
): number {
  const config = algorithmRegistry[id];
  if (!config) return 0;

  const {
    sampleCount,
    useCrossValidation,
    cvFolds = 5,
    useOptuna,
    optunaTrials = 50,
  } = options;
  const costs = config.model.costs;

  let total = costs.base;

  // Add per-sample cost
  if (costs.perSample) {
    total += sampleCount * costs.perSample;
  }

  // Multiply by CV folds if using cross-validation
  if (useCrossValidation) {
    total *= cvFolds;
  }

  // Add Optuna cost
  if (useOptuna) {
    const trials = Math.min(optunaTrials, costs.optuna.maxTrials);
    total += trials * costs.optuna.perTrial;
  }

  return Math.ceil(total);
}

/**
 * Get evaluation metrics for an algorithm
 */
export function getEvaluationMetrics(id: AlgorithmId) {
  const config = algorithmRegistry[id];
  if (!config) return { supported: [], defaults: [], definitions: {} };

  return {
    supported: config.evaluate.supportedMetrics,
    defaults: config.evaluate.defaultMetrics,
    definitions: config.evaluate.metricDefinitions,
  };
}

/**
 * Get visualization plots for an algorithm
 */
export function getVisualizationPlots(id: AlgorithmId) {
  const config = algorithmRegistry[id];
  if (!config) return { supported: [], defaults: [], definitions: {} };

  return {
    supported: config.visualize.supportedPlots,
    defaults: config.visualize.defaultPlots,
    definitions: config.visualize.plotDefinitions,
  };
}

/**
 * Get algorithm capabilities
 */
export function getAlgorithmCapabilities(id: AlgorithmId) {
  const config = algorithmRegistry[id];
  if (!config) return null;

  return {
    ...config.capabilities,
    supportedMetrics: config.evaluate.supportedMetrics,
    defaultMetrics: config.evaluate.defaultMetrics,
    supportedPlots: config.visualize.supportedPlots,
    defaultPlots: config.visualize.defaultPlots,
  };
}
