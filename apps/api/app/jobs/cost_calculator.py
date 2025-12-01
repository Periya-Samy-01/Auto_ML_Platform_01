"""
Job cost calculation based on workflow complexity
"""

from typing import Dict, Any


# Cost constants (in credits)
BASE_JOB_COST = 10  # Minimum cost for any job
DATASET_NODE_COST = 0  # Free (just loading data)
PREPROCESS_NODE_COST = 5  # Per preprocessing operation
MODEL_NODE_BASE_COST = 20  # Base cost per model training
MODEL_NODE_HPO_COST = 10  # Additional cost if HPO enabled
MODEL_NODE_PER_ALGORITHM_COST = 10  # Cost per algorithm to train
EVALUATION_NODE_COST = 5  # Per evaluation operation
VISUALIZE_NODE_COST = 3  # Per visualization
SAVE_NODE_COST = 2  # Per save operation


def calculate_job_cost(workflow_json: Dict[str, Any]) -> int:
    """
    Calculate estimated credit cost for a job based on workflow complexity.

    Args:
        workflow_json: Workflow graph JSON with nodes and edges

    Returns:
        Estimated cost in credits

    Cost breakdown:
        - Base cost: 10 credits
        - Dataset node: 0 credits
        - Preprocess node: 5 credits each
        - Model node: 20 base + 10 per algorithm + 10 if HPO enabled
        - Evaluation node: 5 credits
        - Visualize node: 3 credits
        - Save node: 2 credits

    Example:
        Workflow: 1 dataset + 2 preprocess + 1 model (3 algorithms, HPO) + 1 eval
        Cost: 10 + 0 + 10 + 10 + (20 + 10 + 30) + 5 = 95 credits
    """
    total_cost = BASE_JOB_COST

    # Extract nodes from workflow
    nodes = workflow_json.get("nodes", [])

    if not nodes:
        # Empty workflow, return base cost only
        return BASE_JOB_COST

    for node in nodes:
        node_type = node.get("type", "").lower()
        node_data = node.get("data", {})

        if node_type == "dataset":
            # Dataset loading is free
            total_cost += DATASET_NODE_COST

        elif node_type == "preprocess":
            # Each preprocessing operation costs
            total_cost += PREPROCESS_NODE_COST

        elif node_type == "model":
            # Model training cost
            node_cost = MODEL_NODE_BASE_COST

            # Check for HPO (hyperparameter optimization)
            hpo_enabled = node_data.get("hpo_enabled", False)
            if hpo_enabled:
                node_cost += MODEL_NODE_HPO_COST

            # Cost per algorithm to train
            algorithms = node_data.get("algorithms", [])
            if algorithms:
                # If specific algorithms listed
                num_algorithms = len(algorithms)
            else:
                # Default: assume 1 algorithm
                num_algorithms = 1

            node_cost += MODEL_NODE_PER_ALGORITHM_COST * num_algorithms

            total_cost += node_cost

        elif node_type == "evaluation" or node_type == "evaluate":
            # Evaluation/metrics calculation
            total_cost += EVALUATION_NODE_COST

        elif node_type == "visualize":
            # Visualization generation
            total_cost += VISUALIZE_NODE_COST

        elif node_type == "save":
            # Model saving
            total_cost += SAVE_NODE_COST

    return total_cost


def estimate_job_duration(workflow_json: Dict[str, Any]) -> int:
    """
    Estimate job duration in seconds based on workflow complexity.

    Args:
        workflow_json: Workflow graph JSON

    Returns:
        Estimated duration in seconds

    Note:
        This is a rough estimate. Actual duration depends on:
        - Dataset size
        - Algorithm complexity
        - HPO trials
        - Server load
    """
    nodes = workflow_json.get("nodes", [])

    if not nodes:
        return 60  # 1 minute minimum

    # Base time: 30 seconds
    estimated_seconds = 30

    for node in nodes:
        node_type = node.get("type", "").lower()
        node_data = node.get("data", {})

        if node_type == "dataset":
            # Dataset loading: ~10 seconds
            estimated_seconds += 10

        elif node_type == "preprocess":
            # Preprocessing: ~20 seconds per operation
            estimated_seconds += 20

        elif node_type == "model":
            # Base training time: 60 seconds
            node_time = 60

            # HPO multiplier
            hpo_enabled = node_data.get("hpo_enabled", False)
            if hpo_enabled:
                trials = node_data.get("hpo_trials", 10)
                node_time += trials * 5  # ~5 seconds per trial

            # Per algorithm
            algorithms = node_data.get("algorithms", [])
            num_algorithms = len(algorithms) if algorithms else 1
            node_time *= num_algorithms

            estimated_seconds += node_time

        elif node_type == "evaluation":
            # Evaluation: ~15 seconds
            estimated_seconds += 15

        elif node_type == "visualize":
            # Visualization: ~10 seconds
            estimated_seconds += 10

    return estimated_seconds


def get_refund_percentage(cancellation_count_30d: int) -> float:
    """
    Calculate refund percentage based on user's cancellation history.

    Args:
        cancellation_count_30d: Number of cancellations in last 30 days

    Returns:
        Refund percentage (0.0 to 1.0)

    Formula:
        refund = 1.0 - (min(cancellation_count, 10) * 0.05)

    Examples:
        - 0 cancellations: 100% refund
        - 5 cancellations: 75% refund
        - 10+ cancellations: 50% refund
    """
    penalty = min(cancellation_count_30d, 10) * 0.05
    refund_percentage = 1.0 - penalty

    return max(refund_percentage, 0.5)  # Minimum 50% refund


def calculate_refund_amount(
    original_cost: int,
    cancellation_count_30d: int,
) -> tuple[int, float]:
    """
    Calculate refund amount with penalty.

    Args:
        original_cost: Original job cost in credits
        cancellation_count_30d: User's cancellation count in last 30 days

    Returns:
        Tuple of (refund_amount, refund_percentage)
    """
    refund_percentage = get_refund_percentage(cancellation_count_30d)
    refund_amount = int(original_cost * refund_percentage)

    return refund_amount, refund_percentage
