import type { AlgorithmConfig } from "./types";

/**
 * Decision Tree Algorithm Configuration
 *
 * Simple, interpretable tree-based model for classification and regression.
 */

export const decisionTreeConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "decision_tree",
    name: "Decision Tree",
    shortName: "DT",
    description:
      "A tree-structured model that makes decisions by splitting data based on feature values. Highly interpretable.",
    icon: "🌳",
    category: "tree",
    bestFor: [
      "When interpretability is critical",
      "Understanding feature interactions",
      "Quick baseline models",
      "Visualizing decision rules",
      "Small to medium datasets",
    ],
    limitations: [
      "Prone to overfitting without pruning",
      "Unstable - small data changes can change tree structure",
      "Can create biased trees with imbalanced classes",
      "May not capture complex relationships well",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/tree.html",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["classification", "regression"],
    supportsMulticlass: true,
    supportsProbabilities: true,
    supportsFeatureImportance: true,
    supportsExplainability: true,
    handlesImbalanced: true,
    handlesMissingValues: false,
    requiresScaling: false,
    supportsWarmStart: false,
  },

  // ==========================================================================
  // MODEL CONFIGURATION
  // ==========================================================================
  model: {
    hyperparameters: [
      // --- Main Parameters ---
      {
        key: "max_depth",
        type: "slider",
        label: "Max Depth",
        description: "Maximum depth of the tree",
        tooltip: "Controls tree complexity. Lower values prevent overfitting.",
        min: 1,
        max: 30,
        step: 1,
        default: 5,
      },
      {
        key: "criterion",
        type: "select",
        label: "Split Criterion",
        description: "Function to measure the quality of a split",
        tooltip: "Gini is faster, Entropy can give slightly better results.",
        options: [
          { value: "gini", label: "Gini Impurity" },
          { value: "entropy", label: "Entropy" },
        ],
        default: "gini",
      },
      {
        key: "min_samples_split",
        type: "slider",
        label: "Min Samples Split",
        description: "Minimum samples required to split a node",
        tooltip: "Higher values prevent overfitting.",
        min: 2,
        max: 50,
        step: 1,
        default: 2,
      },

      // --- Advanced Parameters ---
      {
        key: "min_samples_leaf",
        type: "number",
        label: "Min Samples Leaf",
        description: "Minimum samples required at a leaf node",
        tooltip: "Higher values create smoother models.",
        min: 1,
        max: 20,
        default: 1,
        advanced: true,
      },
      {
        key: "max_features",
        type: "select",
        label: "Max Features",
        description: "Number of features to consider for best split",
        tooltip: "Limiting features adds randomness.",
        options: [
          { value: "auto", label: "All Features" },
          { value: "sqrt", label: "Square Root" },
          { value: "log2", label: "Log2" },
        ],
        default: "auto",
        advanced: true,
      },
      {
        key: "max_leaf_nodes",
        type: "number",
        label: "Max Leaf Nodes",
        description: "Maximum number of leaf nodes (empty for unlimited)",
        tooltip: "Limits tree size for interpretability.",
        min: 2,
        max: 100,
        default: 20,
        placeholder: "No limit",
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
          field: "max_depth",
          rules: [
            { type: "required", message: "Max depth is required" },
            { type: "min", value: 1, message: "Must be at least 1" },
          ],
        },
        {
          field: "min_samples_split",
          rules: [
            { type: "min", value: 2, message: "Must be at least 2" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        max_depth: { type: "int", low: 2, high: 20 },
        min_samples_split: { type: "int", low: 2, high: 20 },
        min_samples_leaf: { type: "int", low: 1, high: 10 },
        criterion: { type: "categorical", choices: ["gini", "entropy"] },
        max_features: { type: "categorical", choices: ["auto", "sqrt", "log2"] },
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
      "feature_importance",
      "learning_curve",
      "residual_plot",
      "prediction_vs_actual",
    ],
    defaultPlots: ["confusion_matrix", "feature_importance"],
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
        cost: 1,
      },
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Shows relative importance of each feature",
        requirements: { requiresFeatureImportance: true },
        cost: 1,
      },
      learning_curve: {
        key: "learning_curve",
        name: "Learning Curve",
        description: "Model performance vs training size",
        cost: 3,
      },
      residual_plot: {
        key: "residual_plot",
        name: "Residual Plot",
        description: "Residuals vs predicted values",
        cost: 1,
      },
      prediction_vs_actual: {
        key: "prediction_vs_actual",
        name: "Prediction vs Actual",
        description: "Scatter plot of predictions vs actual",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Not applicable for tree models",
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
        cost: 8,
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

export default decisionTreeConfig;
