import type { AlgorithmConfig } from "./types";

/**
 * K-Means Clustering Algorithm Configuration
 *
 * Unsupervised learning algorithm for clustering data.
 */

export const kmeansConfig: AlgorithmConfig = {
  // ==========================================================================
  // METADATA
  // ==========================================================================
  metadata: {
    id: "kmeans",
    name: "K-Means Clustering",
    shortName: "KMeans",
    description:
      "An unsupervised learning algorithm that partitions data into k clusters by minimizing within-cluster variance.",
    icon: "🔵",
    category: "clustering",
    bestFor: [
      "Customer segmentation",
      "Finding natural groupings in data",
      "Image compression",
      "Anomaly detection",
      "Feature engineering (cluster labels)",
    ],
    limitations: [
      "Must specify number of clusters (k) in advance",
      "Assumes spherical clusters of similar size",
      "Sensitive to initial centroid positions",
      "Not suitable for non-convex shapes",
      "Sensitive to outliers",
    ],
    learnMoreUrl: "https://scikit-learn.org/stable/modules/clustering.html#k-means",
  },

  // ==========================================================================
  // CAPABILITIES
  // ==========================================================================
  capabilities: {
    problemTypes: ["classification"], // Using classification as proxy for clustering
    supportsMulticlass: true,
    supportsProbabilities: false,
    supportsFeatureImportance: false,
    supportsExplainability: false,
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
        key: "n_clusters",
        type: "slider",
        label: "Number of Clusters (K)",
        description: "The number of clusters to form",
        tooltip: "Use elbow method or silhouette score to find optimal k.",
        min: 2,
        max: 20,
        step: 1,
        default: 3,
      },
      {
        key: "init",
        type: "radio",
        label: "Initialization Method",
        description: "Method for initializing centroids",
        tooltip: "K-means++ is smarter and usually better.",
        options: [
          { value: "k-means++", label: "K-Means++", description: "Smart initialization" },
          { value: "random", label: "Random", description: "Random centroid selection" },
        ],
        default: "k-means++",
      },

      // --- Advanced Parameters ---
      {
        key: "n_init",
        type: "slider",
        label: "Number of Initializations",
        description: "Number of times to run with different seeds",
        tooltip: "More runs = better results but slower.",
        min: 1,
        max: 50,
        step: 1,
        default: 10,
        advanced: true,
      },
      {
        key: "max_iter",
        type: "number",
        label: "Max Iterations",
        description: "Maximum iterations for a single run",
        tooltip: "Usually converges well before this limit.",
        min: 100,
        max: 1000,
        default: 300,
        advanced: true,
      },
      {
        key: "algorithm",
        type: "select",
        label: "Algorithm",
        description: "K-means algorithm variant",
        tooltip: "Lloyd is classic, Elkan is faster for well-defined clusters.",
        options: [
          { value: "lloyd", label: "Lloyd (classic)" },
          { value: "elkan", label: "Elkan (faster)" },
        ],
        default: "lloyd",
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
          field: "n_clusters",
          rules: [
            { type: "required", message: "Number of clusters is required" },
            { type: "min", value: 2, message: "Must have at least 2 clusters" },
          ],
        },
      ],
      crossField: [],
    },

    optuna: {
      searchSpace: {
        n_clusters: { type: "int", low: 2, high: 15 },
        init: { type: "categorical", choices: ["k-means++", "random"] },
        n_init: { type: "int", low: 5, high: 20 },
        algorithm: { type: "categorical", choices: ["lloyd", "elkan"] },
      },
      nTrials: 30,
      timeout: 300,
      pruner: "median",
    },

    costs: {
      base: 2,
      perSample: 0.0001,
      crossValidation: { multiplier: 1 },
      optuna: { perTrial: 2, maxTrials: 50 },
    },
  },

  // ==========================================================================
  // EVALUATION CONFIGURATION
  // ==========================================================================
  evaluate: {
    supportedMetrics: [
      "silhouette_score",
      "davies_bouldin_index",
      "calinski_harabasz_index",
      "inertia",
    ],
    defaultMetrics: ["silhouette_score", "inertia"],
    metricDefinitions: {
      silhouette_score: {
        key: "silhouette_score",
        name: "Silhouette Score",
        formula: "(b - a) / max(a, b)",
        range: [-1, 1],
        higherIsBetter: true,
        tooltip: "Measures cluster cohesion and separation. 1 is perfect, -1 is worst.",
        category: "clustering",
      },
      davies_bouldin_index: {
        key: "davies_bouldin_index",
        name: "Davies-Bouldin Index",
        formula: "Average similarity ratio",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Lower is better. Measures average similarity between clusters.",
        category: "clustering",
      },
      calinski_harabasz_index: {
        key: "calinski_harabasz_index",
        name: "Calinski-Harabasz Index",
        formula: "Between/Within cluster dispersion ratio",
        range: "unbounded",
        higherIsBetter: true,
        tooltip: "Higher is better. Ratio of between-cluster to within-cluster dispersion.",
        category: "clustering",
      },
      inertia: {
        key: "inertia",
        name: "Inertia",
        formula: "Sum of squared distances to centroids",
        range: "unbounded",
        higherIsBetter: false,
        tooltip: "Lower is better. Sum of squared distances to cluster centers.",
        category: "clustering",
      },
    },
  },

  // ==========================================================================
  // VISUALIZATION CONFIGURATION
  // ==========================================================================
  visualize: {
    supportedPlots: ["confusion_matrix", "learning_curve"], // Using as placeholders for cluster plots
    defaultPlots: ["confusion_matrix"],
    plotDefinitions: {
      confusion_matrix: {
        key: "confusion_matrix",
        name: "Cluster Scatter Plot",
        description: "2D visualization of data points colored by cluster",
        cost: 1,
      },
      learning_curve: {
        key: "learning_curve",
        name: "Elbow Plot",
        description: "Inertia vs number of clusters for optimal k selection",
        cost: 3,
      },
      // Placeholders
      roc_curve: {
        key: "roc_curve",
        name: "Silhouette Plot",
        description: "Silhouette scores for each sample by cluster",
        cost: 2,
      },
      precision_recall_curve: {
        key: "precision_recall_curve",
        name: "Precision-Recall Curve",
        description: "Not applicable for clustering",
        cost: 1,
      },
      feature_importance: {
        key: "feature_importance",
        name: "Feature Importance",
        description: "Not available for K-Means",
        cost: 1,
      },
      coefficient_plot: {
        key: "coefficient_plot",
        name: "Coefficient Plot",
        description: "Not applicable for K-Means",
        cost: 1,
      },
      residual_plot: {
        key: "residual_plot",
        name: "Residual Plot",
        description: "Not applicable for clustering",
        cost: 1,
      },
      prediction_vs_actual: {
        key: "prediction_vs_actual",
        name: "Prediction vs Actual",
        description: "Not applicable for clustering",
        cost: 1,
      },
      probability_calibration: {
        key: "probability_calibration",
        name: "Probability Calibration",
        description: "Not applicable for clustering",
        cost: 2,
      },
      shap_summary: {
        key: "shap_summary",
        name: "SHAP Summary",
        description: "Not applicable for clustering",
        cost: 10,
      },
      shap_waterfall: {
        key: "shap_waterfall",
        name: "SHAP Waterfall",
        description: "Not applicable for clustering",
        cost: 5,
      },
      partial_dependence: {
        key: "partial_dependence",
        name: "Partial Dependence",
        description: "Not applicable for clustering",
        cost: 8,
      },
    },
  },
};

export default kmeansConfig;
