"""
Workflow Schemas

Pydantic models for workflow execution request/response.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    """Base model that outputs camelCase in JSON responses."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,  # Use camelCase in JSON output
    )


# =============================================================================
# Enums
# =============================================================================

class NodeType(str, Enum):
    """Workflow node types."""
    DATASET = "dataset"
    PREPROCESSING = "preprocessing"
    SPLIT = "split"
    MODEL = "model"
    EVALUATE = "evaluate"
    VISUALIZE = "visualize"


class NodeStatus(str, Enum):
    """Node execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Node Configuration Schemas
# =============================================================================

class BaseNodeConfig(BaseModel):
    """Base configuration for all nodes."""
    pass


class DatasetNodeConfig(BaseNodeConfig):
    """Dataset node configuration."""
    dataset_id: str
    dataset_name: str
    is_sample: bool = False
    target_column: Optional[str] = None
    problem_type: Optional[Literal["classification", "regression", "clustering"]] = None


class PreprocessingOperation(BaseModel):
    """Single preprocessing operation."""
    type: str  # e.g., "fill_missing", "standard_scaler", "one_hot_encode"
    params: Dict[str, Any] = Field(default_factory=dict)
    columns: Optional[List[str]] = None  # If None, applies to all applicable columns


class PreprocessingNodeConfig(BaseNodeConfig):
    """Preprocessing node configuration."""
    operations: List[PreprocessingOperation] = Field(default_factory=list)


class SplitNodeConfig(BaseNodeConfig):
    """Train/Test split node configuration."""
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    stratify: bool = False
    shuffle: bool = True
    random_seed: int = 42


class ModelNodeConfig(BaseNodeConfig):
    """Model node configuration."""
    algorithm: str  # Plugin slug (e.g., "random_forest")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    use_cross_validation: bool = False
    cv_folds: int = Field(default=5, ge=2, le=10)
    use_optuna: bool = False
    optuna_trials: int = Field(default=50, ge=10, le=200)
    optuna_metric: str = "accuracy"


class EvaluateNodeConfig(BaseNodeConfig):
    """Evaluate node configuration."""
    selected_metrics: List[str] = Field(default_factory=list)
    show_confidence_intervals: bool = False
    compare_with_baseline: bool = False


class VisualizeNodeConfig(BaseNodeConfig):
    """Visualize node configuration."""
    selected_plots: List[str] = Field(default_factory=list)


# Union type for node configs
NodeConfig = Union[
    DatasetNodeConfig,
    PreprocessingNodeConfig,
    SplitNodeConfig,
    ModelNodeConfig,
    EvaluateNodeConfig,
    VisualizeNodeConfig,
]


# =============================================================================
# Workflow Graph Schemas
# =============================================================================

class WorkflowNode(BaseModel):
    """A node in the workflow graph."""
    id: str  # Unique node ID
    type: NodeType
    config: Dict[str, Any]  # Will be validated based on type
    position: Optional[Dict[str, float]] = None  # {x, y} for UI


class WorkflowEdge(BaseModel):
    """An edge connecting two nodes."""
    id: str  # Unique edge ID
    source: str  # Source node ID
    target: str  # Target node ID
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None


# =============================================================================
# Request/Response Schemas
# =============================================================================

class WorkflowValidateRequest(BaseModel):
    """Request to validate a workflow without executing."""
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]


class ValidationError(BaseModel):
    """A single validation error."""
    node_id: Optional[str] = None  # None for graph-level errors
    field: Optional[str] = None
    message: str
    severity: Literal["error", "warning"] = "error"


class WorkflowValidateResponse(BaseModel):
    """Response from workflow validation."""
    valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)


class WorkflowExecuteRequest(BaseModel):
    """Request to execute a workflow."""
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    # Optional execution settings
    dry_run: bool = False  # Validate only, don't execute
    priority: int = Field(default=0, ge=0, le=10)  # Higher = more priority


class WorkflowExecuteResponse(CamelCaseModel):
    """Response from workflow execution."""
    job_id: str
    status: WorkflowStatus
    message: str
    results: Optional[Dict[str, Any]] = None  # Results returned directly for sync/HF execution


class NodeExecutionStatus(CamelCaseModel):
    """Status of a single node's execution."""
    node_id: str
    status: NodeStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[float] = None  # 0-100


class WorkflowStatusResponse(CamelCaseModel):
    """Response for workflow status query."""
    job_id: str
    status: WorkflowStatus
    node_statuses: Dict[str, NodeExecutionStatus] = Field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


# =============================================================================
# Result Schemas
# =============================================================================

class MetricResult(CamelCaseModel):
    """Result of a single metric evaluation."""
    key: str
    name: str
    value: float
    confidence_interval: Optional[tuple[float, float]] = None


class PlotResult(CamelCaseModel):
    """Result of a plot generation."""
    key: str
    name: str
    url: str  # URL to the generated plot image
    thumbnail_url: Optional[str] = None


class WorkflowResults(CamelCaseModel):
    """Complete results from workflow execution."""
    # Model info
    algorithm: str
    algorithm_name: str
    problem_type: str

    # Training info
    training_mode: Literal["single", "cross_validation", "optuna"]
    training_time_seconds: float
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)

    # Evaluation results
    metrics: List[MetricResult] = Field(default_factory=list)

    # Visualization results
    plots: List[PlotResult] = Field(default_factory=list)

    # Model artifacts
    model_path: Optional[str] = None  # Path in object storage
    model_base64: Optional[str] = None  # Base64 encoded model content (for transfer)

    # Dataset info
    train_samples: int
    test_samples: int
    features_count: int

    # Cost
    credits_used: int


# =============================================================================
# WebSocket Message Schemas
# =============================================================================

class WSMessageType(str, Enum):
    """WebSocket message types."""
    STATUS_UPDATE = "status_update"
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    PROGRESS = "progress"
    LOG = "log"
    RESULT = "result"
    ERROR = "error"


class WSMessage(BaseModel):
    """WebSocket message structure."""
    type: WSMessageType
    job_id: str
    data: Dict[str, Any]
    timestamp: str
