import type { AlgorithmConfig } from "./types";

/**
 * Linear Regression Algorithm Configuration
 *
 * Linear model for regression with optional regularization.
 */

export const linearRegressionConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "linear_regression",
    name: "Linear Regression",
    shortName: "LinReg",
    description:
      "A linear approach for modeling the relationship between a dependent variable and independent variables. Supports Ridge, Lasso, and ElasticNet regularization.",
    icon: "📉",
    category: "linear",
    bestFor: [
      "Continuous target prediction",
      "When relationship between features and target is linear",
      "Interpretable models with feature coefficients",
      "Baseline model for regression tasks",
      "Feature selection with Lasso regularization",
    ],
    limitations: [
      "Assumes linear relationship between features and target",
      "Sensitive to outliers",
      "Assumes features are independent (multicollinearity issues)",
      "May underperform on complex non-linear patterns",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/linear_model.html",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["regression"],
    supportsMulticlass: false,
    supportsProbabilities: false,
    supportsFeatureImportance: true,
    supportsExplainability: true,
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
        key: "regularization",
        type: "radio",
        label: "Regularization Type",
        description: "Type of regularization to apply",
        tooltip: "Ridge (L2) shrinks coefficients, Lasso (L1) can zero out features, ElasticNet combines both.",
        options: [
          { value: "none", label: "None (OLS)", description: "Ordinary Least Squares" },
          { value: "ridge", label: "Ridge (L2)", description: "Shrinks all coefficients" },
          { value: "lasso", label: "Lasso (L1)", description: "Can zero out features" },
          { value: "elasticnet", label: "Elastic Net", description: "Combines L1 and L2" },
        ],
        default: "none",
      },
      {
        key: "alpha",
        type: "slider",
        label: "Regularization Strength",
        description: "Strength of regularization (higher = stronger)",
        tooltip: "Controls the trade-off between fitting the data and keeping coefficients small.",
        min: 0.0001,
        max: 100,
        step: 0.0001,
        default: 1.0,
        displayFormat: (v: number) => v.toFixed(4),
        dependsOn: { field: "regularization", value: "none" },
      },

      // --- Advanced Parameters ---
      {
        key: "fit_intercept",
        type: "switch",
        label: "Fit Intercept",
        description: "Whether to calculate the intercept",
        tooltip: "Usually keep enabled unless data is already centered.",
        default: true,
        advanced: true,
      },
      {
        key: "l1_ratio",
        type: "slider",
        label: "L1 Ratio (Elastic Net)",
        description: "L1/L2 mixing ratio (0=Ridge, 1=Lasso)",
        tooltip: "Only used when regularization is Elastic Net.",
        min: 0,
        max: 1,
        step: 0.1,
        default: 0.5,
        dependsOn: { field: "regularization", value: "elasticnet" },
        advanced: true,
      },
      {
        key: "max_iter",
        type: "number",
        label: "Max Iterations",
        description: "Maximum iterations for iterative solvers",
        tooltip: "Increase if the model doesn't converge.",
        min: 100,
        max: 10000,
        default: 1000,
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
          field: "alpha",
          rules: [
            { type: "min", value: 0.0001, message: "Alpha must be at least 0.0001" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        regularization: { type: "categorical", choices: ["none", "ridge", "lasso", "elasticnet"] },
        alpha: { type: "float", low: 0.0001, high: 100, log: true },
        l1_ratio: { type: "float", low: 0.1, high: 0.9 },
      },
      nTrials: 50,
      timeout: 300,
      pruner: "median",
    },

    costs: {
      base: 1,
      perSample: 0.00001,
      crossValidation: { multiplier: 5 },
      optuna: { perTrial: 1, maxTrials: 100 },
    },
  },

  // ==========================================================================
  // EVALUATION CONFIGURATION
  // ==========================================================================
  evaluate: {
    supportedMetrics: ["mse", "rmse", "mae", "r2", "mape", "explained_variance"],
    defaultMetrics: ["rmse", "r2", "mae"],
    metricDefinitions: {
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
        tooltip: "Proportion of variance explained by the model. 1.0 is perfect.",
        category: "regression",
      },
      mape: {
        key: "mape",
        name: "Mean Absolute % Error",
        formula: "mean(|y - ŷ|/y) * 100",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Average percentage error. Useful for interpretability.",
        category: "regression",
      },
      explained_variance: {
        key: "explained_variance",
        name: "Explained Variance",
        formula: "1 - Var(y - ŷ)/Var(y)",
        range: "unbounded",
        higherIsBetter: true,
        tooltip: "Similar to R² but can be different if predictions are biased.",
        category: "regression",
      },
    },
  },

  // ==========================================================================
  // VISUALIZATION CONFIGURATION
  // ==========================================================================
  visualize: {
    supportedPlots: [
      "prediction_vs_actual",
      "residual_plot",
      "coefficient_plot",
      "learning_curve",
      "shap_summary",
    ],
    defaultPlots: ["prediction_vs_actual", "coefficient_plot", "residual_plot"],
    plotDefinitions: {
      prediction_vs_actual: {
        key: "prediction_vs_actual",
        name: "Prediction vs Actual",
        description: "Scatter plot comparing predictions to actual values",
        cost: 1,
      },
      residual_plot: {
        key: "residual_plot",
        name: "Residual Plot",
        description: "Residuals vs predicted values",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Feature importance via model coefficients",
        cost: 1,
      },
      learning_curve: {
        key: "learning_curve",
        name: "Learning Curve",
        description: "Model performance vs training size",
        cost: 3,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Feature importance with direction of impact",
        cost: 8,
      },
      // Placeholder definitions
      confusion_matrix: {
        key: "confusion_matrix",
        name: "Confusion Matrix",
        description: "For classification only",
        cost: 1,
      },
      roc_curve: {
        key: "roc_curve",
        name: "ROC Curve",
        description: "For classification only",
        cost: 1,
      },
      precision_recall_curve: {
        key: "precision_recall_curve",
        name: "Precision-Recall Curve",
        description: "For classification only",
        cost: 1,
      },
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Use Coefficient Plot for linear models",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "For classification only",
        cost: 2,
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

export default linearRegressionConfig;
