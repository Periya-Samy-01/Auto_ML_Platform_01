import type { AlgorithmConfig } from "./types";

/**
 * K-Nearest Neighbors Algorithm Configuration
 *
 * Instance-based learning using nearest neighbors.
 */

export const knnConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "knn",
    name: "K-Nearest Neighbors",
    shortName: "KNN",
    description:
      "A non-parametric algorithm that makes predictions based on the k closest training examples in the feature space.",
    icon: "🎯",
    category: "tree", // Using 'tree' as closest category, could be 'distance'
    bestFor: [
      "Small to medium datasets",
      "When decision boundary is irregular",
      "Multi-class classification",
      "Recommendation systems",
      "Pattern recognition",
    ],
    limitations: [
      "Slow prediction for large datasets (lazy learning)",
      "Sensitive to feature scaling",
      "Curse of dimensionality with many features",
      "Memory intensive - stores all training data",
      "Sensitive to noisy data and outliers",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/neighbors.html",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["classification", "regression"],
    supportsMulticlass: true,
    supportsProbabilities: true,
    supportsFeatureImportance: false,
    supportsExplainability: false,
    handlesImbalanced: false,
    handlesMissingValues: false,
    requiresScaling: true,
    supportsWarmStart: false,
  },

  // ==========================================================================
  // MODEL CONFIGURATION
  // ==========================================================================
  model: {
    hyperparameters: [
      // --- Main Parameters ---
      {
        key: "n_neighbors",
        type: "slider",
        label: "Number of Neighbors (K)",
        description: "Number of neighbors to use for prediction",
        tooltip: "Odd numbers avoid ties in classification. Lower K = more complex boundary.",
        min: 1,
        max: 50,
        step: 1,
        default: 5,
      },
      {
        key: "weights",
        type: "radio",
        label: "Weight Function",
        description: "How to weight neighbor contributions",
        tooltip: "Distance weighting gives closer neighbors more influence.",
        options: [
          { value: "uniform", label: "Uniform", description: "All neighbors weighted equally" },
          { value: "distance", label: "Distance", description: "Closer neighbors have more weight" },
        ],
        default: "uniform",
      },
      {
        key: "metric",
        type: "select",
        label: "Distance Metric",
        description: "Distance metric for neighbor calculation",
        tooltip: "Euclidean is standard, Manhattan for grid-like data.",
        options: [
          { value: "minkowski", label: "Minkowski" },
          { value: "euclidean", label: "Euclidean" },
          { value: "manhattan", label: "Manhattan" },
          { value: "cosine", label: "Cosine" },
        ],
        default: "minkowski",
      },

      // --- Advanced Parameters ---
      {
        key: "p",
        type: "slider",
        label: "Minkowski Power (p)",
        description: "Power parameter for Minkowski metric",
        tooltip: "p=1 is Manhattan, p=2 is Euclidean.",
        min: 1,
        max: 5,
        step: 1,
        default: 2,
        dependsOn: { field: "metric", value: "minkowski" },
        advanced: true,
      },
      {
        key: "algorithm",
        type: "select",
        label: "Algorithm",
        description: "Algorithm for computing nearest neighbors",
        tooltip: "Auto picks the best based on data.",
        options: [
          { value: "auto", label: "Auto" },
          { value: "ball_tree", label: "Ball Tree" },
          { value: "kd_tree", label: "KD Tree" },
          { value: "brute", label: "Brute Force" },
        ],
        default: "auto",
        advanced: true,
      },
      {
        key: "leaf_size",
        type: "number",
        label: "Leaf Size",
        description: "Leaf size for tree-based algorithms",
        tooltip: "Affects speed and memory usage.",
        min: 10,
        max: 100,
        default: 30,
        advanced: true,
      },
    ],

    validation: {
      fields: [
        {
          field: "n_neighbors",
          rules: [
            { type: "required", message: "Number of neighbors is required" },
            { type: "min", value: 1, message: "Must have at least 1 neighbor" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        n_neighbors: { type: "int", low: 1, high: 30 },
        weights: { type: "categorical", choices: ["uniform", "distance"] },
        metric: { type: "categorical", choices: ["euclidean", "manhattan", "minkowski"] },
        p: { type: "int", low: 1, high: 5 },
      },
      nTrials: 50,
      timeout: 300,
      pruner: "median",
    },

    costs: {
      base: 1,
      perSample: 0.0001,
      crossValidation: { multiplier: 5 },
      optuna: { perTrial: 1, maxTrials: 100 },
    },
  },

  // ==========================================================================
  // EVALUATION CONFIGURATION
  // ==========================================================================
  evaluate: {
    supportedMetrics: [
      "accuracy",
      "precision",
      "recall",
      "f1",
      "confusion_matrix",
      "mse",
      "rmse",
      "mae",
      "r2",
    ],
    defaultMetrics: ["accuracy", "f1", "confusion_matrix"],
    metricDefinitions: {
      accuracy: {
        key: "accuracy",
        name: "Accuracy",
        formula: "(TP + TN) / Total",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Proportion of correct predictions.",
        category: "classification",
      },
      precision: {
        key: "precision",
        name: "Precision",
        formula: "TP / (TP + FP)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Of positive predictions, how many are correct.",
        category: "classification",
      },
      recall: {
        key: "recall",
        name: "Recall",
        formula: "TP / (TP + FN)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Of actual positives, how many were found.",
        category: "classification",
      },
      f1: {
        key: "f1",
        name: "F1 Score",
        formula: "2 * (P * R) / (P + R)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Harmonic mean of precision and recall.",
        category: "classification",
      },
      confusion_matrix: {
        key: "confusion_matrix",
        name: "Confusion Matrix",
        range: "unbounded",
        higherIsBetter: true,
        tooltip: "Matrix showing true vs predicted labels.",
        category: "classification",
      },
      mse: {
        key: "mse",
        name: "Mean Squared Error",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Average squared prediction error.",
        category: "regression",
      },
      rmse: {
        key: "rmse",
        name: "Root Mean Squared Error",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Square root of MSE.",
        category: "regression",
      },
      mae: {
        key: "mae",
        name: "Mean Absolute Error",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Average absolute prediction error.",
        category: "regression",
      },
      r2: {
        key: "r2",
        name: "R² Score",
        range: "unbounded",
        higherIsBetter: true,
        tooltip: "Proportion of variance explained.",
        category: "regression",
      },
    },
  },

  // ==========================================================================
  // VISUALIZATION CONFIGURATION
  // ==========================================================================
  visualize: {
    supportedPlots: [
      "confusion_matrix",
      "learning_curve",
      "prediction_vs_actual",
      "residual_plot",
    ],
    defaultPlots: ["confusion_matrix"],
    plotDefinitions: {
      confusion_matrix: {
        key: "confusion_matrix",
        name: "Confusion Matrix",
        description: "Shows true vs predicted labels",
        cost: 1,
      },
      learning_curve: {
        key: "learning_curve",
        name: "Learning Curve",
        description: "Model performance vs training size",
        cost: 5,
      },
      prediction_vs_actual: {
        key: "prediction_vs_actual",
        name: "Prediction vs Actual",
        description: "Scatter plot of predictions vs actual",
        cost: 1,
      },
      residual_plot: {
        key: "residual_plot",
        name: "Residual Plot",
        description: "Residuals vs predicted values",
        cost: 1,
      },
      // Placeholders for unsupported plots
      roc_curve: {
        key: "roc_curve",
        name: "ROC Curve",
        description: "ROC curve (requires probabilities)",
        cost: 1,
      },
      precision_recall_curve: {
        key: "precision_recall_curve",
        name: "Precision-Recall Curve",
        description: "Precision-recall trade-off",
        cost: 1,
      },
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Not available for KNN",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Not applicable for KNN",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "Probability calibration plot",
        cost: 2,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Not typically used for KNN",
        cost: 10,
      },
      shap_waterfall: {
        key: "shap_waterfall",
        name: "SHAP Waterfall",
        description: "Explain individual predictions",
        cost: 5,
      },
      partial_dependence: {
        key: "partial_dependence",
        name: "Partial Dependence",
        description: "Effect of features on predictions",
        cost: 8,
      },
    },
  },
};

export default knnConfig;
