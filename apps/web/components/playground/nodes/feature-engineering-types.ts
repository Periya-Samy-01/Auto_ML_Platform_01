/**
 * Feature Engineering Operation Types and Constants
 */

export const FEATURE_OPERATION_TYPES = {
  LOG_TRANSFORM: "log_transform",
  POWER_TRANSFORM: "power_transform",
  EXPONENTIAL_TRANSFORM: "exponential_transform",
  RECIPROCAL_TRANSFORM: "reciprocal_transform",
  POLYNOMIAL: "polynomial",
  INTERACTION: "interaction",
  RATIO: "ratio",
  DIFFERENCE: "difference",
  SUM: "sum",
  BINNING_WIDTH: "binning_width",
  BINNING_FREQUENCY: "binning_frequency",
  BINNING_QUANTILE: "binning_quantile",
} as const;

export type FeatureOperationType =
  (typeof FEATURE_OPERATION_TYPES)[keyof typeof FEATURE_OPERATION_TYPES];

export const FEATURE_OPERATION_NAMES: Record<FeatureOperationType, string> = {
  [FEATURE_OPERATION_TYPES.LOG_TRANSFORM]: "Log Transform",
  [FEATURE_OPERATION_TYPES.POWER_TRANSFORM]: "Power Transform",
  [FEATURE_OPERATION_TYPES.EXPONENTIAL_TRANSFORM]: "Exponential Transform",
  [FEATURE_OPERATION_TYPES.RECIPROCAL_TRANSFORM]: "Reciprocal Transform",
  [FEATURE_OPERATION_TYPES.POLYNOMIAL]: "Polynomial Features",
  [FEATURE_OPERATION_TYPES.INTERACTION]: "Interaction Features",
  [FEATURE_OPERATION_TYPES.RATIO]: "Ratio Features",
  [FEATURE_OPERATION_TYPES.DIFFERENCE]: "Difference Features",
  [FEATURE_OPERATION_TYPES.SUM]: "Sum Features",
  [FEATURE_OPERATION_TYPES.BINNING_WIDTH]: "Equal Width Binning",
  [FEATURE_OPERATION_TYPES.BINNING_FREQUENCY]: "Equal Frequency Binning",
  [FEATURE_OPERATION_TYPES.BINNING_QUANTILE]: "Quantile Binning",
};

export const FEATURE_OPERATION_SHORT_NAMES: Record<FeatureOperationType, string> = {
  [FEATURE_OPERATION_TYPES.LOG_TRANSFORM]: "Log",
  [FEATURE_OPERATION_TYPES.POWER_TRANSFORM]: "Power",
  [FEATURE_OPERATION_TYPES.EXPONENTIAL_TRANSFORM]: "Exp",
  [FEATURE_OPERATION_TYPES.RECIPROCAL_TRANSFORM]: "Recip",
  [FEATURE_OPERATION_TYPES.POLYNOMIAL]: "Poly",
  [FEATURE_OPERATION_TYPES.INTERACTION]: "Interact",
  [FEATURE_OPERATION_TYPES.RATIO]: "Ratio",
  [FEATURE_OPERATION_TYPES.DIFFERENCE]: "Diff",
  [FEATURE_OPERATION_TYPES.SUM]: "Sum",
  [FEATURE_OPERATION_TYPES.BINNING_WIDTH]: "Bin",
  [FEATURE_OPERATION_TYPES.BINNING_FREQUENCY]: "Bin",
  [FEATURE_OPERATION_TYPES.BINNING_QUANTILE]: "Bin",
};

export const FEATURE_OPERATION_CATEGORIES: Record<
  string,
  { icon: string; operations: FeatureOperationType[] }
> = {
  "Mathematical Transforms": {
    icon: "📊",
    operations: [
      FEATURE_OPERATION_TYPES.LOG_TRANSFORM,
      FEATURE_OPERATION_TYPES.POWER_TRANSFORM,
      FEATURE_OPERATION_TYPES.EXPONENTIAL_TRANSFORM,
      FEATURE_OPERATION_TYPES.RECIPROCAL_TRANSFORM,
    ],
  },
  "Polynomial & Interactions": {
    icon: "🔢",
    operations: [
      FEATURE_OPERATION_TYPES.POLYNOMIAL,
      FEATURE_OPERATION_TYPES.INTERACTION,
      FEATURE_OPERATION_TYPES.RATIO,
      FEATURE_OPERATION_TYPES.DIFFERENCE,
      FEATURE_OPERATION_TYPES.SUM,
    ],
  },
  Binning: {
    icon: "📦",
    operations: [
      FEATURE_OPERATION_TYPES.BINNING_WIDTH,
      FEATURE_OPERATION_TYPES.BINNING_FREQUENCY,
      FEATURE_OPERATION_TYPES.BINNING_QUANTILE,
    ],
  },
};

// Operation configuration types
export interface LogTransformConfig {
  logType: "natural" | "log10" | "log2" | "log1p";
  columns: string[];
  handleNegative: "skip" | "absolute" | "error";
  suffix: string;
}

export interface PowerTransformConfig {
  power: "square" | "cube" | "sqrt" | "custom";
  customPower?: number;
  columns: string[];
  handleNegative: "skip" | "absolute" | "error";
}

export interface ExponentialTransformConfig {
  columns: string[];
  handleLarge: "clip" | "allow" | "error";
  suffix: string;
}

export interface ReciprocalTransformConfig {
  columns: string[];
  handleZero: "nan" | "skip" | "error";
  addConstant: number;
}

export interface PolynomialConfig {
  degree: 2 | 3;
  columns: string[];
  includeX2: boolean;
  includeX3: boolean;
  includeBias: boolean;
  namingPattern: "pow" | "superscript" | "custom";
}

export interface InteractionConfig {
  columns: string[];
  degree: 2 | 3; // pairwise or triplets
  namingPattern: "x" | "underscore" | "custom";
  includePolynomial: boolean;
}

export interface RatioConfig {
  ratios: Array<{ numerator: string; denominator: string }>;
  handleZero: "nan" | "skip" | "error";
  namingPattern: "div" | "slash" | "custom";
}

export interface DifferenceConfig {
  differences: Array<{ col1: string; col2: string }>;
  namingPattern: "minus" | "dash" | "custom";
  includeAbsolute: boolean;
}

export interface SumConfig {
  columns: string[];
  featureName: string;
  includeAverage: boolean;
}

export interface BinningWidthConfig {
  column: string | null;
  bins: number;
  labels: "auto" | "custom";
  customLabels?: string[];
  encoding: "ordinal" | "onehot";
  keepOriginal: boolean;
}

export interface BinningFrequencyConfig {
  column: string | null;
  bins: number;
  labels: "auto" | "custom";
  customLabels?: string[];
  encoding: "ordinal" | "onehot";
  keepOriginal: boolean;
}

export interface BinningQuantileConfig {
  column: string | null;
  quantiles: number[];
  labels: "auto" | "custom";
  customLabels?: string[];
  encoding: "ordinal" | "onehot";
}

export type FeatureOperationConfig =
  | LogTransformConfig
  | PowerTransformConfig
  | ExponentialTransformConfig
  | ReciprocalTransformConfig
  | PolynomialConfig
  | InteractionConfig
  | RatioConfig
  | DifferenceConfig
  | SumConfig
  | BinningWidthConfig
  | BinningFrequencyConfig
  | BinningQuantileConfig;

export interface FeatureOperationWarning {
  type: "error" | "warning" | "tip";
  message: string;
}

export interface FeatureOperation {
  id: string;
  type: FeatureOperationType;
  name: string;
  order: number;
  expanded: boolean;
  config: FeatureOperationConfig;
  newFeatures: string[];
  warnings: FeatureOperationWarning[];
}

// Default configurations for each operation type
export const FEATURE_DEFAULT_CONFIGS: Record<FeatureOperationType, FeatureOperationConfig> = {
  [FEATURE_OPERATION_TYPES.LOG_TRANSFORM]: {
    logType: "natural",
    columns: [],
    handleNegative: "skip",
    suffix: "_log",
  } as LogTransformConfig,
  [FEATURE_OPERATION_TYPES.POWER_TRANSFORM]: {
    power: "square",
    columns: [],
    handleNegative: "skip",
  } as PowerTransformConfig,
  [FEATURE_OPERATION_TYPES.EXPONENTIAL_TRANSFORM]: {
    columns: [],
    handleLarge: "clip",
    suffix: "_exp",
  } as ExponentialTransformConfig,
  [FEATURE_OPERATION_TYPES.RECIPROCAL_TRANSFORM]: {
    columns: [],
    handleZero: "nan",
    addConstant: 0,
  } as ReciprocalTransformConfig,
  [FEATURE_OPERATION_TYPES.POLYNOMIAL]: {
    degree: 2,
    columns: [],
    includeX2: true,
    includeX3: false,
    includeBias: false,
    namingPattern: "pow",
  } as PolynomialConfig,
  [FEATURE_OPERATION_TYPES.INTERACTION]: {
    columns: [],
    degree: 2,
    namingPattern: "x",
    includePolynomial: false,
  } as InteractionConfig,
  [FEATURE_OPERATION_TYPES.RATIO]: {
    ratios: [],
    handleZero: "nan",
    namingPattern: "div",
  } as RatioConfig,
  [FEATURE_OPERATION_TYPES.DIFFERENCE]: {
    differences: [],
    namingPattern: "minus",
    includeAbsolute: false,
  } as DifferenceConfig,
  [FEATURE_OPERATION_TYPES.SUM]: {
    columns: [],
    featureName: "sum_selected",
    includeAverage: false,
  } as SumConfig,
  [FEATURE_OPERATION_TYPES.BINNING_WIDTH]: {
    column: null,
    bins: 5,
    labels: "auto",
    encoding: "ordinal",
    keepOriginal: true,
  } as BinningWidthConfig,
  [FEATURE_OPERATION_TYPES.BINNING_FREQUENCY]: {
    column: null,
    bins: 4,
    labels: "auto",
    encoding: "ordinal",
    keepOriginal: true,
  } as BinningFrequencyConfig,
  [FEATURE_OPERATION_TYPES.BINNING_QUANTILE]: {
    column: null,
    quantiles: [0.25, 0.5, 0.75],
    labels: "auto",
    encoding: "ordinal",
  } as BinningQuantileConfig,
};

// Helper to generate unique IDs
export const generateFeatureOperationId = () =>
  `fe-op-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

// Helper to create a new operation
export const createFeatureOperation = (
  type: FeatureOperationType,
  order: number
): FeatureOperation => ({
  id: generateFeatureOperationId(),
  type,
  name: FEATURE_OPERATION_NAMES[type],
  order,
  expanded: true,
  config: { ...FEATURE_DEFAULT_CONFIGS[type] },
  newFeatures: [],
  warnings: [],
});
