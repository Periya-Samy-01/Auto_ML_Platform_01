import type { AlgorithmConfig } from "./types";

/**
 * Logistic Regression Algorithm Configuration
 *
 * This single file contains ALL configuration for the Logistic Regression algorithm:
 * - Metadata (name, description, icon, best use cases)
 * - Capabilities (what it can/can't do)
 * - Model hyperparameters (UI field definitions)
 * - Validation rules
 * - Optuna search space for hyperparameter tuning
 * - Cost calculation
 * - Evaluation metrics
 * - Visualization plots
 */

export const logisticRegressionConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "logistic_regression",
    name: "Logistic Regression",
    shortName: "LogReg",
    description:
      "A linear model for binary and multiclass classification that estimates probabilities using the logistic function.",
    icon: "📈",
    category: "linear",
    bestFor: [
      "Binary classification problems",
      "When you need probability estimates",
      "Interpretable models with feature coefficients",
      "Baseline model for classification tasks",
      "Text classification with TF-IDF features",
    ],
    limitations: [
      "Assumes linear decision boundary",
      "May underperform on complex non-linear patterns",
      "Sensitive to feature scaling",
      "Can struggle with highly correlated features",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["classification"],
    supportsMulticlass: true,
    supportsProbabilities: true,
    supportsFeatureImportance: true, // Via coefficients
    supportsExplainability: true, // Via SHAP
    handlesImbalanced: true, // Via class_weight
    handlesMissingValues: false,
    requiresScaling: true,
    supportsWarmStart: true,
  },

  // ==========================================================================
  // MODEL CONFIGURATION
  // ==========================================================================
  model: {
    hyperparameters: [
      // --- Regularization Section ---
      {
        key: "penalty",
        type: "radio",
        label: "Regularization Type",
        description: "Type of regularization to prevent overfitting",
        tooltip:
          "L1 (Lasso) can zero out features for feature selection. L2 (Ridge) shrinks all coefficients. ElasticNet combines both.",
        options: [
          {
            value: "l2",
            label: "L2 (Ridge)",
            description: "Shrinks coefficients uniformly",
          },
          {
            value: "l1",
            label: "L1 (Lasso)",
            description: "Can zero out features",
          },
          {
            value: "elasticnet",
            label: "Elastic Net",
            description: "Combines L1 and L2",
          },
          {
            value: "none",
            label: "None",
            description: "No regularization",
          },
        ],
        default: "l2",
      },
      {
        key: "C",
        type: "slider",
        label: "Regularization Strength (C)",
        description: "Inverse of regularization strength. Smaller values = stronger regularization.",
        tooltip:
          "Controls the trade-off between fitting the training data and keeping the model simple. Lower values mean more regularization.",
        min: 0.001,
        max: 100,
        step: 0.001,
        default: 1.0,
        displayFormat: (v: number) => v.toFixed(3),
      },
      {
        key: "l1_ratio",
        type: "slider",
        label: "L1 Ratio",
        description: "Balance between L1 and L2 (0 = L2 only, 1 = L1 only)",
        tooltip: "Only used when penalty is Elastic Net",
        min: 0,
        max: 1,
        step: 0.05,
        default: 0.5,
        dependsOn: { field: "penalty", value: "elasticnet" },
      },

      // --- Solver Section ---
      {
        key: "solver",
        type: "select",
        label: "Solver",
        description: "Algorithm for optimization",
        tooltip:
          "Different solvers work better for different penalty types and dataset sizes.",
        options: [
          { value: "lbfgs", label: "LBFGS (default)" },
          { value: "liblinear", label: "Liblinear" },
          { value: "newton-cg", label: "Newton-CG" },
          { value: "newton-cholesky", label: "Newton-Cholesky" },
          { value: "sag", label: "SAG" },
          { value: "saga", label: "SAGA" },
        ],
        default: "lbfgs",
      },

      // --- Advanced Section ---
      {
        key: "max_iter",
        type: "number",
        label: "Max Iterations",
        description: "Maximum iterations for solver convergence",
        tooltip: "Increase if the model doesn't converge",
        min: 50,
        max: 10000,
        step: 50,
        default: 100,
        advanced: true,
      },
      {
        key: "tol",
        type: "number",
        label: "Tolerance",
        description: "Convergence tolerance",
        tooltip: "Stop when improvement is less than this value",
        min: 0.0000001,
        max: 0.01,
        step: 0.0000001,
        default: 0.0001,
        advanced: true,
      },
      {
        key: "class_weight",
        type: "radio",
        label: "Class Weight",
        description: "How to handle class imbalance",
        tooltip:
          "'Balanced' automatically adjusts weights inversely proportional to class frequencies.",
        options: [
          { value: "none", label: "None", description: "Equal weight for all classes" },
          { value: "balanced", label: "Balanced", description: "Auto-adjust for imbalance" },
        ],
        default: "none",
        advanced: true,
      },
      {
        key: "fit_intercept",
        type: "switch",
        label: "Fit Intercept",
        description: "Whether to fit an intercept term",
        tooltip: "Usually keep enabled unless data is already centered",
        default: true,
        advanced: true,
      },
    ],

    validation: {
      fields: [
        {
          field: "C",
          rules: [
            { type: "required", message: "Regularization strength is required" },
            { type: "min", value: 0.001, message: "C must be at least 0.001" },
            { type: "max", value: 100, message: "C must be at most 100" },
          ],
        },
        {
          field: "max_iter",
          rules: [
            { type: "required", message: "Max iterations is required" },
            { type: "min", value: 50, message: "Must be at least 50" },
          ],
        },
      ],
      crossField: [
        {
          fields: ["penalty", "solver"],
          validate: (values) => {
            const penalty = values.penalty as string;
            const solver = values.solver as string;

            // L1 penalty only works with liblinear and saga
            if (penalty === "l1" && !["liblinear", "saga"].includes(solver)) {
              return "L1 penalty requires 'liblinear' or 'saga' solver";
            }
            // ElasticNet only works with saga
            if (penalty === "elasticnet" && solver !== "saga") {
              return "Elastic Net penalty requires 'saga' solver";
            }
            // None penalty doesn't work with liblinear
            if (penalty === "none" && solver === "liblinear") {
              return "'None' penalty doesn't work with 'liblinear' solver";
            }
            return null;
          },
          message: "Invalid solver/penalty combination",
        },
      ],
    },

    optuna: {
      searchSpace: {
        C: { type: "float", low: 0.001, high: 100, log: true },
        penalty: { type: "categorical", choices: ["l1", "l2", "elasticnet", "none"] },
        solver: { type: "categorical", choices: ["lbfgs", "liblinear", "saga"] },
        max_iter: { type: "int", low: 100, high: 1000, step: 100 },
        class_weight: { type: "categorical", choices: ["none", "balanced"] },
      },
      nTrials: 50,
      timeout: 300, // 5 minutes
      pruner: "median",
    },

    costs: {
      base: 1,
      perSample: 0.0001, // Very fast algorithm
      crossValidation: {
        multiplier: 5, // 5-fold CV = 5x cost
      },
      optuna: {
        perTrial: 1,
        maxTrials: 100,
      },
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
      "balanced_accuracy",
      "matthews_corrcoef",
    ],
    defaultMetrics: ["accuracy", "precision", "recall", "f1", "roc_auc"],
    metricDefinitions: {
      accuracy: {
        key: "accuracy",
        name: "Accuracy",
        formula: "(TP + TN) / (TP + TN + FP + FN)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Proportion of correct predictions. Can be misleading with imbalanced classes.",
        category: "classification",
      },
      precision: {
        key: "precision",
        name: "Precision",
        formula: "TP / (TP + FP)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Of all positive predictions, how many are actually positive.",
        category: "classification",
      },
      recall: {
        key: "recall",
        name: "Recall",
        formula: "TP / (TP + FN)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Of all actual positives, how many did we correctly identify.",
        category: "classification",
      },
      f1: {
        key: "f1",
        name: "F1 Score",
        formula: "2 * (Precision * Recall) / (Precision + Recall)",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Harmonic mean of precision and recall. Good for imbalanced datasets.",
        category: "classification",
      },
      roc_auc: {
        key: "roc_auc",
        name: "ROC AUC",
        formula: "Area under ROC curve",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Model's ability to distinguish between classes. 0.5 = random, 1.0 = perfect.",
        category: "classification",
      },
      log_loss: {
        key: "log_loss",
        name: "Log Loss",
        formula: "-mean(y * log(p) + (1-y) * log(1-p))",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Penalizes confident wrong predictions heavily. Lower is better.",
        category: "classification",
      },
      balanced_accuracy: {
        key: "balanced_accuracy",
        name: "Balanced Accuracy",
        formula: "(Sensitivity + Specificity) / 2",
        range: [0, 1],
        higherIsBetter: true,
        tooltip: "Average of recall for each class. Good for imbalanced data.",
        category: "classification",
      },
      matthews_corrcoef: {
        key: "matthews_corrcoef",
        name: "Matthews Correlation",
        formula: "(TP*TN - FP*FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))",
        range: [-1, 1],
        higherIsBetter: true,
        tooltip: "Balanced measure even for imbalanced classes. -1 to 1 scale.",
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
      "coefficient_plot",
      "probability_calibration",
      "shap_summary",
      "shap_waterfall",
    ],
    defaultPlots: ["confusion_matrix", "roc_curve", "coefficient_plot"],
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
        requirements: { minSamples: 100 },
        cost: 5,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Feature importance via model coefficients",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "How well-calibrated are the probability estimates",
        requirements: { requiresProbabilities: true, minSamples: 100 },
        cost: 2,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Feature importance with direction of impact",
        cost: 10,
      },
      shap_waterfall: {
        key: "shap_waterfall",
        name: "SHAP Waterfall",
        description: "Explain individual predictions",
        cost: 5,
      },
      // Placeholder definitions for plots not supported by this algorithm
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Not applicable - use Coefficient Plot",
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
      partial_dependence: {
        key: "partial_dependence",
        name: "Partial Dependence",
        description: "Effect of features on predictions",
        cost: 10,
      },
    },
  },
};

export default logisticRegressionConfig;
