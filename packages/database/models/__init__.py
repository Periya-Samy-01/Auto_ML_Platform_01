"""
SQLAlchemy Models for AutoML Platform
All models matching the production PostgreSQL schema
"""

from .enums import (
    UserTier,
    FileFormat,
    ProblemType,
    JobStatus,
    NodeType,
    NodeStatus,
    TutorialDifficulty,
    ProcessingStatus,
    OAuthProvider,
)
from .user import User
from .dataset import Dataset
from .dataset_version import DatasetVersion
from .dataset_profile import DatasetProfile
from .ingestion_job import IngestionJob
from .workflow import Workflow
from .workflow_snapshot import WorkflowSnapshot
from .job import Job
from .job_node import JobNode
from .model import Model
from .experiment import Experiment
from .experiment_run import ExperimentRun
from .tutorial import Tutorial
from .user_tutorial_progress import UserTutorialProgress

__all__ = [
    # Enums
    "UserTier",
    "FileFormat",
    "ProblemType",
    "JobStatus",
    "NodeType",
    "NodeStatus",
    "TutorialDifficulty",
    "ProcessingStatus",
    "OAuthProvider",
    # Models
    "User",
    "Dataset",
    "DatasetVersion",
    "DatasetProfile",
    "IngestionJob",
    "Workflow",
    "WorkflowSnapshot",
    "Job",
    "JobNode",
    "Model",
    "Experiment",
    "ExperimentRun",
    "Tutorial",
    "UserTutorialProgress",
]
