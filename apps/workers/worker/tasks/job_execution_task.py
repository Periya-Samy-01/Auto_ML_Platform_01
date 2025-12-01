"""
Job Execution Task
Main Celery task for executing ML workflow jobs
"""

import os
import sys
import uuid
import tempfile
import traceback
import logging
import pickle
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import polars as pl
from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from worker.celery_app import celery_app
from worker.errors import ProcessingError

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration (from environment)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/automl_dev")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class JobExecutionTask(Task):
    """Custom task class with service initialization"""

    def __init__(self):
        self.r2_service = None

    def __call__(self, *args, **kwargs):
        """Initialize services on first call"""
        if not self.r2_service:
            from worker.services.r2_service import R2Service
            self.r2_service = R2Service()
        return super().__call__(*args, **kwargs)


@celery_app.task(
    bind=True,
    base=JobExecutionTask,
    name='worker.tasks.job_execution_task.execute_job',
    max_retries=1,
    default_retry_delay=300,  # 5 minutes
    acks_late=True,
    reject_on_worker_lost=True
)
def execute_job(self, job_id: str) -> Dict[str, Any]:
    """
    Execute a complete ML workflow job.

    This task:
    1. Loads the job and workflow snapshot from database
    2. Processes nodes in dependency order
    3. Executes: dataset load → preprocess → train → evaluate → save
    4. Updates job status and creates JobNode records for tracking
    5. Stores trained models in R2

    Args:
        job_id: Job UUID (as string)

    Returns:
        Execution results with trained models and metrics
    """
    logger.info(f"Starting job execution: {job_id}")

    # Create database session
    db = SessionLocal()
    temp_files = []  # Track temp files for cleanup

    try:
        # Import models (avoid circular imports)
        from packages.database.models.job import Job
        from packages.database.models.job_node import JobNode
        from packages.database.models.workflow_snapshot import WorkflowSnapshot
        from packages.database.models.dataset_version import DatasetVersion
        from packages.database.models.model import Model
        from packages.database.models.enums import JobStatus, NodeStatus, NodeType

        # 1. Load job from database
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()

        if not job:
            raise ProcessingError(f"Job {job_id} not found")

        # Check if already completed (idempotency)
        if job.status == JobStatus.COMPLETED:
            logger.info(f"Job {job_id} already completed")
            return {"status": "already_completed"}

        # Update job status to RUNNING
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.celery_task_id = self.request.id
        db.commit()

        logger.info(f"Job {job_id} status updated to RUNNING")

        # 2. Load workflow snapshot
        snapshot = db.query(WorkflowSnapshot).filter(
            WorkflowSnapshot.id == job.workflow_snapshot_id
        ).first()

        if not snapshot:
            raise ProcessingError(f"Workflow snapshot {job.workflow_snapshot_id} not found")

        workflow_graph = snapshot.graph_json
        nodes = workflow_graph.get("nodes", [])
        edges = workflow_graph.get("edges", [])

        logger.info(f"Loaded workflow with {len(nodes)} nodes and {len(edges)} edges")

        # 3. Build execution plan (topological sort)
        execution_order = build_execution_order(nodes, edges)
        logger.info(f"Execution order: {[node['id'] for node in execution_order]}")

        # 4. Execute nodes in order
        context = WorkflowContext()  # Shared state between nodes
        trained_models = []

        for node in execution_order:
            node_id = node["id"]
            node_type_str = node.get("type", "").lower()
            node_data = node.get("data", {})

            logger.info(f"Executing node: {node_id} (type: {node_type_str})")

            # Create JobNode record
            job_node = create_job_node(
                db=db,
                job_id=job.id,
                node_id=node_id,
                node_type_str=node_type_str,
            )

            try:
                # Execute based on node type
                if node_type_str == "dataset":
                    execute_dataset_node(
                        db=db,
                        job_node=job_node,
                        node_data=node_data,
                        context=context,
                        r2_service=self.r2_service,
                        temp_files=temp_files,
                    )

                elif node_type_str == "preprocess":
                    execute_preprocess_node(
                        db=db,
                        job_node=job_node,
                        node_data=node_data,
                        context=context,
                    )

                elif node_type_str == "model" or node_type_str == "train":
                    model = execute_model_node(
                        db=db,
                        job_node=job_node,
                        node_data=node_data,
                        context=context,
                        job=job,
                        r2_service=self.r2_service,
                        temp_files=temp_files,
                    )
                    if model:
                        trained_models.append(model)

                elif node_type_str == "evaluate" or node_type_str == "evaluation":
                    execute_evaluate_node(
                        db=db,
                        job_node=job_node,
                        node_data=node_data,
                        context=context,
                    )

                elif node_type_str == "visualize":
                    execute_visualize_node(
                        db=db,
                        job_node=job_node,
                        node_data=node_data,
                        context=context,
                    )

                elif node_type_str == "save":
                    execute_save_node(
                        db=db,
                        job_node=job_node,
                        node_data=node_data,
                        context=context,
                    )

                else:
                    logger.warning(f"Unknown node type: {node_type_str}")
                    job_node.status = NodeStatus.SKIPPED
                    db.commit()
                    continue

                # Mark node as completed
                job_node.status = NodeStatus.COMPLETED
                job_node.completed_at = datetime.utcnow()
                job_node.duration_seconds = int(
                    (job_node.completed_at - job_node.started_at).total_seconds()
                )
                db.commit()

                logger.info(f"Node {node_id} completed successfully")

            except Exception as node_error:
                # Mark node as failed
                job_node.status = NodeStatus.FAILED
                job_node.error_message = str(node_error)
                job_node.completed_at = datetime.utcnow()
                if job_node.started_at:
                    job_node.duration_seconds = int(
                        (job_node.completed_at - job_node.started_at).total_seconds()
                    )
                db.commit()

                logger.error(f"Node {node_id} failed: {str(node_error)}")

                # Fail entire job
                raise ProcessingError(f"Node {node_id} failed: {str(node_error)}") from node_error

        # 5. Job completed successfully
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.duration_seconds = int(
            (job.completed_at - job.started_at).total_seconds()
        )
        db.commit()

        logger.info(f"Job {job_id} completed successfully in {job.duration_seconds}s")

        return {
            "status": "completed",
            "job_id": str(job.id),
            "duration_seconds": job.duration_seconds,
            "trained_models": [str(model.id) for model in trained_models],
        }

    except Exception as e:
        # Log error
        logger.error(f"Failed to execute job {job_id}: {str(e)}")
        logger.error(traceback.format_exc())

        # Update job status to FAILED
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            if job.started_at:
                job.duration_seconds = int(
                    (job.completed_at - job.started_at).total_seconds()
                )
            db.commit()

        # Don't retry on most errors
        raise

    finally:
        # Clean up temp files
        import shutil
        for temp_path in temp_files:
            try:
                if os.path.exists(temp_path):
                    if os.path.isdir(temp_path):
                        shutil.rmtree(temp_path)
                    else:
                        os.remove(temp_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temp file {temp_path}: {cleanup_error}")

        # Close database session
        db.close()


class WorkflowContext:
    """
    Shared context between workflow nodes.
    Stores intermediate data (dataframes, models, etc.)
    """

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.current_dataframe: Optional[pl.DataFrame] = None
        self.train_df: Optional[pl.DataFrame] = None
        self.test_df: Optional[pl.DataFrame] = None
        self.target_column: Optional[str] = None
        self.feature_columns: List[str] = []
        self.trained_models: Dict[str, Any] = {}
        self.evaluation_results: Dict[str, Any] = {}
        self.preprocessors: List[Any] = []


def build_execution_order(nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
    """
    Build execution order using topological sort.

    Args:
        nodes: List of workflow nodes
        edges: List of workflow edges

    Returns:
        List of nodes in execution order
    """
    # Build adjacency list
    dependencies = {node["id"]: [] for node in nodes}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            dependencies[target].append(source)

    # Topological sort (Kahn's algorithm)
    in_degree = {node_id: len(deps) for node_id, deps in dependencies.items()}
    queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
    result = []

    while queue:
        current = queue.pop(0)
        result.append(current)

        # Find nodes that depend on current
        for node_id, deps in dependencies.items():
            if current in deps:
                in_degree[node_id] -= 1
                if in_degree[node_id] == 0:
                    queue.append(node_id)

    # Convert node IDs to full node objects
    node_map = {node["id"]: node for node in nodes}
    ordered_nodes = [node_map[node_id] for node_id in result if node_id in node_map]

    return ordered_nodes


def create_job_node(
    db: Session,
    job_id: uuid.UUID,
    node_id: str,
    node_type_str: str,
) -> Any:
    """Create a JobNode record for tracking"""
    from packages.database.models.job_node import JobNode
    from packages.database.models.enums import NodeStatus, NodeType

    # Map string to NodeType enum
    node_type_map = {
        "dataset": NodeType.DATASET,
        "preprocess": NodeType.PREPROCESS,
        "model": NodeType.MODEL,
        "train": NodeType.MODEL,
        "evaluate": NodeType.EVALUATE,
        "evaluation": NodeType.EVALUATE,
        "visualize": NodeType.VISUALIZE,
        "save": NodeType.SAVE,
    }

    node_type = node_type_map.get(node_type_str, NodeType.DATASET)

    job_node = JobNode(
        job_id=job_id,
        node_id=node_id,
        node_type=node_type,
        status=NodeStatus.PENDING,
        started_at=datetime.utcnow(),
    )

    db.add(job_node)
    db.commit()
    db.refresh(job_node)

    return job_node


# ============================================================
# Node Execution Functions
# ============================================================

def execute_dataset_node(
    db: Session,
    job_node: Any,
    node_data: Dict,
    context: WorkflowContext,
    r2_service: Any,
    temp_files: List[str],
) -> None:
    """Execute dataset loading node"""
    from packages.database.models.dataset_version import DatasetVersion

    logger.info(f"Loading dataset for node {job_node.node_id}")

    # Get dataset version ID from node data
    version_id = node_data.get("dataset_version_id") or node_data.get("version_id")

    if not version_id:
        raise ProcessingError("No dataset_version_id in node data")

    # Load dataset version
    version = db.query(DatasetVersion).filter(
        DatasetVersion.id == uuid.UUID(version_id)
    ).first()

    if not version:
        raise ProcessingError(f"Dataset version {version_id} not found")

    # Download Parquet file from R2
    temp_dir = tempfile.mkdtemp()
    temp_files.append(temp_dir)
    local_file = os.path.join(temp_dir, "data.parquet")

    logger.info(f"Downloading dataset from R2: {version.r2_parquet_path}")
    r2_service.download_file_from_r2(version.r2_parquet_path, local_file)

    # Load with Polars
    df = pl.read_parquet(local_file)
    logger.info(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Store in context
    context.current_dataframe = df
    context.data[job_node.node_id] = df

    # Update job node result
    job_node.result_json = {
        "row_count": df.shape[0],
        "column_count": df.shape[1],
        "columns": df.columns,
    }


def execute_preprocess_node(
    db: Session,
    job_node: Any,
    node_data: Dict,
    context: WorkflowContext,
) -> None:
    """Execute preprocessing node"""
    logger.info(f"Executing preprocessing for node {job_node.node_id}")

    if context.current_dataframe is None:
        raise ProcessingError("No dataframe in context for preprocessing")

    df = context.current_dataframe

    # Get preprocessing operation
    operation = node_data.get("operation") or node_data.get("preprocessor_type")

    if not operation:
        logger.warning("No preprocessing operation specified, skipping")
        return

    # Import preprocessors
    from worker.ml.preprocessors import (
        DuplicateRemovalPreprocessor,
        MissingValueImputationPreprocessor,
        FeatureScalingPreprocessor,
        OneHotEncodingPreprocessor,
        OrdinalLabelEncodingPreprocessor,
        DataTypeConversionPreprocessor,
        OutlierHandlingPreprocessor,
        DatetimeFeatureExtractionPreprocessor,
        DataContainer,
    )

    # Create preprocessor based on operation
    preprocessor = None

    if operation == "duplicate_removal":
        preprocessor = DuplicateRemovalPreprocessor()
    elif operation == "missing_value_imputation":
        strategy = node_data.get("strategy", "mean")
        preprocessor = MissingValueImputationPreprocessor(strategy=strategy)
    elif operation == "feature_scaling":
        method = node_data.get("method", "standard")
        preprocessor = FeatureScalingPreprocessor(method=method)
    elif operation == "one_hot_encoding":
        columns = node_data.get("columns", [])
        preprocessor = OneHotEncodingPreprocessor(columns=columns)
    elif operation == "ordinal_encoding":
        columns = node_data.get("columns", [])
        preprocessor = OrdinalLabelEncodingPreprocessor(columns=columns)
    elif operation == "outlier_handling":
        method = node_data.get("method", "iqr")
        preprocessor = OutlierHandlingPreprocessor(method=method)
    elif operation == "datetime_extraction":
        columns = node_data.get("columns", [])
        preprocessor = DatetimeFeatureExtractionPreprocessor(columns=columns)
    else:
        logger.warning(f"Unknown preprocessing operation: {operation}")
        return

    # Apply preprocessing
    if preprocessor:
        data_container = DataContainer(df=df)
        result_container = preprocessor.fit_transform(data_container)
        df = result_container.df

        # Store preprocessor for later use
        context.preprocessors.append(preprocessor)

        logger.info(f"Applied {operation}: {df.shape[0]} rows, {df.shape[1]} columns")

    # Update context
    context.current_dataframe = df
    context.data[job_node.node_id] = df

    # Update job node result
    job_node.result_json = {
        "operation": operation,
        "row_count": df.shape[0],
        "column_count": df.shape[1],
    }


def execute_model_node(
    db: Session,
    job_node: Any,
    node_data: Dict,
    context: WorkflowContext,
    job: Any,
    r2_service: Any,
    temp_files: List[str],
) -> Optional[Any]:
    """Execute model training node"""
    from packages.database.models.model import Model

    logger.info(f"Training model for node {job_node.node_id}")

    if context.current_dataframe is None:
        raise ProcessingError("No dataframe in context for model training")

    df = context.current_dataframe

    # Get training configuration
    target_column = node_data.get("target_column")
    algorithm = node_data.get("algorithm", "logistic_regression")
    task_type = node_data.get("task", "classification")
    test_split = node_data.get("test_split", 0.2)

    if not target_column:
        raise ProcessingError("No target_column specified for model training")

    # Split train/test
    train_df, test_df = split_train_test(df, test_split)
    context.train_df = train_df
    context.test_df = test_df
    context.target_column = target_column

    # Prepare X, y
    X_train = train_df.drop(target_column).to_pandas()
    y_train = train_df[target_column].to_pandas()
    X_test = test_df.drop(target_column).to_pandas()
    y_test = test_df[target_column].to_pandas()

    context.feature_columns = list(X_train.columns)

    logger.info(f"Train set: {len(X_train)} rows, Test set: {len(X_test)} rows")

    # Create trainer
    trainer = create_trainer(algorithm, task_type, node_data)

    # Train model
    logger.info(f"Training {algorithm} model...")
    trainer.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = trainer.predict(X_test)
    metrics = trainer.evaluate(X_test, y_test)

    logger.info(f"Model trained. Metrics: {metrics}")

    # Serialize model
    temp_dir = tempfile.mkdtemp()
    temp_files.append(temp_dir)
    model_file = os.path.join(temp_dir, "model.pkl")

    with open(model_file, 'wb') as f:
        pickle.dump(trainer, f)

    # Upload to R2
    r2_path = f"models/{job.user_id}/{job.id}/{job_node.id}.pkl"
    model_size = r2_service.upload_file_to_r2(
        model_file,
        r2_path,
        content_type="application/octet-stream"
    )

    logger.info(f"Model uploaded to R2: {r2_path} ({model_size} bytes)")

    # Create Model record
    model_record = Model(
        user_id=job.user_id,
        job_id=job.id,
        job_node_id=job_node.id,
        name=f"{algorithm}_{str(job_node.id)[:8]}",
        model_type=algorithm,
        s3_model_path=r2_path,
        model_size_bytes=model_size,
        hyperparameters_json=node_data.get("hyperparameters", {}),
        metrics_json=metrics,
        is_saved=True,
    )

    db.add(model_record)
    db.commit()
    db.refresh(model_record)

    # Store in context
    context.trained_models[job_node.node_id] = trainer

    # Update job node result
    job_node.result_json = {
        "algorithm": algorithm,
        "task": task_type,
        "metrics": metrics,
        "model_id": str(model_record.id),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }

    return model_record


def execute_evaluate_node(
    db: Session,
    job_node: Any,
    node_data: Dict,
    context: WorkflowContext,
) -> None:
    """Execute evaluation node"""
    logger.info(f"Evaluating model for node {job_node.node_id}")

    # Evaluation is already done in model node
    # This node can be used for custom evaluation logic

    job_node.result_json = {
        "message": "Evaluation performed in model training node"
    }


def execute_visualize_node(
    db: Session,
    job_node: Any,
    node_data: Dict,
    context: WorkflowContext,
) -> None:
    """Execute visualization node"""
    logger.info(f"Creating visualization for node {job_node.node_id}")

    # Visualization would be implemented here
    # For now, just mark as completed

    job_node.result_json = {
        "message": "Visualization node (placeholder)"
    }


def execute_save_node(
    db: Session,
    job_node: Any,
    node_data: Dict,
    context: WorkflowContext,
) -> None:
    """Execute save node"""
    logger.info(f"Saving artifacts for node {job_node.node_id}")

    # Models are already saved in model node
    # This node can be used for custom save logic

    job_node.result_json = {
        "message": "Models already saved in model training node"
    }


# ============================================================
# Helper Functions
# ============================================================

def split_train_test(
    df: pl.DataFrame,
    test_size: float = 0.2,
) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """Split dataframe into train and test sets"""
    n = len(df)
    test_n = int(n * test_size)
    train_n = n - test_n

    # Shuffle
    df_shuffled = df.sample(fraction=1.0, shuffle=True, seed=42)

    train_df = df_shuffled[:train_n]
    test_df = df_shuffled[train_n:]

    return train_df, test_df


def create_trainer(algorithm: str, task_type: str, node_data: Dict) -> Any:
    """Create trainer instance based on algorithm"""
    from worker.ml.trainers import (
        LogisticRegressionTrainer,
        NaiveBayesTrainer,
        KNNTrainer,
        DecisionTreeTrainer,
        RandomForestTrainer,
        XGBoostTrainer,
        LinearRegressionTrainer,
        KMeansTrainer,
        NeuralNetworkTrainer,
    )

    hyperparameters = node_data.get("hyperparameters", {})

    trainer_map = {
        "logistic_regression": LogisticRegressionTrainer,
        "naive_bayes": NaiveBayesTrainer,
        "knn": KNNTrainer,
        "decision_tree": DecisionTreeTrainer,
        "random_forest": RandomForestTrainer,
        "xgboost": XGBoostTrainer,
        "linear_regression": LinearRegressionTrainer,
        "kmeans": KMeansTrainer,
        "neural_network": NeuralNetworkTrainer,
    }

    trainer_class = trainer_map.get(algorithm)

    if not trainer_class:
        raise ProcessingError(f"Unknown algorithm: {algorithm}")

    # Create trainer with hyperparameters
    trainer = trainer_class(
        name=algorithm,
        task=task_type,
        **hyperparameters
    )

    return trainer
