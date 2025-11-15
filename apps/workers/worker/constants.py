#apps/workers/worker/constants.py
"""
Constants for ML worker module.
Defines task types, model types, and valid values for type safety.
"""

# Task types
TASK_CLASSIFICATION = "classification"
TASK_REGRESSION = "regression"
TASK_CLUSTERING = "clustering"
TASK_DIMENSIONALITY_REDUCTION = "dimensionality_reduction"

# Groupings
SUPERVISED_TASKS = {TASK_CLASSIFICATION, TASK_REGRESSION}
UNSUPERVISED_TASKS = {TASK_CLUSTERING, TASK_DIMENSIONALITY_REDUCTION}
ALL_TASKS = SUPERVISED_TASKS | UNSUPERVISED_TASKS

# Model types (for SHAP/feature importance)
MODEL_TYPE_LINEAR = "linear"
MODEL_TYPE_TREE = "tree"
MODEL_TYPE_NEURAL = "neural"
MODEL_TYPE_DISTANCE = "distance"
MODEL_TYPE_CLUSTERING = "clustering"
MODEL_TYPE_DIMENSIONALITY = "dimensionality"

# Valid values for validation
VALID_TASKS = ALL_TASKS
VALID_MODEL_TYPES = {
    MODEL_TYPE_LINEAR,
    MODEL_TYPE_TREE,
    MODEL_TYPE_NEURAL,
    MODEL_TYPE_DISTANCE,
    MODEL_TYPE_CLUSTERING,
    MODEL_TYPE_DIMENSIONALITY,
}