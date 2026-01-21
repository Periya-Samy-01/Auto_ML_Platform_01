/**
 * Algorithm Configuration Types
 *
 * This file defines the TypeScript types for the config-driven algorithm architecture.
 * Each algorithm is defined in a single config file that contains ALL configuration
 * for model training, evaluation, and visualization.
 */

// =============================================================================
// Field Types - Define UI components for hyperparameters
// =============================================================================

export type FieldType =
  | "radio"
  | "slider"
  | "number"
  | "select"
  | "switch"
  | "text"
  | "multiSelect";

export interface BaseField {
  key: string;
  label: string;
  type: FieldType;
  description?: string;
  tooltip?: string;
  advanced?: boolean; // If true, shown in "Advanced" section
  dependsOn?: {
    field: string;
    value: unknown;
  };
}

export interface RadioField extends BaseField {
  type: "radio";
  options: Array<{
    value: string;
    label: string;
    description?: string;
  }>;
  default: string;
}

export interface SliderField extends BaseField {
  type: "slider";
  min: number;
  max: number;
  step: number;
  default: number;
  unit?: string;
  displayFormat?: (value: number) => string;
}

export interface NumberField extends BaseField {
  type: "number";
  min?: number;
  max?: number;
  step?: number;
  default: number;
  placeholder?: string;
}

export interface SelectField extends BaseField {
  type: "select";
  options: Array<{
    value: string;
    label: string;
  }>;
  default: string;
}

export interface SwitchField extends BaseField {
  type: "switch";
  default: boolean;
}

export interface TextField extends BaseField {
  type: "text";
  default: string;
  placeholder?: string;
}

export interface MultiSelectField extends BaseField {
  type: "multiSelect";
  options: Array<{
    value: string;
    label: string;
  }>;
  default: string[];
}

export type HyperparameterField =
  | RadioField
  | SliderField
  | NumberField
  | SelectField
  | SwitchField
  | TextField
  | MultiSelectField;

// =============================================================================
// Validation Types
// =============================================================================

export interface ValidationRule {
  type: "required" | "min" | "max" | "minLength" | "pattern" | "custom";
  value?: unknown;
  message: string;
}

export interface FieldValidation {
  field: string;
  rules: ValidationRule[];
}

export interface CrossFieldValidation {
  fields: string[];
  validate: (values: Record<string, unknown>) => string | null;
  message: string;
}

export interface ModelValidation {
  fields: FieldValidation[];
  crossField?: CrossFieldValidation[];
}

// =============================================================================
// Optuna Configuration
// =============================================================================

export type OptunaDistribution =
  | { type: "categorical"; choices: (string | number | boolean)[] }
  | { type: "int"; low: number; high: number; step?: number; log?: boolean }
  | { type: "float"; low: number; high: number; step?: number; log?: boolean };

export interface OptunaSearchSpace {
  [paramName: string]: OptunaDistribution;
}

export interface OptunaConfig {
  searchSpace: OptunaSearchSpace;
  nTrials: number;
  timeout?: number; // seconds
  pruner?: "median" | "hyperband" | "none";
}

// =============================================================================
// Cost Configuration
// =============================================================================

export interface CostConfig {
  base: number; // Base credits for single training run
  perSample?: number; // Additional cost per sample (for large datasets)
  crossValidation: {
    multiplier: number; // e.g., 5 for 5-fold CV
  };
  optuna: {
    perTrial: number;
    maxTrials: number;
  };
}

// =============================================================================
// Evaluation Configuration
// =============================================================================

export type MetricCategory = "classification" | "regression" | "clustering";

export interface MetricDefinition {
  key: string;
  name: string;
  formula?: string;
  range: [number, number] | "unbounded";
  higherIsBetter: boolean;
  tooltip: string;
  category: MetricCategory;
}

export interface EvaluationConfig {
  supportedMetrics: string[];
  defaultMetrics: string[];
  metricDefinitions: Record<string, MetricDefinition>;
}

// =============================================================================
// Visualization Configuration
// =============================================================================

export type PlotType =
  | "confusion_matrix"
  | "roc_curve"
  | "precision_recall_curve"
  | "learning_curve"
  | "feature_importance"
  | "residual_plot"
  | "prediction_vs_actual"
  | "coefficient_plot"
  | "probability_calibration"
  | "shap_summary"
  | "shap_waterfall"
  | "partial_dependence";

export interface PlotDefinition {
  key: PlotType;
  name: string;
  description: string;
  requirements?: {
    minSamples?: number;
    requiresProbabilities?: boolean;
    requiresFeatureImportance?: boolean;
  };
  cost: number;
  configOptions?: HyperparameterField[];
}

export interface VisualizationConfig {
  supportedPlots: PlotType[];
  defaultPlots: PlotType[];
  plotDefinitions: Record<PlotType, PlotDefinition>;
}

// =============================================================================
// Algorithm Capabilities
// =============================================================================

export interface AlgorithmCapabilities {
  problemTypes: ("classification" | "regression")[];
  supportsMulticlass: boolean;
  supportsProbabilities: boolean;
  supportsFeatureImportance: boolean;
  supportsExplainability: boolean;
  handlesImbalanced: boolean;
  handlesMissingValues: boolean;
  requiresScaling: boolean;
  supportsWarmStart: boolean;
}

// =============================================================================
// Main Algorithm Config
// =============================================================================

export interface AlgorithmMetadata {
  id: string;
  name: string;
  shortName: string;
  description: string;
  icon: string;
  category: "linear" | "tree" | "ensemble" | "neural" | "clustering" | "dimensionality";
  bestFor: string[];
  limitations: string[];
  learnMoreUrl?: string;
}

export interface ModelConfig {
  hyperparameters: HyperparameterField[];
  validation: ModelValidation;
  optuna: OptunaConfig;
  costs: CostConfig;
}

export interface AlgorithmConfig {
  metadata: AlgorithmMetadata;
  capabilities: AlgorithmCapabilities;
  model: ModelConfig;
  evaluate: EvaluationConfig;
  visualize: VisualizationConfig;
}

// =============================================================================
// Registry
// =============================================================================

export type AlgorithmId =
  | "logistic_regression"
  | "linear_regression"
  | "decision_tree"
  | "random_forest"
  | "xgboost"
  | "knn"
  | "naive_bayes"
  | "neural_network"
  | "svm"
  | "kmeans"
  | "pca";

export type AlgorithmRegistry = Partial<Record<AlgorithmId, AlgorithmConfig>>;
