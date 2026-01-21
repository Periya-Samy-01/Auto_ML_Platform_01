import type { AlgorithmConfig } from "./types";

/**
 * Support Vector Machine Algorithm Configuration
 *
 * Kernel-based model for classification and regression.
 */

export const svmConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "svm",
    name: "Support Vector Machine",
    shortName: "SVM",
    description:
      "A powerful algorithm that finds the optimal hyperplane to separate classes, with kernel tricks for non-linear boundaries.",
    icon: "🔷",
    category: "linear",
    bestFor: [
      "High-dimensional data (text classification)",
      "When margin of separation is clear",
      "Small to medium datasets",
      "Binary classification problems",
      "Image classification",
    ],
    limitations: [
      "Slow on large datasets (O(n²) to O(n³) complexity)",
      "Sensitive to feature scaling",
      "Difficult to interpret (especially with non-linear kernels)",
      "Requires careful kernel and parameter selection",
      "Memory intensive for large datasets",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/svm.html",
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
    handlesImbalanced: true,
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
        key: "kernel",
        type: "radio",
        label: "Kernel",
        description: "Kernel type for the algorithm",
        tooltip: "RBF is most common. Linear for linearly separable data.",
        options: [
          { value: "rbf", label: "RBF (Gaussian)", description: "Non-linear, most common" },
          { value: "linear", label: "Linear", description: "Fast, interpretable" },
          { value: "poly", label: "Polynomial", description: "Non-linear with degree control" },
          { value: "sigmoid", label: "Sigmoid", description: "Neural network-like" },
        ],
        default: "rbf",
      },
      {
        key: "C",
        type: "slider",
        label: "Regularization (C)",
        description: "Regularization parameter (smaller = more regularization)",
        tooltip: "Controls trade-off between smooth boundary and classifying points correctly.",
        min: 0.001,
        max: 100,
        step: 0.001,
        default: 1.0,
        displayFormat: (v: number) => v.toFixed(3),
      },
      {
        key: "gamma",
        type: "select",
        label: "Gamma",
        description: "Kernel coefficient for RBF, poly, and sigmoid",
        tooltip: "Scale uses 1/(n_features * X.var()), Auto uses 1/n_features.",
        options: [
          { value: "scale", label: "Scale (1 / (n_features * var))" },
          { value: "auto", label: "Auto (1 / n_features)" },
        ],
        default: "scale",
      },

      // --- Advanced Parameters ---
      {
        key: "degree",
        type: "slider",
        label: "Polynomial Degree",
        description: "Degree for polynomial kernel",
        tooltip: "Only used when kernel is Polynomial.",
        min: 1,
        max: 10,
        step: 1,
        default: 3,
        dependsOn: { field: "kernel", value: "poly" },
        advanced: true,
      },
      {
        key: "probability",
        type: "switch",
        label: "Probability Estimates",
        description: "Enable probability estimates",
        tooltip: "Slower training but enables predict_proba. Required for ROC curves.",
        default: true,
        advanced: true,
      },
      {
        key: "class_weight",
        type: "radio",
        label: "Class Weight",
        description: "How to handle class imbalance",
        options: [
          { value: "none", label: "None", description: "Equal weight" },
          { value: "balanced", label: "Balanced", description: "Auto-adjust" },
        ],
        default: "none",
        advanced: true,
      },
      {
        key: "max_iter",
        type: "number",
        label: "Max Iterations",
        description: "Hard limit on iterations (-1 = no limit)",
        tooltip: "Set a limit if training takes too long.",
        min: -1,
        max: 10000,
        default: -1,
        advanced: true,
      },
      {
        key: "random_state",
        type: "number",
        label: "Random Seed",
        description: "Seed for reproducibility",
        min: 0,
        max: 9999,
        default: 42,
        advanced: true,
      },
    ],

    validation: {
      fields: [
        {
          field: "C",
          rules: [
            { type: "required", message: "C is required" },
            { type: "min", value: 0.001, message: "C must be at least 0.001" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        kernel: { type: "categorical", choices: ["rbf", "linear", "poly"] },
        C: { type: "float", low: 0.01, high: 100, log: true },
        gamma: { type: "categorical", choices: ["scale", "auto"] },
        degree: { type: "int", low: 2, high: 5 },
      },
      nTrials: 50,
      timeout: 600,
      pruner: "median",
    },

    costs: {
      base: 3,
      perSample: 0.001,
      crossValidation: { multiplier: 5 },
      optuna: { perTrial: 3, maxTrials: 100 },
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
      "roc_auc",
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
      roc_auc: {
        key: "roc_auc",
        name: "ROC AUC",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Model's ability to distinguish between classes.",
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
      "roc_curve",
      "precision_recall_curve",
      "learning_curve",
      "prediction_vs_actual",
      "residual_plot",
    ],
    defaultPlots: ["confusion_matrix", "roc_curve"],
    plotDefinitions: {
      confusion_matrix: {
        key: "confusion_matrix",
        name: "Confusion Matrix",
        description: "Shows true vs predicted labels",
        cost: 1,
      },
      roc_curve: {
        key: "roc_curve",
        name: "ROC Curve",
        description: "Receiver Operating Characteristic curve",
        requirements: { requiresProbabilities: true },
        cost: 1,
      },
      precision_recall_curve: {
        key: "precision_recall_curve",
        name: "Precision-Recall Curve",
        description: "Trade-off between precision and recall",
        requirements: { requiresProbabilities: true },
        cost: 1,
      },
      learning_curve: {
        key: "learning_curve",
        name: "Learning Curve",
        description: "Model performance vs training size",
        cost: 8,
      },
      prediction_vs_actual: {
        key: "prediction_vs_actual",
        name: "Prediction vs Actual",
        description: "For regression tasks",
        cost: 1,
      },
      residual_plot: {
        key: "residual_plot",
        name: "Residual Plot",
        description: "Residuals vs predicted values",
        cost: 1,
      },
      // Placeholders
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Not available for SVM",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Only for linear kernel",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "Calibration of probability estimates",
        cost: 2,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Feature impact on predictions",
        cost: 15,
      },
      shap_waterfall: {
        key: "shap_waterfall",
        name: "SHAP Waterfall",
        description: "Explain individual predictions",
        cost: 8,
      },
      partial_dependence: {
        key: "partial_dependence",
        name: "Partial Dependence",
        description: "Effect of features on predictions",
        cost: 10,
      },
    },
  },
};

export default svmConfig;
