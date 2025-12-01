"""
Tests for Job Execution Task
"""

import os
import sys
import uuid
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

import pytest
import polars as pl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add project paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from packages.database.base import Base
from packages.database.models.job import Job
from packages.database.models.job_node import JobNode
from packages.database.models.workflow_snapshot import WorkflowSnapshot
from packages.database.models.user import User
from packages.database.models.enums import JobStatus, NodeStatus, NodeType, UserTier


# Test database
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        tier=UserTier.FREE,
        credit_balance=1000,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def simple_workflow_graph():
    """Simple workflow with dataset + preprocess + model."""
    return {
        "nodes": [
            {
                "id": "dataset_node",
                "type": "dataset",
                "data": {
                    "dataset_version_id": str(uuid.uuid4())
                }
            },
            {
                "id": "preprocess_node",
                "type": "preprocess",
                "data": {
                    "operation": "missing_value_imputation",
                    "strategy": "mean"
                }
            },
            {
                "id": "model_node",
                "type": "model",
                "data": {
                    "algorithm": "logistic_regression",
                    "target_column": "target",
                    "test_split": 0.2
                }
            }
        ],
        "edges": [
            {"source": "dataset_node", "target": "preprocess_node"},
            {"source": "preprocess_node", "target": "model_node"}
        ]
    }


@pytest.fixture
def test_workflow_snapshot(db_session, test_user, simple_workflow_graph):
    """Create test workflow snapshot."""
    snapshot = WorkflowSnapshot(
        workflow_id=uuid.uuid4(),
        user_id=test_user.id,
        graph_json=simple_workflow_graph,
    )
    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)
    return snapshot


@pytest.fixture
def test_job(db_session, test_user, test_workflow_snapshot):
    """Create test job."""
    job = Job(
        user_id=test_user.id,
        workflow_snapshot_id=test_workflow_snapshot.id,
        status=JobStatus.PENDING,
        credits_cost=50,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


class TestExecutionOrder:
    """Test workflow execution order logic."""

    def test_build_execution_order_simple(self):
        """Test topological sort with simple linear workflow."""
        from worker.tasks.job_execution_task import build_execution_order

        nodes = [
            {"id": "node1", "type": "dataset"},
            {"id": "node2", "type": "preprocess"},
            {"id": "node3", "type": "model"},
        ]
        edges = [
            {"source": "node1", "target": "node2"},
            {"source": "node2", "target": "node3"},
        ]

        ordered = build_execution_order(nodes, edges)

        assert len(ordered) == 3
        assert ordered[0]["id"] == "node1"
        assert ordered[1]["id"] == "node2"
        assert ordered[2]["id"] == "node3"

    def test_build_execution_order_parallel(self):
        """Test topological sort with parallel branches."""
        from worker.tasks.job_execution_task import build_execution_order

        nodes = [
            {"id": "node1", "type": "dataset"},
            {"id": "node2a", "type": "preprocess"},
            {"id": "node2b", "type": "preprocess"},
            {"id": "node3", "type": "model"},
        ]
        edges = [
            {"source": "node1", "target": "node2a"},
            {"source": "node1", "target": "node2b"},
            {"source": "node2a", "target": "node3"},
            {"source": "node2b", "target": "node3"},
        ]

        ordered = build_execution_order(nodes, edges)

        assert len(ordered) == 4
        # node1 should be first
        assert ordered[0]["id"] == "node1"
        # node2a and node2b can be in any order
        middle_ids = {ordered[1]["id"], ordered[2]["id"]}
        assert middle_ids == {"node2a", "node2b"}
        # node3 should be last
        assert ordered[3]["id"] == "node3"


class TestWorkflowContext:
    """Test workflow context."""

    def test_workflow_context_initialization(self):
        """Test context initializes correctly."""
        from worker.tasks.job_execution_task import WorkflowContext

        context = WorkflowContext()

        assert context.data == {}
        assert context.current_dataframe is None
        assert context.train_df is None
        assert context.test_df is None
        assert context.target_column is None
        assert context.feature_columns == []
        assert context.trained_models == {}
        assert context.preprocessors == []


class TestHelperFunctions:
    """Test helper functions."""

    def test_split_train_test(self):
        """Test train/test split."""
        from worker.tasks.job_execution_task import split_train_test

        # Create sample dataframe
        df = pl.DataFrame({
            "feature1": list(range(100)),
            "feature2": list(range(100, 200)),
            "target": [0, 1] * 50,
        })

        train_df, test_df = split_train_test(df, test_size=0.2)

        assert len(train_df) == 80
        assert len(test_df) == 20
        assert len(train_df) + len(test_df) == len(df)

    def test_create_trainer(self):
        """Test trainer creation."""
        from worker.tasks.job_execution_task import create_trainer

        trainer = create_trainer(
            algorithm="logistic_regression",
            task_type="classification",
            node_data={"hyperparameters": {"max_iter": 100}}
        )

        assert trainer is not None
        assert trainer.name == "logistic_regression"

    def test_create_trainer_unknown_algorithm(self):
        """Test trainer creation with unknown algorithm."""
        from worker.tasks.job_execution_task import create_trainer
        from worker.errors import ProcessingError

        with pytest.raises(ProcessingError):
            create_trainer(
                algorithm="unknown_algorithm",
                task_type="classification",
                node_data={}
            )


class TestNodeExecution:
    """Test individual node execution functions."""

    @patch("worker.tasks.job_execution_task.create_job_node")
    def test_create_job_node(self, mock_create, db_session, test_job):
        """Test job node creation."""
        from worker.tasks.job_execution_task import create_job_node

        # Actually call the real function
        mock_create.side_effect = lambda **kwargs: create_job_node(**kwargs)

        job_node = create_job_node(
            db=db_session,
            job_id=test_job.id,
            node_id="test_node",
            node_type_str="dataset",
        )

        assert job_node is not None
        assert job_node.job_id == test_job.id
        assert job_node.node_id == "test_node"
        assert job_node.node_type == NodeType.DATASET
        assert job_node.status == NodeStatus.PENDING

    def test_execute_dataset_node(self, db_session, test_job):
        """Test dataset node execution."""
        from worker.tasks.job_execution_task import (
            execute_dataset_node,
            WorkflowContext,
        )
        from packages.database.models.dataset_version import DatasetVersion

        # Create mock dataset version
        version = DatasetVersion(
            id=uuid.uuid4(),
            dataset_id=uuid.uuid4(),
            user_id=test_job.user_id,
            version_number=1,
            r2_parquet_path="test/path.parquet",
            row_count=100,
            column_count=5,
        )
        db_session.add(version)
        db_session.commit()

        # Create job node
        job_node = JobNode(
            job_id=test_job.id,
            node_id="dataset_node",
            node_type=NodeType.DATASET,
            status=NodeStatus.PENDING,
        )
        db_session.add(job_node)
        db_session.commit()

        # Create sample dataframe
        df = pl.DataFrame({
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        })

        # Mock R2 service
        mock_r2 = Mock()

        # Mock file download
        def mock_download(r2_path, local_path):
            # Write a parquet file
            df.write_parquet(local_path)

        mock_r2.download_file_from_r2 = mock_download

        context = WorkflowContext()
        temp_files = []

        node_data = {"dataset_version_id": str(version.id)}

        execute_dataset_node(
            db=db_session,
            job_node=job_node,
            node_data=node_data,
            context=context,
            r2_service=mock_r2,
            temp_files=temp_files,
        )

        # Verify context updated
        assert context.current_dataframe is not None
        assert len(context.current_dataframe) == 3
        assert job_node.result_json is not None


class TestJobExecutionTask:
    """Test the main execute_job task."""

    @patch("worker.tasks.job_execution_task.SessionLocal")
    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"})
    def test_execute_job_already_completed(self, mock_session_class, db_session, test_job):
        """Test job that's already completed."""
        from worker.tasks.job_execution_task import execute_job

        # Set job as already completed
        test_job.status = JobStatus.COMPLETED
        db_session.commit()

        # Mock database session
        mock_session_class.return_value = db_session

        # Create mock task
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.r2_service = Mock()

        result = execute_job(mock_task, str(test_job.id))

        assert result["status"] == "already_completed"

    @patch("worker.tasks.job_execution_task.SessionLocal")
    def test_execute_job_not_found(self, mock_session_class, db_session):
        """Test job that doesn't exist."""
        from worker.tasks.job_execution_task import execute_job
        from worker.errors import ProcessingError

        mock_session_class.return_value = db_session

        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.r2_service = Mock()

        with pytest.raises(ProcessingError, match="not found"):
            execute_job(mock_task, str(uuid.uuid4()))


class TestEndToEndExecution:
    """Test end-to-end job execution (with heavy mocking)."""

    @patch("worker.tasks.job_execution_task.SessionLocal")
    @patch("worker.tasks.job_execution_task.execute_dataset_node")
    @patch("worker.tasks.job_execution_task.execute_preprocess_node")
    @patch("worker.tasks.job_execution_task.execute_model_node")
    def test_full_workflow_execution(
        self,
        mock_model,
        mock_preprocess,
        mock_dataset,
        mock_session_class,
        db_session,
        test_job,
        test_workflow_snapshot,
    ):
        """Test full workflow execution with mocked node functions."""
        from worker.tasks.job_execution_task import execute_job

        mock_session_class.return_value = db_session

        # Mock task
        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.r2_service = Mock()

        # Mock node execution to just mark as success
        def mock_node_success(*args, **kwargs):
            pass

        mock_dataset.side_effect = mock_node_success
        mock_preprocess.side_effect = mock_node_success
        mock_model.side_effect = mock_node_success
        mock_model.return_value = None

        result = execute_job(mock_task, str(test_job.id))

        # Verify job completed
        assert result["status"] == "completed"
        assert result["job_id"] == str(test_job.id)

        # Verify job status updated
        db_session.refresh(test_job)
        assert test_job.status == JobStatus.COMPLETED
        assert test_job.started_at is not None
        assert test_job.completed_at is not None

    @patch("worker.tasks.job_execution_task.SessionLocal")
    @patch("worker.tasks.job_execution_task.execute_dataset_node")
    def test_workflow_execution_with_failure(
        self,
        mock_dataset,
        mock_session_class,
        db_session,
        test_job,
    ):
        """Test workflow execution when a node fails."""
        from worker.tasks.job_execution_task import execute_job
        from worker.errors import ProcessingError

        mock_session_class.return_value = db_session

        mock_task = Mock()
        mock_task.request.id = "test-task-id"
        mock_task.r2_service = Mock()

        # Make dataset node fail
        mock_dataset.side_effect = ProcessingError("Dataset load failed")

        with pytest.raises(ProcessingError):
            execute_job(mock_task, str(test_job.id))

        # Verify job marked as failed
        db_session.refresh(test_job)
        assert test_job.status == JobStatus.FAILED
        assert test_job.error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
