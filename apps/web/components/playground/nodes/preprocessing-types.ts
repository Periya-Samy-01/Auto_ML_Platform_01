/**
 * Preprocessing Operation Types and Constants
 */

export const OPERATION_TYPES = {
  FILL_MISSING: "fill_missing",
  SCALE_STANDARD: "scale_standard",
  SCALE_MINMAX: "scale_minmax",
  SCALE_ROBUST: "scale_robust",
  ENCODE_ONEHOT: "encode_onehot",
  ENCODE_LABEL: "encode_label",
  REMOVE_DUPLICATES: "remove_duplicates",
  REMOVE_OUTLIERS_IQR: "remove_outliers_iqr",
  REMOVE_OUTLIERS_ZSCORE: "remove_outliers_zscore",
  DROP_COLUMNS: "drop_columns",
} as const;

export type OperationType = (typeof OPERATION_TYPES)[keyof typeof OPERATION_TYPES];

export const OPERATION_NAMES: Record<OperationType, string> = {
  [OPERATION_TYPES.FILL_MISSING]: "Fill Missing Values",
  [OPERATION_TYPES.SCALE_STANDARD]: "Standard Scaler",
  [OPERATION_TYPES.SCALE_MINMAX]: "MinMax Scaler",
  [OPERATION_TYPES.SCALE_ROBUST]: "Robust Scaler",
  [OPERATION_TYPES.ENCODE_ONEHOT]: "One-Hot Encode",
  [OPERATION_TYPES.ENCODE_LABEL]: "Label Encode",
  [OPERATION_TYPES.REMOVE_DUPLICATES]: "Remove Duplicates",
  [OPERATION_TYPES.REMOVE_OUTLIERS_IQR]: "Remove Outliers (IQR)",
  [OPERATION_TYPES.REMOVE_OUTLIERS_ZSCORE]: "Remove Outliers (Z-score)",
  [OPERATION_TYPES.DROP_COLUMNS]: "Drop Columns",
};

export const OPERATION_SHORT_NAMES: Record<OperationType, string> = {
  [OPERATION_TYPES.FILL_MISSING]: "Fill",
  [OPERATION_TYPES.SCALE_STANDARD]: "Scale",
  [OPERATION_TYPES.SCALE_MINMAX]: "Scale",
  [OPERATION_TYPES.SCALE_ROBUST]: "Scale",
  [OPERATION_TYPES.ENCODE_ONEHOT]: "Encode",
  [OPERATION_TYPES.ENCODE_LABEL]: "Encode",
  [OPERATION_TYPES.REMOVE_DUPLICATES]: "Dedup",
  [OPERATION_TYPES.REMOVE_OUTLIERS_IQR]: "Outliers",
  [OPERATION_TYPES.REMOVE_OUTLIERS_ZSCORE]: "Outliers",
  [OPERATION_TYPES.DROP_COLUMNS]: "Drop",
};

export const OPERATION_CATEGORIES: Record<string, { icon: string; operations: OperationType[] }> = {
  "Missing Values": {
    icon: "📊",
    operations: [OPERATION_TYPES.FILL_MISSING],
  },
  "Scaling": {
    icon: "🔢",
    operations: [
      OPERATION_TYPES.SCALE_STANDARD,
      OPERATION_TYPES.SCALE_MINMAX,
      OPERATION_TYPES.SCALE_ROBUST,
    ],
  },
  "Encoding": {
    icon: "🏷️",
    operations: [OPERATION_TYPES.ENCODE_ONEHOT, OPERATION_TYPES.ENCODE_LABEL],
  },
  "Cleaning": {
    icon: "🧹",
    operations: [
      OPERATION_TYPES.REMOVE_DUPLICATES,
      OPERATION_TYPES.REMOVE_OUTLIERS_IQR,
      OPERATION_TYPES.REMOVE_OUTLIERS_ZSCORE,
    ],
  },
  "Feature Selection": {
    icon: "🎯",
    operations: [OPERATION_TYPES.DROP_COLUMNS],
  },
};

// Operation configuration types
export interface FillMissingConfig {
  strategy: "mean" | "median" | "mode" | "constant";
  constantValue?: string | number;
  columns: "all_numeric" | "all_categorical" | string[];
}

export interface ScaleConfig {
  columns: "all_numeric" | string[];
  withMean?: boolean;
  withStd?: boolean;
}

export interface EncodeConfig {
  columns: "all_categorical" | string[];
  dropFirst?: boolean;
  handleUnknown?: "error" | "ignore";
}

export interface RemoveDuplicatesConfig {
  columns: "all" | string[];
  keep: "first" | "last";
}

export interface RemoveOutliersConfig {
  columns: "all_numeric" | string[];
  method: "iqr" | "zscore";
  threshold: number; // IQR multiplier (1.5) or z-score threshold (3)
  action: "remove" | "clip";
}

export interface DropColumnsConfig {
  columns: string[];
}

export type OperationConfig =
  | FillMissingConfig
  | ScaleConfig
  | EncodeConfig
  | RemoveDuplicatesConfig
  | RemoveOutliersConfig
  | DropColumnsConfig;

export interface OperationWarning {
  type: "error" | "warning" | "tip";
  message: string;
}

export interface Operation {
  id: string;
  type: OperationType;
  name: string;
  order: number;
  expanded: boolean;
  config: OperationConfig;
  affectedColumns: string[];
  warnings: OperationWarning[];
}

// Default configurations for each operation type
export const DEFAULT_CONFIGS: Record<OperationType, OperationConfig> = {
  [OPERATION_TYPES.FILL_MISSING]: {
    strategy: "mean",
    columns: "all_numeric",
  } as FillMissingConfig,
  [OPERATION_TYPES.SCALE_STANDARD]: {
    columns: "all_numeric",
    withMean: true,
    withStd: true,
  } as ScaleConfig,
  [OPERATION_TYPES.SCALE_MINMAX]: {
    columns: "all_numeric",
  } as ScaleConfig,
  [OPERATION_TYPES.SCALE_ROBUST]: {
    columns: "all_numeric",
  } as ScaleConfig,
  [OPERATION_TYPES.ENCODE_ONEHOT]: {
    columns: "all_categorical",
    dropFirst: true,
    handleUnknown: "error",
  } as EncodeConfig,
  [OPERATION_TYPES.ENCODE_LABEL]: {
    columns: "all_categorical",
  } as EncodeConfig,
  [OPERATION_TYPES.REMOVE_DUPLICATES]: {
    columns: "all",
    keep: "first",
  } as RemoveDuplicatesConfig,
  [OPERATION_TYPES.REMOVE_OUTLIERS_IQR]: {
    columns: "all_numeric",
    method: "iqr",
    threshold: 1.5,
    action: "remove",
  } as RemoveOutliersConfig,
  [OPERATION_TYPES.REMOVE_OUTLIERS_ZSCORE]: {
    columns: "all_numeric",
    method: "zscore",
    threshold: 3,
    action: "remove",
  } as RemoveOutliersConfig,
  [OPERATION_TYPES.DROP_COLUMNS]: {
    columns: [],
  } as DropColumnsConfig,
};

// Helper to generate unique IDs
export const generateOperationId = () => `op-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

// Helper to create a new operation
export const createOperation = (type: OperationType, order: number): Operation => ({
  id: generateOperationId(),
  type,
  name: OPERATION_NAMES[type],
  order,
  expanded: true,
  config: { ...DEFAULT_CONFIGS[type] },
  affectedColumns: [],
  warnings: [],
});
