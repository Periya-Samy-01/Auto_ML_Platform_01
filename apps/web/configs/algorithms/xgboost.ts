import type { AlgorithmConfig } from "./types";

/**
 * XGBoost Algorithm Configuration
 *
 * Gradient boosting with regularization for high performance.
 */

export const xgboostConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "xgboost",
    name: "XGBoost",
    shortName: "XGB",
    description:
      "Extreme Gradient Boosting - a scalable, high-performance gradient boosting library with built-in regularization.",
    icon: "⚡",
    category: "ensemble",
    bestFor: [
      "Structured/tabular data competitions",
      "When you need state-of-the-art performance",
      "Large datasets with many features",
      "Both classification and regression",
      "Handling missing values automatically",
    ],
    limitations: [
      "Requires careful hyperparameter tuning",
      "Can overfit with too many boosting rounds",
      "Less interpretable than simpler models",
      "Memory intensive for very large datasets",
    ],
    learnMoreUrl: "https://xgboost.readthedocs.io/",
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
    handlesMissingValues: true,
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
        description: "Number of boosting rounds",
        tooltip: "More trees can improve performance but increase training time and risk overfitting.",
        min: 10,
        max: 1000,
        step: 10,
        default: 100,
      },
      {
        key: "max_depth",
        type: "slider",
        label: "Max Depth",
        description: "Maximum tree depth for base learners",
        tooltip: "Lower values prevent overfitting. 3-10 is typical.",
        min: 1,
        max: 20,
        step: 1,
        default: 6,
      },
      {
        key: "learning_rate",
        type: "slider",
        label: "Learning Rate",
        description: "Boosting learning rate (eta)",
        tooltip: "Lower values require more trees but can improve generalization.",
        min: 0.01,
        max: 1.0,
        step: 0.01,
        default: 0.1,
        displayFormat: (v: number) => v.toFixed(2),
      },

      // --- Advanced Parameters ---
      {
        key: "min_child_weight",
        type: "number",
        label: "Min Child Weight",
        description: "Minimum sum of instance weight in a child",
        tooltip: "Higher values prevent overfitting.",
        min: 1,
        max: 20,
        default: 1,
        advanced: true,
      },
      {
        key: "subsample",
        type: "slider",
        label: "Subsample Ratio",
        description: "Subsample ratio of training instances",
        tooltip: "Values < 1.0 add randomness to prevent overfitting.",
        min: 0.5,
        max: 1.0,
        step: 0.1,
        default: 1.0,
        advanced: true,
      },
      {
        key: "colsample_bytree",
        type: "slider",
        label: "Column Sample Ratio",
        description: "Subsample ratio of columns per tree",
        tooltip: "Feature subsampling adds diversity.",
        min: 0.5,
        max: 1.0,
        step: 0.1,
        default: 1.0,
        advanced: true,
      },
      {
        key: "reg_alpha",
        type: "slider",
        label: "L1 Regularization",
        description: "L1 regularization on weights",
        tooltip: "Higher values mean more regularization.",
        min: 0,
        max: 10,
        step: 0.1,
        default: 0,
        advanced: true,
      },
      {
        key: "reg_lambda",
        type: "slider",
        label: "L2 Regularization",
        description: "L2 regularization on weights",
        tooltip: "Higher values mean more regularization.",
        min: 0,
        max: 10,
        step: 0.1,
        default: 1,
        advanced: true,
      },
      {
        key: "scale_pos_weight",
        type: "number",
        label: "Scale Pos Weight",
        description: "Balance of positive and negative weights",
        tooltip: "Set to sum(negative)/sum(positive) for imbalanced data.",
        min: 0.1,
        max: 100,
        default: 1,
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
          field: "n_estimators",
          rules: [
            { type: "required", message: "Number of trees is required" },
            { type: "min", value: 10, message: "Must have at least 10 trees" },
          ],
        },
        {
          field: "learning_rate",
          rules: [
            { type: "required", message: "Learning rate is required" },
            { type: "min", value: 0.01, message: "Must be at least 0.01" },
            { type: "max", value: 1, message: "Must be at most 1.0" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        n_estimators: { type: "int", low: 50, high: 500, step: 50 },
        max_depth: { type: "int", low: 3, high: 12 },
        learning_rate: { type: "float", low: 0.01, high: 0.3, log: true },
        subsample: { type: "float", low: 0.6, high: 1.0 },
        colsample_bytree: { type: "float", low: 0.6, high: 1.0 },
        reg_alpha: { type: "float", low: 0, high: 10 },
        reg_lambda: { type: "float", low: 0, high: 10 },
      },
      nTrials: 100,
      timeout: 900,
      pruner: "hyperband",
    },

    costs: {
      base: 5,
      perSample: 0.001,
      crossValidation: { multiplier: 5 },
      optuna: { perTrial: 5, maxTrials: 100 },
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
      "log_loss",
      "confusion_matrix",
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
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Model's ability to distinguish between classes.",
        category: "classification",
      },
      log_loss: {
        key: "log_loss",
        name: "Log Loss",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Penalizes confident wrong predictions.",
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
      "feature_importance",
      "learning_curve",
      "shap_summary",
      "shap_waterfall",
      "partial_dependence",
      "residual_plot",
      "prediction_vs_actual",
    ],
    defaultPlots: ["confusion_matrix", "feature_importance", "roc_curve"],
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
        cost: 10,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Feature importance with direction of impact",
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
        cost: 12,
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
        description: "Not applicable for XGBoost",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "Calibration of probability estimates",
        cost: 2,
      },
    },
  },
};

export default xgboostConfig;
