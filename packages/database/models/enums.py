"""
Enum types matching PostgreSQL ENUM definitions
"""

import enum


class UserTier(str, enum.Enum):
    """User subscription tier"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class FileFormat(str, enum.Enum):
    """Supported dataset file formats"""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    EXCEL = "excel"
    UNKNOWN = "unknown"


class ProblemType(str, enum.Enum):
    """Machine learning problem type"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    OTHER = "other"


class JobStatus(str, enum.Enum):
    """Job execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class NodeType(str, enum.Enum):
    """Workflow node types"""
    DATASET = "dataset"
    PREPROCESS = "preprocess"
    MODEL = "model"
    VISUALIZE = "visualize"
    SAVE = "save"


class NodeStatus(str, enum.Enum):
    """Individual node execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TutorialDifficulty(str, enum.Enum):
    """Tutorial difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProcessingStatus(str, enum.Enum):
    """Dataset version processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OAuthProvider(str, enum.Enum):
    """OAuth authentication providers"""
    GOOGLE = "google"
    GITHUB = "github"
    EMAIL = "email"  # For future email/password auth
