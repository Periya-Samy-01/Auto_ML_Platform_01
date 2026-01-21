import type { AlgorithmConfig } from "./types";

/**
 * Neural Network (MLP) Algorithm Configuration
 *
 * Multi-layer Perceptron for classification and regression.
 */

export const neuralNetworkConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "neural_network",
    name: "Neural Network",
    shortName: "MLP",
    description:
      "A Multi-layer Perceptron (MLP) neural network that can learn complex non-linear patterns through multiple hidden layers.",
    icon: "🧠",
    category: "neural",
    bestFor: [
      "Complex non-linear patterns",
      "Large datasets with many features",
      "When other models underperform",
      "Pattern recognition tasks",
      "Both classification and regression",
    ],
    limitations: [
      "Requires careful hyperparameter tuning",
      "Can be slow to train",
      "Prone to overfitting without regularization",
      "Less interpretable than simpler models",
      "Sensitive to feature scaling",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/neural_networks_supervised.html",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["classification", "regression"],
    supportsMulticlass: true,
    supportsProbabilities: true,
    supportsFeatureImportance: false,
    supportsExplainability: true,
    handlesImbalanced: false,
    handlesMissingValues: false,
    requiresScaling: true,
    supportsWarmStart: true,
  },

  // ==========================================================================
  // MODEL CONFIGURATION
  // ==========================================================================
  model: {
    hyperparameters: [
      // --- Main Parameters ---
      {
        key: "hidden_layer_sizes",
        type: "select",
        label: "Hidden Layer Sizes",
        description: "Number and size of hidden layers",
        tooltip: "More/larger layers can learn more complex patterns but risk overfitting.",
        options: [
          { value: "(50,)", label: "Small (50)" },
          { value: "(100,)", label: "Medium (100)" },
          { value: "(100, 50)", label: "Two Layers (100, 50)" },
          { value: "(100, 100)", label: "Two Layers (100, 100)" },
          { value: "(128, 64, 32)", label: "Three Layers (128, 64, 32)" },
          { value: "(256, 128, 64)", label: "Large (256, 128, 64)" },
        ],
        default: "(100,)",
      },
      {
        key: "activation",
        type: "radio",
        label: "Activation Function",
        description: "Activation function for hidden layers",
        tooltip: "ReLU is most common and usually works best.",
        options: [
          { value: "relu", label: "ReLU", description: "Fast, good default" },
          { value: "tanh", label: "Tanh", description: "Centered at zero" },
          { value: "logistic", label: "Sigmoid", description: "Classic activation" },
        ],
        default: "relu",
      },
      {
        key: "learning_rate_init",
        type: "slider",
        label: "Initial Learning Rate",
        description: "Initial learning rate for weight updates",
        tooltip: "Lower values are more stable but slower.",
        min: 0.0001,
        max: 0.1,
        step: 0.0001,
        default: 0.001,
        displayFormat: (v: number) => v.toFixed(4),
      },

      // --- Advanced Parameters ---
      {
        key: "solver",
        type: "select",
        label: "Optimizer",
        description: "Weight optimization algorithm",
        tooltip: "Adam is usually best. LBFGS good for small datasets.",
        options: [
          { value: "adam", label: "Adam" },
          { value: "sgd", label: "SGD" },
          { value: "lbfgs", label: "L-BFGS" },
        ],
        default: "adam",
        advanced: true,
      },
      {
        key: "alpha",
        type: "slider",
        label: "L2 Regularization",
        description: "L2 penalty (regularization) parameter",
        tooltip: "Higher values prevent overfitting.",
        min: 0,
        max: 1,
        step: 0.0001,
        default: 0.0001,
        displayFormat: (v: number) => v.toFixed(4),
        advanced: true,
      },
      {
        key: "batch_size",
        type: "select",
        label: "Batch Size",
        description: "Size of minibatches for SGD/Adam",
        tooltip: "Auto uses min(200, n_samples).",
        options: [
          { value: "auto", label: "Auto" },
          { value: "32", label: "32" },
          { value: "64", label: "64" },
          { value: "128", label: "128" },
          { value: "256", label: "256" },
        ],
        default: "auto",
        advanced: true,
      },
      {
        key: "max_iter",
        type: "number",
        label: "Max Iterations",
        description: "Maximum number of iterations",
        tooltip: "Increase if model doesn't converge.",
        min: 50,
        max: 2000,
        default: 200,
        advanced: true,
      },
      {
        key: "early_stopping",
        type: "switch",
        label: "Early Stopping",
        description: "Stop training when validation score stops improving",
        tooltip: "Helps prevent overfitting.",
        default: true,
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
          field: "learning_rate_init",
          rules: [
            { type: "required", message: "Learning rate is required" },
            { type: "min", value: 0.0001, message: "Must be at least 0.0001" },
          ],
        },
        {
          field: "max_iter",
          rules: [
            { type: "min", value: 50, message: "Must be at least 50" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        hidden_layer_sizes: {
          type: "categorical",
          choices: ["(50,)", "(100,)", "(100, 50)", "(100, 100)", "(128, 64, 32)"],
        },
        activation: { type: "categorical", choices: ["relu", "tanh", "logistic"] },
        solver: { type: "categorical", choices: ["adam", "sgd"] },
        alpha: { type: "float", low: 0.0001, high: 0.1, log: true },
        learning_rate_init: { type: "float", low: 0.0001, high: 0.01, log: true },
        batch_size: { type: "categorical", choices: ["auto", "32", "64", "128"] },
      },
      nTrials: 50,
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
        cost: 10,
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
        description: "Not directly available for neural networks",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Not applicable for neural networks",
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
        cost: 20,
      },
      shap_waterfall: {
        key: "shap_waterfall",
        name: "SHAP Waterfall",
        description: "Explain individual predictions",
        cost: 10,
      },
      partial_dependence: {
        key: "partial_dependence",
        name: "Partial Dependence",
        description: "Effect of features on predictions",
        cost: 15,
      },
    },
  },
};

export default neuralNetworkConfig;
