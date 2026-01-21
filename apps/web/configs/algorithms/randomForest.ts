import type { AlgorithmConfig } from "./types";

/**
 * Random Forest Algorithm Configuration
 *
 * Ensemble of decision trees with bootstrap aggregating.
 * Works for both classification and regression tasks.
 */

export const randomForestConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "random_forest",
    name: "Random Forest",
    shortName: "RF",
    description:
      "An ensemble learning method that combines multiple decision trees trained on random subsets of data and features.",
    icon: "🌲",
    category: "ensemble",
    bestFor: [
      "Tabular data with mixed feature types",
      "When you need feature importance",
      "Reducing overfitting compared to single decision tree",
      "Handling non-linear relationships",
      "Both classification and regression tasks",
    ],
    limitations: [
      "Can be slow for real-time predictions with many trees",
      "Less interpretable than single decision tree",
      "May overfit on very noisy datasets",
      "Requires more memory than simpler models",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees",
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
    supportsWarmStart: true,
  },

  // ==========================================================================
  // MODEL CONFIGURATION
  // ==========================================================================
  model: {
    hyperparameters: [
      // --- Main Parameters ---
      {
        key: "n_estimators",
        type: "slider",
        label: "Number of Trees",
        description: "The number of trees in the forest",
        tooltip: "More trees generally improve performance but increase training time.",
        min: 10,
        max: 500,
        step: 10,
        default: 100,
      },
      {
        key: "max_depth",
        type: "number",
        label: "Max Depth",
        description: "Maximum depth of each tree (empty for unlimited)",
        tooltip: "Limiting depth prevents overfitting. Leave empty for no limit.",
        min: 1,
        max: 50,
        default: 10,
        placeholder: "No limit",
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

      // --- Advanced Parameters ---
      {
        key: "min_samples_split",
        type: "number",
        label: "Min Samples Split",
        description: "Minimum samples required to split a node",
        tooltip: "Higher values prevent overfitting.",
        min: 2,
        max: 20,
        default: 2,
        advanced: true,
      },
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
        tooltip: "sqrt is good for classification, log2 for regression.",
        options: [
          { value: "sqrt", label: "Square Root" },
          { value: "log2", label: "Log2" },
          { value: "auto", label: "All Features" },
        ],
        default: "sqrt",
        advanced: true,
      },
      {
        key: "bootstrap",
        type: "switch",
        label: "Bootstrap Samples",
        description: "Whether to use bootstrap samples when building trees",
        tooltip: "Bootstrap sampling introduces diversity among trees.",
        default: true,
        advanced: true,
      },
      {
        key: "class_weight",
        type: "radio",
        label: "Class Weight",
        description: "How to handle class imbalance",
        tooltip: "Balanced auto-adjusts weights inversely proportional to class frequencies.",
        options: [
          { value: "none", label: "None", description: "Equal weight for all classes" },
          { value: "balanced", label: "Balanced", description: "Auto-adjust for imbalance" },
        ],
        default: "none",
        advanced: true,
      },
      {
        key: "random_state",
        type: "number",
        label: "Random Seed",
        description: "Seed for reproducibility",
        tooltip: "Set a value for reproducible results.",
        min: 0,
        max: 9999,
        default: 42,
        advanced: true,
      },
    ],

    validation: {
      fields: [
        {
          field: "n_estimators",
          rules: [
            { type: "required", message: "Number of trees is required" },
            { type: "min", value: 10, message: "Must have at least 10 trees" },
            { type: "max", value: 500, message: "Maximum 500 trees" },
          ],
        },
        {
          field: "max_depth",
          rules: [
            { type: "min", value: 1, message: "Max depth must be at least 1" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        n_estimators: { type: "int", low: 50, high: 300, step: 50 },
        max_depth: { type: "int", low: 3, high: 20 },
        min_samples_split: { type: "int", low: 2, high: 10 },
        min_samples_leaf: { type: "int", low: 1, high: 5 },
        max_features: { type: "categorical", choices: ["sqrt", "log2", "auto"] },
        bootstrap: { type: "categorical", choices: [true, false] },
      },
      nTrials: 50,
      timeout: 600,
      pruner: "median",
    },

    costs: {
      base: 3,
      perSample: 0.0005,
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
      "balanced_accuracy",
      // Regression metrics (when used for regression)
      "mse",
      "rmse",
      "mae",
      "r2",
    ],
    defaultMetrics: ["accuracy", "f1", "roc_auc"],
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
        formula: "Area under ROC curve",
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
      balanced_accuracy: {
        key: "balanced_accuracy",
        name: "Balanced Accuracy",
        formula: "(Sensitivity + Specificity) / 2",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Average recall for each class.",
        category: "classification",
      },
      mse: {
        key: "mse",
        name: "Mean Squared Error",
        formula: "mean((y - ŷ)²)",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Average squared difference between predictions and actual values.",
        category: "regression",
      },
      rmse: {
        key: "rmse",
        name: "Root Mean Squared Error",
        formula: "sqrt(MSE)",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Square root of MSE, in same units as target.",
        category: "regression",
      },
      mae: {
        key: "mae",
        name: "Mean Absolute Error",
        formula: "mean(|y - ŷ|)",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Average absolute difference between predictions and actual values.",
        category: "regression",
      },
      r2: {
        key: "r2",
        name: "R² Score",
        formula: "1 - SS_res/SS_tot",
        range: "unbounded",
        higherIsBetter: true,
        tooltip: "Proportion of variance explained by the model.",
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
      "feature_importance",
      "learning_curve",
      "shap_summary",
      "partial_dependence",
      // Regression
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
        requirements: { requiresProbabilities: true },
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
        requirements: { minSamples: 100 },
        cost: 5,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Feature importance with direction of impact",
        cost: 10,
      },
      partial_dependence: {
        key: "partial_dependence",
        name: "Partial Dependence",
        description: "Effect of features on predictions",
        cost: 10,
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
        description: "Scatter plot of predictions vs actual values",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Not applicable for tree-based models",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "How well-calibrated are the probabilities",
        cost: 2,
      },
      shap_waterfall: {
        key: "shap_waterfall",
        name: "SHAP Waterfall",
        description: "Explain individual predictions",
        cost: 5,
      },
    },
  },
};

export default randomForestConfig;
