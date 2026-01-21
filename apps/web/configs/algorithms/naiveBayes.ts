import type { AlgorithmConfig } from "./types";

/**
 * Naive Bayes Algorithm Configuration
 *
 * Probabilistic classifier based on Bayes' theorem.
 */

export const naiveBayesConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "naive_bayes",
    name: "Naive Bayes",
    shortName: "NB",
    description:
      "A probabilistic classifier based on Bayes' theorem with the assumption of feature independence. Fast and effective for many use cases.",
    icon: "🎲",
    category: "linear",
    bestFor: [
      "Text classification (spam detection, sentiment analysis)",
      "When features are independent",
      "Real-time prediction requirements",
      "Multi-class classification",
      "When training data is limited",
    ],
    limitations: [
      "Assumes feature independence (naive assumption)",
      "Can be outperformed by more complex models",
      "Zero probability problem (requires smoothing)",
      "Not suitable when features are correlated",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/naive_bayes.html",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["classification"],
    supportsMulticlass: true,
    supportsProbabilities: true,
    supportsFeatureImportance: false,
    supportsExplainability: false,
    handlesImbalanced: false,
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
        key: "variant",
        type: "radio",
        label: "Naive Bayes Variant",
        description: "Type of Naive Bayes algorithm",
        tooltip: "Gaussian for continuous features, Multinomial for counts, Bernoulli for binary.",
        options: [
          { value: "gaussian", label: "Gaussian", description: "For continuous features" },
          { value: "multinomial", label: "Multinomial", description: "For count features (text)" },
          { value: "bernoulli", label: "Bernoulli", description: "For binary features" },
        ],
        default: "gaussian",
      },

      // --- Advanced Parameters ---
      {
        key: "var_smoothing",
        type: "slider",
        label: "Variance Smoothing",
        description: "Portion of largest variance added for stability",
        tooltip: "Only used for Gaussian variant. Prevents numerical issues.",
        min: 1e-12,
        max: 1e-3,
        step: 1e-12,
        default: 1e-9,
        displayFormat: (v: number) => v.toExponential(2),
        dependsOn: { field: "variant", value: "gaussian" },
        advanced: true,
      },
      {
        key: "alpha",
        type: "slider",
        label: "Smoothing Parameter",
        description: "Additive smoothing parameter (Laplace smoothing)",
        tooltip: "Used for Multinomial and Bernoulli. Prevents zero probabilities.",
        min: 0,
        max: 10,
        step: 0.1,
        default: 1.0,
        advanced: true,
      },
      {
        key: "fit_prior",
        type: "switch",
        label: "Fit Prior",
        description: "Whether to learn class prior probabilities",
        tooltip: "If false, uses uniform prior.",
        default: true,
        advanced: true,
      },
    ],

    validation: {
      fields: [
        {
          field: "alpha",
          rules: [
            { type: "min", value: 0, message: "Alpha must be non-negative" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        variant: { type: "categorical", choices: ["gaussian", "multinomial", "bernoulli"] },
        alpha: { type: "float", low: 0.01, high: 10, log: true },
        var_smoothing: { type: "float", low: 1e-12, high: 1e-6, log: true },
      },
      nTrials: 30,
      timeout: 180,
      pruner: "median",
    },

    costs: {
      base: 1,
      perSample: 0.00001,
      crossValidation: { multiplier: 5 },
      optuna: { perTrial: 1, maxTrials: 50 },
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
        cost: 3,
      },
      // Placeholders
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Not available for Naive Bayes",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Not applicable for Naive Bayes",
        cost: 1,
      },
      residual_plot: {
        key: "residual_plot",
        name: "Residual Plot",
        description: "For regression only",
        cost: 1,
      },
      prediction_vs_actual: {
        key: "prediction_vs_actual",
        name: "Prediction vs Actual",
        description: "For regression only",
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

export default naiveBayesConfig;
