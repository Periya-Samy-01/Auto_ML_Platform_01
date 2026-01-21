"""
Workflow Validator

Validates workflow graphs and node configurations before execution.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from app.plugins.registry import PluginRegistry
from app.plugins.preprocessing.registry import get_method as get_preprocessing_method
from .schemas import (
    NodeType,
    WorkflowNode,
    WorkflowEdge,
    ValidationError,
    WorkflowValidateResponse,
)


class WorkflowValidator:
    """
    Validates workflow graph structure and node configurations.

    Checks for:
    - Graph connectivity (no orphan nodes)
    - Proper node connections (Dataset → Preprocessing → Split → Model → Evaluate → Visualize)
    - Required configurations (dataset selected, algorithm selected, etc.)
    - Cyclic dependencies
    - Valid node configurations
    """

    def __init__(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]):
        self.nodes = {n.id: n for n in nodes}
        self.edges = edges
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

        # Build adjacency lists
        self.outgoing: Dict[str, List[str]] = defaultdict(list)  # node -> [downstream nodes]
        self.incoming: Dict[str, List[str]] = defaultdict(list)  # node -> [upstream nodes]

        for edge in edges:
            self.outgoing[edge.source].append(edge.target)
            self.incoming[edge.target].append(edge.source)

    def validate(self) -> WorkflowValidateResponse:
        """Run all validation checks."""
        self._validate_graph_structure()
        self._validate_node_connections()
        self._validate_node_configs()
        self._check_cycles()

        return WorkflowValidateResponse(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
        )

    def _add_error(
        self,
        message: str,
        node_id: Optional[str] = None,
        field: Optional[str] = None,
    ):
        """Add a validation error."""
        self.errors.append(ValidationError(
            node_id=node_id,
            field=field,
            message=message,
            severity="error",
        ))

    def _add_warning(
        self,
        message: str,
        node_id: Optional[str] = None,
        field: Optional[str] = None,
    ):
        """Add a validation warning."""
        self.warnings.append(ValidationError(
            node_id=node_id,
            field=field,
            message=message,
            severity="warning",
        ))

    def _validate_graph_structure(self):
        """Validate basic graph structure."""
        if not self.nodes:
            self._add_error("Workflow must have at least one node")
            return

        # Check for dataset node
        dataset_nodes = [n for n in self.nodes.values() if n.type == NodeType.DATASET]
        if not dataset_nodes:
            self._add_error("Workflow must have at least one Dataset node")

        # Check for model node
        model_nodes = [n for n in self.nodes.values() if n.type == NodeType.MODEL]
        if not model_nodes:
            self._add_error("Workflow must have at least one Model node")

        # Check for orphan nodes (nodes not connected to anything except Dataset)
        for node_id, node in self.nodes.items():
            if node.type != NodeType.DATASET:
                if not self.incoming[node_id] and not self.outgoing[node_id]:
                    self._add_error(
                        f"Node is not connected to any other nodes",
                        node_id=node_id,
                    )

    def _validate_node_connections(self):
        """Validate that nodes are connected in the correct order."""
        # Define valid upstream node types for each node type
        valid_upstream = {
            NodeType.DATASET: [],  # Dataset is source, no upstream
            NodeType.PREPROCESSING: [NodeType.DATASET, NodeType.PREPROCESSING],
            NodeType.SPLIT: [NodeType.DATASET, NodeType.PREPROCESSING],
            NodeType.MODEL: [NodeType.SPLIT, NodeType.DATASET, NodeType.PREPROCESSING],
            NodeType.EVALUATE: [NodeType.MODEL],
            NodeType.VISUALIZE: [NodeType.MODEL, NodeType.EVALUATE],
        }

        for node_id, node in self.nodes.items():
            upstream_ids = self.incoming[node_id]

            # Check if required input is connected
            if node.type in [NodeType.PREPROCESSING, NodeType.SPLIT, NodeType.MODEL]:
                if not upstream_ids:
                    self._add_error(
                        f"Node requires an input connection",
                        node_id=node_id,
                    )
                    continue

            # Check if upstream connections are valid types
            allowed_types = valid_upstream.get(node.type, [])
            for upstream_id in upstream_ids:
                upstream_node = self.nodes.get(upstream_id)
                if upstream_node and upstream_node.type not in allowed_types:
                    self._add_error(
                        f"Invalid connection: {upstream_node.type.value} cannot connect to {node.type.value}",
                        node_id=node_id,
                    )

            # Check for multiple inputs where only one is allowed
            if node.type in [NodeType.MODEL, NodeType.EVALUATE, NodeType.VISUALIZE]:
                if len(upstream_ids) > 1:
                    self._add_warning(
                        f"Node has multiple inputs, only the first will be used",
                        node_id=node_id,
                    )

    def _validate_node_configs(self):
        """Validate individual node configurations."""
        for node_id, node in self.nodes.items():
            config = node.config

            if node.type == NodeType.DATASET:
                self._validate_dataset_config(node_id, config)
            elif node.type == NodeType.PREPROCESSING:
                self._validate_preprocessing_config(node_id, config)
            elif node.type == NodeType.SPLIT:
                self._validate_split_config(node_id, config)
            elif node.type == NodeType.MODEL:
                self._validate_model_config(node_id, config)
            elif node.type == NodeType.EVALUATE:
                self._validate_evaluate_config(node_id, config)
            elif node.type == NodeType.VISUALIZE:
                self._validate_visualize_config(node_id, config)

    def _validate_dataset_config(self, node_id: str, config: Dict):
        """Validate dataset node configuration."""
        dataset_id = config.get("dataset_id") or config.get("datasetId")
        if not dataset_id:
            self._add_error(
                "No dataset selected",
                node_id=node_id,
                field="dataset_id",
            )

        problem_type = config.get("problem_type") or config.get("problemType")
        target_column = config.get("target_column") or config.get("targetColumn")

        # Supervised learning requires target column
        if problem_type in ["classification", "regression"] and not target_column:
            self._add_error(
                f"Target column required for {problem_type}",
                node_id=node_id,
                field="target_column",
            )

    def _validate_preprocessing_config(self, node_id: str, config: Dict):
        """Validate preprocessing node configuration."""
        operations = config.get("operations", [])

        if not operations:
            self._add_warning(
                "No preprocessing operations configured",
                node_id=node_id,
            )
            return

        # Validate each operation
        for i, op in enumerate(operations):
            op_type = op.get("type")
            if not op_type:
                self._add_error(
                    f"Operation {i + 1} has no type specified",
                    node_id=node_id,
                    field=f"operations[{i}].type",
                )
                continue

            # Check if operation type exists in registry
            if not get_preprocessing_method(op_type):
                self._add_error(
                    f"Unknown preprocessing operation: {op_type}",
                    node_id=node_id,
                    field=f"operations[{i}].type",
                )

    def _validate_split_config(self, node_id: str, config: Dict):
        """Validate train/test split configuration."""
        test_size = config.get("test_size") or config.get("testSize", 0.2)

        if not 0.1 <= test_size <= 0.5:
            self._add_error(
                "Test size must be between 10% and 50%",
                node_id=node_id,
                field="test_size",
            )

    def _validate_model_config(self, node_id: str, config: Dict):
        """Validate model node configuration."""
        algorithm = config.get("algorithm")
        if not algorithm:
            self._add_error(
                "No algorithm selected",
                node_id=node_id,
                field="algorithm",
            )
            return

        # Check if algorithm exists in plugin registry
        plugin = PluginRegistry.get_model(algorithm)
        if not plugin:
            self._add_error(
                f"Unknown algorithm: {algorithm}",
                node_id=node_id,
                field="algorithm",
            )
            return

        # Validate hyperparameters
        hyperparameters = config.get("hyperparameters", {})
        # TODO: Add hyperparameter validation based on plugin schema

        # Validate Optuna settings
        use_optuna = config.get("use_optuna") or config.get("useOptuna", False)
        if use_optuna:
            trials = config.get("optuna_trials") or config.get("optunaTrials", 50)
            if trials < 10:
                self._add_warning(
                    "Less than 10 Optuna trials may not find optimal hyperparameters",
                    node_id=node_id,
                    field="optuna_trials",
                )

    def _validate_evaluate_config(self, node_id: str, config: Dict):
        """Validate evaluate node configuration."""
        metrics = config.get("selected_metrics") or config.get("selectedMetrics", [])

        if not metrics:
            self._add_error(
                "No evaluation metrics selected",
                node_id=node_id,
                field="selected_metrics",
            )

    def _validate_visualize_config(self, node_id: str, config: Dict):
        """Validate visualize node configuration."""
        plots = config.get("selected_plots") or config.get("selectedPlots", [])

        if not plots:
            self._add_warning(
                "No visualizations selected",
                node_id=node_id,
                field="selected_plots",
            )

    def _check_cycles(self):
        """Check for cyclic dependencies in the graph."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self.outgoing[node_id]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    self._add_error("Workflow contains a cycle (circular dependency)")
                    return

    def get_execution_order(self) -> List[str]:
        """
        Get nodes in topological order for execution.

        Returns:
            List of node IDs in execution order
        """
        # Kahn's algorithm for topological sort
        in_degree = {node_id: len(self.incoming[node_id]) for node_id in self.nodes}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(node_id)

            for neighbor in self.outgoing[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result


def validate_workflow(
    nodes: List[WorkflowNode],
    edges: List[WorkflowEdge],
) -> WorkflowValidateResponse:
    """
    Validate a workflow.

    Args:
        nodes: List of workflow nodes
        edges: List of workflow edges

    Returns:
        Validation response with errors and warnings
    """
    validator = WorkflowValidator(nodes, edges)
    return validator.validate()


def get_execution_order(
    nodes: List[WorkflowNode],
    edges: List[WorkflowEdge],
) -> List[str]:
    """
    Get the execution order for workflow nodes.

    Args:
        nodes: List of workflow nodes
        edges: List of workflow edges

    Returns:
        List of node IDs in topological order
    """
    validator = WorkflowValidator(nodes, edges)
    return validator.get_execution_order()
