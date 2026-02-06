"""
Workflow Executor

Executes workflow nodes in topological order, passing data between nodes.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score

from app.plugins.base import ProblemType
from app.plugins.registry import PluginRegistry
from app.plugins.shared.evaluators import compute_metrics
from app.plugins.shared.visualizers import generate_plots
from app.plugins.preprocessing.registry import apply_preprocessing

from .schemas import (
    NodeType,
    NodeStatus,
    WorkflowStatus,
    WorkflowNode,
    WorkflowEdge,
    NodeExecutionStatus,
    MetricResult,
    PlotResult,
    WorkflowResults,
)
from .validator import WorkflowValidator

logger = logging.getLogger(__name__)


class NodeExecutionContext:
    """Context passed between nodes during execution."""

    def __init__(self):
        # Data at each stage
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.X_train: Optional[np.ndarray] = None
        self.X_test: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None
        self.y_test: Optional[np.ndarray] = None

        # Model and predictions
        self.model: Optional[Any] = None
        self.predictions: Optional[np.ndarray] = None
        self.probabilities: Optional[np.ndarray] = None

        # Metadata
        self.problem_type: Optional[ProblemType] = None
        self.target_column: Optional[str] = None
        self.feature_names: List[str] = []
        self.algorithm: Optional[str] = None
        self.algorithm_name: Optional[str] = None

        # Results
        self.metrics: List[MetricResult] = []
        self.plots: List[PlotResult] = []

        # Timing
        self.training_time: float = 0.0

        # Hyperparameters used for training
        self.hyperparameters: Dict[str, Any] = {}


class WorkflowExecutor:
    """
    Executes a validated workflow.

    The executor:
    1. Sorts nodes topologically
    2. Executes each node in order
    3. Passes data between connected nodes
    4. Publishes status updates
    5. Stores results
    """

    def __init__(
        self,
        nodes: List[WorkflowNode],
        edges: List[WorkflowEdge],
        job_id: str,
        status_callback: Optional[Callable[[str, NodeStatus, Optional[str]], None]] = None,
    ):
        self.nodes = {n.id: n for n in nodes}
        self.edges = edges
        self.job_id = job_id
        self.status_callback = status_callback

        # Build graph
        self.validator = WorkflowValidator(nodes, edges)
        self.execution_order = self.validator.get_execution_order()

        # Execution state
        self.context = NodeExecutionContext()
        self.node_statuses: Dict[str, NodeExecutionStatus] = {}
        self.node_outputs: Dict[str, Any] = {}

        # Initialize statuses
        for node_id in self.nodes:
            self.node_statuses[node_id] = NodeExecutionStatus(
                node_id=node_id,
                status=NodeStatus.PENDING,
            )

    def _update_node_status(
        self,
        node_id: str,
        status: NodeStatus,
        error: Optional[str] = None,
        progress: Optional[float] = None,
    ):
        """Update a node's status and notify callback."""
        now = datetime.utcnow().isoformat()

        node_status = self.node_statuses[node_id]
        node_status.status = status
        node_status.error = error
        node_status.progress = progress

        if status == NodeStatus.RUNNING:
            node_status.started_at = now
        elif status in [NodeStatus.COMPLETED, NodeStatus.FAILED]:
            node_status.completed_at = now

        if self.status_callback:
            self.status_callback(node_id, status, error)

    def execute(self) -> WorkflowResults:
        """
        Execute the workflow.

        Returns:
            WorkflowResults with all outputs
        """
        logger.info(f"Starting workflow execution: {self.job_id}")
        start_time = time.time()

        try:
            for node_id in self.execution_order:
                node = self.nodes[node_id]
                self._update_node_status(node_id, NodeStatus.RUNNING)

                try:
                    self._execute_node(node)
                    self._update_node_status(node_id, NodeStatus.COMPLETED)
                except Exception as e:
                    logger.error(f"Node {node_id} failed: {e}")
                    self._update_node_status(node_id, NodeStatus.FAILED, str(e))
                    raise

            total_time = time.time() - start_time
            logger.info(f"Workflow completed in {total_time:.2f}s")

            return self._build_results(total_time)

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    def _execute_node(self, node: WorkflowNode):
        """Execute a single node."""
        logger.info(f"Executing node: {node.id} ({node.type.value})")

        if node.type == NodeType.DATASET:
            self._execute_dataset_node(node)
        elif node.type == NodeType.PREPROCESSING:
            self._execute_preprocessing_node(node)
        elif node.type == NodeType.SPLIT:
            self._execute_split_node(node)
        elif node.type == NodeType.MODEL:
            self._execute_model_node(node)
        elif node.type == NodeType.EVALUATE:
            self._execute_evaluate_node(node)
        elif node.type == NodeType.VISUALIZE:
            self._execute_visualize_node(node)

    def _execute_dataset_node(self, node: WorkflowNode):
        """Load and prepare dataset."""
        config = node.config
        dataset_id = config.get("dataset_id") or config.get("datasetId")
        is_sample = config.get("is_sample") or config.get("isSample", False)

        # Get problem type and target column
        problem_type_str = config.get("problem_type") or config.get("problemType")
        self.context.target_column = config.get("target_column") or config.get("targetColumn")

        if problem_type_str:
            self.context.problem_type = ProblemType(problem_type_str)

        # Load dataset
        if is_sample:
            # Load from sample datasets
            self.context.raw_data = self._load_sample_dataset(dataset_id)
        else:
            # Load from user's uploaded datasets
            self.context.raw_data = self._load_user_dataset(dataset_id)

        logger.info(f"Loaded dataset with shape: {self.context.raw_data.shape}")

    def _load_sample_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Load a sample dataset using the sample dataset service."""
        from app.services.sample_datasets import sample_dataset_service
        
        # Normalize the dataset ID (handle frontend prefixes like "sample-iris" -> "iris")
        normalized_id = dataset_id
        if dataset_id.startswith("sample-"):
            normalized_id = dataset_id[7:]  # Remove "sample-" prefix
        
        return sample_dataset_service.load_dataset(normalized_id)

    def _load_user_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Load a user's uploaded dataset."""
        # This would load from R2/database
        # For now, raise an error - implement when storage is set up
        raise NotImplementedError("User dataset loading not yet implemented")

    def _execute_preprocessing_node(self, node: WorkflowNode):
        """Apply preprocessing operations."""
        config = node.config
        operations = config.get("operations", [])

        if self.context.raw_data is None:
            raise ValueError("No data available for preprocessing")

        # Start with raw data
        df = self.context.raw_data.copy()

        # Apply each operation
        for op in operations:
            op_type = op.get("type")
            params = op.get("params", {})

            try:
                df = apply_preprocessing(
                    df,
                    method_slug=op_type,
                    parameters=params,
                    target_column=self.context.target_column,
                )
            except ValueError as e:
                logger.warning(f"Preprocessing operation failed: {e}")

        self.context.processed_data = df
        logger.info(f"Preprocessing complete. Shape: {df.shape}")

    def _execute_split_node(self, node: WorkflowNode):
        """Split data into train/test sets."""
        config = node.config
        test_size = config.get("test_size") or config.get("testSize", 0.2)
        stratify = config.get("stratify", False)
        shuffle = config.get("shuffle", True)
        random_seed = config.get("random_seed") or config.get("randomSeed", 42)

        # Use processed data if available, otherwise raw data
        df = self.context.processed_data if self.context.processed_data is not None else self.context.raw_data

        if df is None:
            raise ValueError("No data available for splitting")

        # Separate features and target
        if self.context.target_column and self.context.target_column in df.columns:
            X = df.drop(columns=[self.context.target_column])
            y = df[self.context.target_column]
        else:
            # Unsupervised: no target
            X = df
            y = None

        # Store feature names
        self.context.feature_names = list(X.columns)

        # Convert to numpy
        X = X.values

        # Split
        if y is not None:
            y = y.values
            stratify_param = y if (stratify and self.context.problem_type == ProblemType.CLASSIFICATION) else None

            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                shuffle=shuffle,
                random_state=random_seed,
                stratify=stratify_param,
            )
            self.context.y_train = y_train
            self.context.y_test = y_test
        else:
            X_train, X_test = train_test_split(
                X,
                test_size=test_size,
                shuffle=shuffle,
                random_state=random_seed,
            )

        self.context.X_train = X_train
        self.context.X_test = X_test

        logger.info(f"Split complete. Train: {len(X_train)}, Test: {len(X_test)}")

    def _execute_model_node(self, node: WorkflowNode):
        """Train the model."""
        config = node.config
        algorithm = config.get("algorithm")
        hyperparameters = config.get("hyperparameters", {})
        use_cv = config.get("use_cross_validation") or config.get("useCrossValidation", False)
        cv_folds = config.get("cv_folds") or config.get("cvFolds", 5)
        use_optuna = config.get("use_optuna") or config.get("useOptuna", False)

        # Get plugin
        plugin = PluginRegistry.get_model(algorithm)
        if not plugin:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        self.context.algorithm = algorithm
        self.context.algorithm_name = plugin.name
        self.context.hyperparameters = hyperparameters  # Store hyperparameters for results

        # Train
        logger.info(f"Training {plugin.name}...")
        start_time = time.time()

        if use_optuna:
            # Hyperparameter tuning with Optuna
            model = self._train_with_optuna(plugin, config)
        elif use_cv:
            # Cross-validation
            model, cv_scores = self._train_with_cv(plugin, hyperparameters, cv_folds)
            logger.info(f"CV scores: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        else:
            # Simple training
            model = plugin.train(
                self.context.X_train,
                self.context.y_train,
                hyperparameters,
                self.context.problem_type,
            )

        self.context.training_time = time.time() - start_time
        self.context.model = model

        # Make predictions
        self.context.predictions = plugin.predict(model, self.context.X_test)
        self.context.probabilities = plugin.predict_proba(model, self.context.X_test)

        logger.info(f"Training complete in {self.context.training_time:.2f}s")

    def _train_with_cv(self, plugin, hyperparameters: Dict, cv_folds: int):
        """Train with cross-validation."""
        from sklearn.base import clone

        # Train model
        model = plugin.train(
            self.context.X_train,
            self.context.y_train,
            hyperparameters,
            self.context.problem_type,
        )

        # Calculate CV scores
        scoring = "accuracy" if self.context.problem_type == ProblemType.CLASSIFICATION else "r2"
        cv_scores = cross_val_score(model, self.context.X_train, self.context.y_train, cv=cv_folds, scoring=scoring)

        return model, cv_scores

    def _train_with_optuna(self, plugin, config: Dict):
        """Train with Optuna hyperparameter optimization."""
        # This is a simplified version - full implementation would use Optuna
        # For now, just train with default hyperparameters
        logger.warning("Optuna optimization not fully implemented, using defaults")
        hyperparameters = config.get("hyperparameters", {})
        return plugin.train(
            self.context.X_train,
            self.context.y_train,
            hyperparameters,
            self.context.problem_type,
        )

    def _execute_evaluate_node(self, node: WorkflowNode):
        """Calculate evaluation metrics."""
        config = node.config
        selected_metrics = config.get("selected_metrics") or config.get("selectedMetrics", [])

        if self.context.model is None or self.context.predictions is None:
            raise ValueError("No model or predictions available for evaluation")

        # Evaluate
        results = compute_metrics(
            metric_keys=selected_metrics,
            y_true=self.context.y_test,
            y_pred=self.context.predictions,
            y_pred_proba=self.context.probabilities,
        )

        # Convert to MetricResult objects
        for key, value in results.items():
            self.context.metrics.append(MetricResult(
                key=key,
                name=key.replace("_", " ").title(),
                value=float(value) if isinstance(value, (int, float, np.number)) else 0.0,
            ))

        logger.info(f"Evaluated {len(self.context.metrics)} metrics")

    def _execute_visualize_node(self, node: WorkflowNode):
        """Generate visualizations."""
        config = node.config
        selected_plots = config.get("selected_plots") or config.get("selectedPlots", [])

        if not selected_plots:
            logger.info("No plots selected, skipping visualization")
            return

        # Generate plots
        plot_results = generate_plots(
            plot_keys=selected_plots,
            model=self.context.model,
            X_train=self.context.X_train,
            X_test=self.context.X_test,
            y_train=self.context.y_train,
            y_test=self.context.y_test,
            y_pred=self.context.predictions,
            y_pred_proba=self.context.probabilities,
            feature_names=self.context.feature_names,
        )

        # Convert to PlotResult objects
        for plot in plot_results:
            # Skip plots with errors
            if "error" in plot:
                logger.warning(f"Plot {plot.get('key')} failed: {plot.get('error')}")
                continue
            # Store base64 image as data URL
            image_data = f"data:image/png;base64,{plot['image']}" if plot.get('image') else ""
            self.context.plots.append(PlotResult(
                key=plot.get("key", ""),
                name=plot.get("name", ""),
                url=image_data,
            ))

        logger.info(f"Generated {len(self.context.plots)} plots")

    def _build_results(self, total_time: float) -> WorkflowResults:
        """Build the final workflow results."""
        # Determine training mode
        training_mode = "single"
        # TODO: Track CV/Optuna mode
        
        # Save model if exists
        model_path = None
        if self.context.model is not None:
            try:
                import os
                import joblib
                
                # Create outputs directory if it doesn't exist
                # Use absolute path relative to project root
                # apps/api/app/workflows/executor.py -> ../../../..
                # We want to save to c:/Folders/AutoML Platform 2.0/outputs/models
                
                # Get project root from current file path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
                models_dir = os.path.join(project_root, "outputs", "models")
                os.makedirs(models_dir, exist_ok=True)
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"model_{self.job_id}_{timestamp}.joblib"
                full_path = os.path.join(models_dir, filename)
                
                # Save model
                joblib.dump(self.context.model, full_path)
                logger.info(f"Saved model to {full_path}")
                
                # Store relative path or absolute path - storing absolute for simplicity in this environment
                model_path = full_path
                
            except Exception as e:
                logger.error(f"Failed to save model: {e}")

        # Read model as base64 for transfer if path exists
        model_base64 = None
        if model_path and os.path.exists(model_path):
            try:
                import base64
                with open(model_path, "rb") as f:
                    model_base64 = base64.b64encode(f.read()).decode("utf-8")
            except Exception as e:
                logger.error(f"Failed to encode model: {e}")

        return WorkflowResults(
            algorithm=self.context.algorithm or "unknown",
            algorithm_name=self.context.algorithm_name or "Unknown",
            problem_type=self.context.problem_type.value if self.context.problem_type else "unknown",
            training_mode=training_mode,
            training_time_seconds=self.context.training_time,
            hyperparameters=self.context.hyperparameters,
            metrics=self.context.metrics,
            plots=self.context.plots,
            train_samples=len(self.context.X_train) if self.context.X_train is not None else 0,
            test_samples=len(self.context.X_test) if self.context.X_test is not None else 0,
            features_count=len(self.context.feature_names),
            credits_used=0,  # Credits system removed
            model_path=model_path,
            model_base64=model_base64,
        )



def execute_workflow(
    nodes: List[WorkflowNode],
    edges: List[WorkflowEdge],
    job_id: Optional[str] = None,
    status_callback: Optional[Callable] = None,
) -> WorkflowResults:
    """
    Execute a workflow.

    Args:
        nodes: List of workflow nodes
        edges: List of workflow edges
        job_id: Optional job ID (generated if not provided)
        status_callback: Optional callback for status updates

    Returns:
        WorkflowResults with all outputs
    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    executor = WorkflowExecutor(nodes, edges, job_id, status_callback)
    return executor.execute()
