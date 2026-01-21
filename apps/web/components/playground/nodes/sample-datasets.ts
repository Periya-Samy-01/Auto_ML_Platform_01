/**
 * Sample Datasets Catalog
 * 
 * Defines all available sample/toy datasets for the workflow playground.
 * Users can only use these datasets in workflows - they cannot upload, modify, or delete them.
 */

export interface ColumnInfo {
  name: string;
  type: "int" | "float" | "string" | "boolean" | "datetime";
  missingPercent: number;
}

export interface ProblemType {
  value: "classification" | "regression" | "clustering" | "time_series" | "nlp" | "image";
  label: string;
  autoDetected: boolean;
}

export interface SampleDataset {
  id: string;
  name: string;
  description: string;
  isSample: boolean;
  rows: number;
  columns: number;
  size: number; // bytes
  columnInfo: ColumnInfo[];
  defaultTarget: string;
  availableProblemTypes: ProblemType[];
  tags: string[];
}

// =============================================================================
// SAMPLE DATASETS CATALOG (14 datasets)
// =============================================================================

export const SAMPLE_DATASETS: SampleDataset[] = [
  // -------------------------------------------------------------------------
  // SKLEARN DATASETS (Small, loaded at runtime)
  // -------------------------------------------------------------------------
  {
    id: "iris",
    name: "Iris",
    description: "Classic iris flower classification with 3 species and 4 features.",
    isSample: true,
    rows: 150,
    columns: 5,
    size: 4608,
    columnInfo: [
      { name: "sepal length (cm)", type: "float", missingPercent: 0 },
      { name: "sepal width (cm)", type: "float", missingPercent: 0 },
      { name: "petal length (cm)", type: "float", missingPercent: 0 },
      { name: "petal width (cm)", type: "float", missingPercent: 0 },
      { name: "target", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["beginner", "multiclass"],
  },

  {
    id: "breast_cancer",
    name: "Breast Cancer Wisconsin",
    description: "Breast cancer diagnostic dataset with 30 features for binary classification.",
    isSample: true,
    rows: 569,
    columns: 31,
    size: 98000,
    columnInfo: [
      { name: "mean radius", type: "float", missingPercent: 0 },
      { name: "mean texture", type: "float", missingPercent: 0 },
      { name: "mean perimeter", type: "float", missingPercent: 0 },
      { name: "mean area", type: "float", missingPercent: 0 },
      { name: "mean smoothness", type: "float", missingPercent: 0 },
      { name: "target", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["healthcare", "binary"],
  },

  {
    id: "diabetes",
    name: "Diabetes Progression",
    description: "Diabetes disease progression prediction with 10 baseline variables.",
    isSample: true,
    rows: 442,
    columns: 11,
    size: 51200,
    columnInfo: [
      { name: "age", type: "float", missingPercent: 0 },
      { name: "sex", type: "float", missingPercent: 0 },
      { name: "bmi", type: "float", missingPercent: 0 },
      { name: "bp", type: "float", missingPercent: 0 },
      { name: "s1", type: "float", missingPercent: 0 },
      { name: "s2", type: "float", missingPercent: 0 },
      { name: "s3", type: "float", missingPercent: 0 },
      { name: "s4", type: "float", missingPercent: 0 },
      { name: "s5", type: "float", missingPercent: 0 },
      { name: "s6", type: "float", missingPercent: 0 },
      { name: "target", type: "float", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "regression", label: "Regression", autoDetected: true },
    ],
    tags: ["healthcare", "beginner"],
  },

  {
    id: "california_housing",
    name: "California Housing",
    description: "California housing prices based on census data with 8 features.",
    isSample: true,
    rows: 20640,
    columns: 9,
    size: 1500000,
    columnInfo: [
      { name: "MedInc", type: "float", missingPercent: 0 },
      { name: "HouseAge", type: "float", missingPercent: 0 },
      { name: "AveRooms", type: "float", missingPercent: 0 },
      { name: "AveBedrms", type: "float", missingPercent: 0 },
      { name: "Population", type: "float", missingPercent: 0 },
      { name: "AveOccup", type: "float", missingPercent: 0 },
      { name: "Latitude", type: "float", missingPercent: 0 },
      { name: "Longitude", type: "float", missingPercent: 0 },
      { name: "target", type: "float", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "regression", label: "Regression", autoDetected: true },
    ],
    tags: ["real-estate", "intermediate"],
  },

  {
    id: "wine",
    name: "Wine",
    description: "Wine recognition with 13 chemical analysis features for 3 cultivars.",
    isSample: true,
    rows: 178,
    columns: 14,
    size: 15000,
    columnInfo: [
      { name: "alcohol", type: "float", missingPercent: 0 },
      { name: "malic_acid", type: "float", missingPercent: 0 },
      { name: "ash", type: "float", missingPercent: 0 },
      { name: "alcalinity_of_ash", type: "float", missingPercent: 0 },
      { name: "magnesium", type: "float", missingPercent: 0 },
      { name: "target", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["multiclass", "beginner"],
  },

  {
    id: "digits",
    name: "Digits (Mini-MNIST)",
    description: "8x8 handwritten digit images (0-9) for image classification.",
    isSample: true,
    rows: 1797,
    columns: 65,
    size: 120000,
    columnInfo: [
      { name: "pixel_0", type: "float", missingPercent: 0 },
      { name: "target", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
      { value: "image", label: "Image Classification", autoDetected: false },
    ],
    tags: ["image", "multiclass", "intermediate"],
  },

  // -------------------------------------------------------------------------
  // CSV DATASETS (Loaded from files)
  // -------------------------------------------------------------------------
  {
    id: "titanic",
    name: "Titanic",
    description: "Titanic passenger survival prediction with demographic and ticket info.",
    isSample: true,
    rows: 891,
    columns: 12,
    size: 61440,
    columnInfo: [
      { name: "PassengerId", type: "int", missingPercent: 0 },
      { name: "Survived", type: "int", missingPercent: 0 },
      { name: "Pclass", type: "int", missingPercent: 0 },
      { name: "Name", type: "string", missingPercent: 0 },
      { name: "Sex", type: "string", missingPercent: 0 },
      { name: "Age", type: "float", missingPercent: 19.87 },
      { name: "SibSp", type: "int", missingPercent: 0 },
      { name: "Parch", type: "int", missingPercent: 0 },
      { name: "Ticket", type: "string", missingPercent: 0 },
      { name: "Fare", type: "float", missingPercent: 0 },
      { name: "Cabin", type: "string", missingPercent: 77.1 },
      { name: "Embarked", type: "string", missingPercent: 0.22 },
    ],
    defaultTarget: "Survived",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["binary", "missing-values", "beginner"],
  },

  {
    id: "boston_housing",
    name: "Boston Housing",
    description: "Boston house prices dataset with 13 features (deprecated in sklearn).",
    isSample: true,
    rows: 506,
    columns: 14,
    size: 51200,
    columnInfo: [
      { name: "CRIM", type: "float", missingPercent: 0 },
      { name: "ZN", type: "float", missingPercent: 0 },
      { name: "INDUS", type: "float", missingPercent: 0 },
      { name: "CHAS", type: "int", missingPercent: 0 },
      { name: "NOX", type: "float", missingPercent: 0 },
      { name: "RM", type: "float", missingPercent: 0 },
      { name: "AGE", type: "float", missingPercent: 0 },
      { name: "DIS", type: "float", missingPercent: 0 },
      { name: "RAD", type: "int", missingPercent: 0 },
      { name: "TAX", type: "float", missingPercent: 0 },
      { name: "PTRATIO", type: "float", missingPercent: 0 },
      { name: "B", type: "float", missingPercent: 0 },
      { name: "LSTAT", type: "float", missingPercent: 0 },
      { name: "MEDV", type: "float", missingPercent: 0 },
    ],
    defaultTarget: "MEDV",
    availableProblemTypes: [
      { value: "regression", label: "Regression", autoDetected: true },
    ],
    tags: ["real-estate", "beginner"],
  },

  {
    id: "air_passengers",
    name: "Air Passengers",
    description: "Monthly airline passenger numbers (1949-1960) for time series analysis.",
    isSample: true,
    rows: 144,
    columns: 3,
    size: 2048,
    columnInfo: [
      { name: "Month", type: "datetime", missingPercent: 0 },
      { name: "Year", type: "int", missingPercent: 0 },
      { name: "Passengers", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "Passengers",
    availableProblemTypes: [
      { value: "regression", label: "Regression", autoDetected: false },
      { value: "time_series", label: "Time Series", autoDetected: true },
    ],
    tags: ["time-series", "forecasting", "beginner"],
  },

  {
    id: "sms_spam",
    name: "SMS Spam Collection",
    description: "SMS messages labeled as spam or ham for text classification.",
    isSample: true,
    rows: 5572,
    columns: 2,
    size: 500000,
    columnInfo: [
      { name: "label", type: "string", missingPercent: 0 },
      { name: "message", type: "string", missingPercent: 0 },
    ],
    defaultTarget: "label",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
      { value: "nlp", label: "NLP", autoDetected: false },
    ],
    tags: ["nlp", "text", "binary", "intermediate"],
  },

  {
    id: "imdb_reviews",
    name: "IMDb Movie Reviews (Small)",
    description: "Movie reviews with sentiment labels - 1000 sample subset.",
    isSample: true,
    rows: 1000,
    columns: 2,
    size: 1200000,
    columnInfo: [
      { name: "review", type: "string", missingPercent: 0 },
      { name: "sentiment", type: "string", missingPercent: 0 },
    ],
    defaultTarget: "sentiment",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
      { value: "nlp", label: "NLP", autoDetected: false },
    ],
    tags: ["nlp", "sentiment", "text", "intermediate"],
  },

  {
    id: "credit_fraud",
    name: "Credit Card Fraud (Downsampled)",
    description: "Imbalanced fraud detection with anonymized transaction features.",
    isSample: true,
    rows: 10000,
    columns: 31,
    size: 4500000,
    columnInfo: [
      { name: "Time", type: "float", missingPercent: 0 },
      { name: "V1", type: "float", missingPercent: 0 },
      { name: "Amount", type: "float", missingPercent: 0 },
      { name: "Class", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "Class",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["imbalanced", "fraud", "advanced"],
  },

  {
    id: "synthetic_imbalanced",
    name: "Synthetic Imbalanced Classification",
    description: "Synthetic dataset with 95:5 class imbalance for testing imbalanced learning.",
    isSample: true,
    rows: 10000,
    columns: 21,
    size: 2000000,
    columnInfo: [
      { name: "feature_0", type: "float", missingPercent: 0 },
      { name: "target", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "target",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["imbalanced", "synthetic", "intermediate"],
  },

  {
    id: "transactions_categorical",
    name: "High-Cardinality Transactions",
    description: "Transaction data with high-cardinality categorical features for testing encoders.",
    isSample: true,
    rows: 10000,
    columns: 10,
    size: 1500000,
    columnInfo: [
      { name: "transaction_id", type: "string", missingPercent: 0 },
      { name: "merchant_id", type: "string", missingPercent: 0 },
      { name: "category", type: "string", missingPercent: 0 },
      { name: "city", type: "string", missingPercent: 0 },
      { name: "state", type: "string", missingPercent: 0 },
      { name: "amount", type: "float", missingPercent: 0 },
      { name: "hour", type: "int", missingPercent: 0 },
      { name: "day_of_week", type: "int", missingPercent: 0 },
      { name: "is_weekend", type: "int", missingPercent: 0 },
      { name: "is_fraud", type: "int", missingPercent: 0 },
    ],
    defaultTarget: "is_fraud",
    availableProblemTypes: [
      { value: "classification", label: "Classification", autoDetected: true },
    ],
    tags: ["categorical", "high-cardinality", "fraud", "advanced"],
  },
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

export function formatRowCount(count: number): string {
  if (count < 1000) return `${count}`;
  if (count < 1000000) return `${(count / 1000).toFixed(1)}K`;
  return `${(count / 1000000).toFixed(1)}M`;
}

/**
 * Get sample dataset by ID
 */
export function getSampleDatasetById(id: string): SampleDataset | undefined {
  return SAMPLE_DATASETS.find((d) => d.id === id);
}

/**
 * Filter sample datasets by problem type
 */
export function filterByProblemType(problemType: string): SampleDataset[] {
  return SAMPLE_DATASETS.filter((d) =>
    d.availableProblemTypes.some((pt) => pt.value === problemType)
  );
}

/**
 * Search sample datasets by name or description
 */
export function searchSampleDatasets(query: string): SampleDataset[] {
  const lowerQuery = query.toLowerCase();
  return SAMPLE_DATASETS.filter(
    (d) =>
      d.name.toLowerCase().includes(lowerQuery) ||
      d.description.toLowerCase().includes(lowerQuery) ||
      d.tags.some((t) => t.toLowerCase().includes(lowerQuery))
  );
}
