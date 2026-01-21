"""
Tests for Job API endpoints
"""

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from packages.database.models.user import User
from packages.database.models.workflow import Workflow
from packages.database.models.workflow_snapshot import WorkflowSnapshot
from packages.database.models.job import Job
from packages.database.models.job_node import JobNode
from packages.database.models.credit_transaction import CreditTransaction
from packages.database.models.enums import (
    JobStatus,
    NodeStatus,
    NodeType,
    TransactionType,
    UserTier,
)


@pytest.fixture
def test_workflow(db_session: Session, test_user: User):
    """Create a test workflow."""
    workflow = Workflow(
        user_id=test_user.id,
        name="Test Workflow",
        description="A test workflow",
    )
    db_session.add(workflow)
    db_session.commit()
    db_session.refresh(workflow)
    return workflow


@pytest.fixture
def test_workflow_snapshot(db_session: Session, test_user: User, test_workflow: Workflow):
    """Create a test workflow snapshot with a simple graph."""
    graph_json = {
        "nodes": [
            {
                "id": "node1",
                "type": "dataset",
                "data": {
                    "dataset_version_id": str(uuid.uuid4())
                }
            },
            {
                "id": "node2",
                "type": "preprocess",
                "data": {
                    "operation": "missing_value_imputation"
                }
            },
            {
                "id": "node3",
                "type": "model",
                "data": {
                    "algorithm": "logistic_regression",
                    "target_column": "target"
                }
            }
        ],
        "edges": [
            {"source": "node1", "target": "node2"},
            {"source": "node2", "target": "node3"}
        ]
    }

    snapshot = WorkflowSnapshot(
        workflow_id=test_workflow.id,
        user_id=test_user.id,
        graph_json=graph_json,
        snapshot_name="Test Snapshot",
    )
    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)
    return snapshot


class TestJobCreation:
    """Test job creation endpoint."""

    @patch("app.jobs.service.queue_job_execution")
    def test_create_job_success(
        self,
        mock_queue,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test successful job creation."""
        # Add initial credits
        transaction = CreditTransaction(
            user_id=test_user.id,
            amount=500,
            balance_after=500,
            transaction_type=TransactionType.PURCHASE,
            description="Initial credits",
        )
        db_session.add(transaction)
        db_session.commit()

        response = authenticated_client.post(
            "/api/jobs",
            json={
                "workflow_snapshot_id": str(test_workflow_snapshot.id),
                "priority": 5,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        assert data["status"] == "queued" or data["status"] == "pending"
        assert data["credits_cost"] > 0
        assert mock_queue.called

    def test_create_job_insufficient_credits(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test job creation with insufficient credits."""
        # User has 0 credits by default
        response = authenticated_client.post(
            "/api/jobs",
            json={
                "workflow_snapshot_id": str(test_workflow_snapshot.id),
            },
        )

        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
        assert "Insufficient credits" in response.json()["detail"]

    def test_create_job_invalid_snapshot(
        self,
        authenticated_client,
        test_user,
    ):
        """Test job creation with invalid snapshot ID."""
        response = authenticated_client.post(
            "/api/jobs",
            json={
                "workflow_snapshot_id": str(uuid.uuid4()),  # Random UUID
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJobListing:
    """Test job listing endpoint."""

    def test_list_jobs_empty(
        self,
        authenticated_client,
        test_user,
    ):
        """Test listing jobs when none exist."""
        response = authenticated_client.get("/api/jobs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["has_more"] is False

    def test_list_jobs_with_data(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test listing jobs with existing data."""
        # Create test jobs
        for i in range(3):
            job = Job(
                user_id=test_user.id,
                workflow_snapshot_id=test_workflow_snapshot.id,
                status=JobStatus.COMPLETED if i % 2 == 0 else JobStatus.RUNNING,
                credits_cost=100 + i * 10,
            )
            db_session.add(job)
        db_session.commit()

        response = authenticated_client.get("/api/jobs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_jobs_with_filter(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test listing jobs with status filter."""
        # Create jobs with different statuses
        job1 = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.COMPLETED,
            credits_cost=100,
        )
        job2 = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.RUNNING,
            credits_cost=100,
        )
        db_session.add_all([job1, job2])
        db_session.commit()

        response = authenticated_client.get("/api/jobs?status_filter=completed")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "completed"

    def test_list_jobs_pagination(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test job listing pagination."""
        # Create 10 jobs
        for i in range(10):
            job = Job(
                user_id=test_user.id,
                workflow_snapshot_id=test_workflow_snapshot.id,
                status=JobStatus.COMPLETED,
                credits_cost=100,
            )
            db_session.add(job)
        db_session.commit()

        # Page 1
        response = authenticated_client.get("/api/jobs?page=1&page_size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 10
        assert len(data["items"]) == 5
        assert data["has_more"] is True

        # Page 2
        response = authenticated_client.get("/api/jobs?page=2&page_size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 5
        assert data["has_more"] is False


class TestJobDetails:
    """Test job details endpoint."""

    def test_get_job_success(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test getting job details."""
        job = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.COMPLETED,
            credits_cost=150,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_seconds=120,
        )
        db_session.add(job)
        db_session.commit()

        response = authenticated_client.get(f"/api/jobs/{job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(job.id)
        assert data["status"] == "completed"
        assert data["credits_cost"] == 150
        assert data["duration_seconds"] == 120

    def test_get_job_not_found(
        self,
        authenticated_client,
        test_user,
    ):
        """Test getting non-existent job."""
        response = authenticated_client.get(f"/api/jobs/{uuid.uuid4()}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJobCancellation:
    """Test job cancellation endpoint."""

    @patch("app.jobs.service.revoke_celery_task")
    def test_cancel_job_success(
        self,
        mock_revoke,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test successful job cancellation."""
        # Create running job
        job = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.RUNNING,
            credits_cost=100,
            celery_task_id="test-task-id",
        )
        db_session.add(job)
        db_session.commit()

        response = authenticated_client.post(f"/api/jobs/{job.id}/cancel")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job"]["status"] == "cancelled"
        assert data["refund_amount"] >= 0
        assert data["refund_percentage"] > 0
        assert mock_revoke.called

    def test_cancel_completed_job(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test cancelling already completed job."""
        job = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.COMPLETED,
            credits_cost=100,
        )
        db_session.add(job)
        db_session.commit()

        response = authenticated_client.post(f"/api/jobs/{job.id}/cancel")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestJobRetry:
    """Test job retry endpoint."""

    @patch("app.jobs.service.queue_job_execution")
    def test_retry_job_success(
        self,
        mock_queue,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test successful job retry."""
        # Add credits
        transaction = CreditTransaction(
            user_id=test_user.id,
            amount=500,
            balance_after=500,
            transaction_type=TransactionType.PURCHASE,
        )
        db_session.add(transaction)

        # Create failed job
        failed_job = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.FAILED,
            credits_cost=100,
            error_message="Test error",
        )
        db_session.add(failed_job)
        db_session.commit()

        response = authenticated_client.post(f"/api/jobs/{failed_job.id}/retry")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["original_job_id"] == str(failed_job.id)
        assert data["new_job"]["id"] != str(failed_job.id)
        assert mock_queue.called

    def test_retry_running_job(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test retrying a non-failed job."""
        job = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.RUNNING,
            credits_cost=100,
        )
        db_session.add(job)
        db_session.commit()

        response = authenticated_client.post(f"/api/jobs/{job.id}/retry")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestJobLogs:
    """Test job logs endpoint."""

    def test_get_job_logs(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test getting job execution logs."""
        # Create job
        job = Job(
            user_id=test_user.id,
            workflow_snapshot_id=test_workflow_snapshot.id,
            status=JobStatus.COMPLETED,
            credits_cost=100,
        )
        db_session.add(job)
        db_session.flush()

        # Create job nodes
        node1 = JobNode(
            job_id=job.id,
            node_id="node1",
            node_type=NodeType.DATASET,
            status=NodeStatus.SUCCESS,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_seconds=10,
        )
        node2 = JobNode(
            job_id=job.id,
            node_id="node2",
            node_type=NodeType.MODEL,
            status=NodeStatus.SUCCESS,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_seconds=60,
        )
        db_session.add_all([node1, node2])
        db_session.commit()

        response = authenticated_client.get(f"/api/jobs/{job.id}/logs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == str(job.id)
        assert len(data["nodes"]) == 2
        assert data["overall_status"] == "completed"


class TestJobStats:
    """Test job statistics endpoint."""

    def test_get_job_stats(
        self,
        authenticated_client,
        db_session,
        test_user,
        test_workflow_snapshot,
    ):
        """Test getting job statistics."""
        # Create various jobs
        jobs_data = [
            (JobStatus.COMPLETED, 100),
            (JobStatus.COMPLETED, 150),
            (JobStatus.FAILED, 80),
            (JobStatus.RUNNING, 120),
        ]

        for job_status, cost in jobs_data:
            job = Job(
                user_id=test_user.id,
                workflow_snapshot_id=test_workflow_snapshot.id,
                status=job_status,
                credits_cost=cost,
                duration_seconds=60 if job_status == JobStatus.COMPLETED else None,
            )
            db_session.add(job)
        db_session.commit()

        response = authenticated_client.get("/api/jobs/stats/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_jobs"] == 4
        assert data["completed_jobs"] == 2
        assert data["failed_jobs"] == 1
        assert data["running_jobs"] == 1
        assert data["total_credits_spent"] > 0
        assert data["success_rate"] is not None


class TestCostCalculation:
    """Test cost calculation logic."""

    def test_simple_workflow_cost(self):
        """Test cost calculation for simple workflow."""
        from app.jobs.cost_calculator import calculate_job_cost

        workflow = {
            "nodes": [
                {"type": "dataset", "data": {}},
                {"type": "preprocess", "data": {}},
                {"type": "model", "data": {"algorithms": ["logistic_regression"]}},
            ]
        }

        cost = calculate_job_cost(workflow)
        # BASE (10) + DATASET (0) + PREPROCESS (5) + MODEL (20 + 10) = 45
        assert cost == 45

    def test_complex_workflow_cost(self):
        """Test cost calculation for complex workflow."""
        from app.jobs.cost_calculator import calculate_job_cost

        workflow = {
            "nodes": [
                {"type": "dataset", "data": {}},
                {"type": "preprocess", "data": {}},
                {"type": "preprocess", "data": {}},
                {
                    "type": "model",
                    "data": {
                        "algorithms": ["random_forest", "xgboost", "logistic_regression"],
                        "hpo_enabled": True,
                    }
                },
                {"type": "evaluation", "data": {}},
            ]
        }

        cost = calculate_job_cost(workflow)
        # BASE (10) + DATASET (0) + PREPROCESS (5) + PREPROCESS (5) +
        # MODEL (20 + 10 HPO + 30 for 3 algos) + EVAL (5) = 85
        assert cost == 85

    def test_refund_calculation(self):
        """Test refund calculation with penalties."""
        from app.jobs.cost_calculator import calculate_refund_amount

        # No prior cancellations - 100% refund
        amount, percentage = calculate_refund_amount(100, 0)
        assert amount == 100
        assert percentage == 1.0

        # 5 prior cancellations - 75% refund
        amount, percentage = calculate_refund_amount(100, 5)
        assert amount == 75
        assert percentage == 0.75

        # 10+ prior cancellations - 50% refund (minimum)
        amount, percentage = calculate_refund_amount(100, 15)
        assert amount == 50
        assert percentage == 0.5
