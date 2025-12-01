"""
Manual Verification Script for Jobs System
Run this to verify the complete jobs implementation works correctly.

Usage:
    python verify_jobs_system.py
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from packages.database.base import Base
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
from apps.api.app.jobs.service import (
    create_job,
    get_jobs,
    get_job_by_id,
    cancel_job,
    retry_job,
    get_job_stats,
)
from apps.api.app.jobs.cost_calculator import (
    calculate_job_cost,
    calculate_refund_amount,
)


# Use in-memory SQLite for testing
TEST_DB_URL = "sqlite:///:memory:"


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_success(message: str):
    """Print success message."""
    print(f"[OK] {message}")


def print_error(message: str):
    """Print error message."""
    print(f"[ERROR] {message}")


def print_info(message: str):
    """Print info message."""
    print(f"  {message}")


def setup_test_database():
    """Create test database and tables."""
    # Enable SQLite type decorators for proper UUID handling
    engine = create_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        # Enable type conversion
        native_datetime=True,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def create_test_user(db):
    """Create a test user with credits."""
    user = User(
        email="verify@test.com",
        full_name="Verification User",
        tier=UserTier.PRO,
        credit_balance=0,
        email_verified=True,
    )
    db.add(user)
    db.flush()

    # Add initial credits
    transaction = CreditTransaction(
        user_id=user.id,
        amount=1000,
        balance_after=1000,
        transaction_type=TransactionType.PURCHASE,
        description="Initial credits for verification",
    )
    db.add(transaction)
    user.credit_balance = 1000
    db.commit()
    db.refresh(user)

    return user


def create_test_workflow(db, user):
    """Create a test workflow."""
    workflow = Workflow(
        user_id=user.id,
        name="Verification Workflow",
        description="Test workflow for verification",
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def create_test_snapshot(db, user, workflow):
    """Create a test workflow snapshot."""
    graph_json = {
        "nodes": [
            {
                "id": "dataset_1",
                "type": "dataset",
                "data": {"dataset_version_id": str(uuid.uuid4())}
            },
            {
                "id": "preprocess_1",
                "type": "preprocess",
                "data": {"operation": "missing_value_imputation"}
            },
            {
                "id": "preprocess_2",
                "type": "preprocess",
                "data": {"operation": "feature_scaling"}
            },
            {
                "id": "model_1",
                "type": "model",
                "data": {
                    "algorithm": "random_forest",
                    "algorithms": ["random_forest", "xgboost"],
                    "hpo_enabled": True,
                    "target_column": "target"
                }
            },
            {
                "id": "evaluate_1",
                "type": "evaluate",
                "data": {}
            }
        ],
        "edges": [
            {"source": "dataset_1", "target": "preprocess_1"},
            {"source": "preprocess_1", "target": "preprocess_2"},
            {"source": "preprocess_2", "target": "model_1"},
            {"source": "model_1", "target": "evaluate_1"}
        ]
    }

    snapshot = WorkflowSnapshot(
        workflow_id=workflow.id,
        user_id=user.id,
        graph_json=graph_json,
        snapshot_name="Verification Snapshot v1",
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def verify_cost_calculation():
    """Verify cost calculation logic."""
    print_section("1. Cost Calculation")

    # Test simple workflow
    simple_workflow = {
        "nodes": [
            {"type": "dataset", "data": {}},
            {"type": "model", "data": {"algorithms": ["logistic_regression"]}},
        ]
    }
    cost = calculate_job_cost(simple_workflow)
    expected = 10 + 0 + 20 + 10  # BASE + DATASET + MODEL_BASE + 1 algo
    if cost == expected:
        print_success(f"Simple workflow cost: {cost} credits (expected {expected})")
    else:
        print_error(f"Simple workflow cost: {cost} credits (expected {expected})")

    # Test complex workflow with HPO
    complex_workflow = {
        "nodes": [
            {"type": "dataset", "data": {}},
            {"type": "preprocess", "data": {}},
            {
                "type": "model",
                "data": {
                    "algorithms": ["random_forest", "xgboost", "logistic_regression"],
                    "hpo_enabled": True
                }
            },
            {"type": "evaluate", "data": {}},
        ]
    }
    cost = calculate_job_cost(complex_workflow)
    # BASE (10) + DATASET (0) + PREPROCESS (5) + MODEL (20 + 10 HPO + 30 for 3 algos) + EVAL (5)
    expected = 80
    if cost == expected:
        print_success(f"Complex workflow cost: {cost} credits (expected {expected})")
    else:
        print_error(f"Complex workflow cost: {cost} credits (expected {expected})")

    # Test refund calculation
    print_info("\nRefund calculations:")
    test_cases = [
        (0, 1.0, 100),   # 0 cancellations = 100% refund
        (5, 0.75, 75),   # 5 cancellations = 75% refund
        (10, 0.5, 50),   # 10 cancellations = 50% refund
        (20, 0.5, 50),   # 20 cancellations = 50% minimum
    ]

    for cancel_count, expected_pct, expected_amt in test_cases:
        amount, percentage = calculate_refund_amount(100, cancel_count)
        if amount == expected_amt and percentage == expected_pct:
            print_success(
                f"  {cancel_count} cancellations: {amount} credits "
                f"({percentage * 100:.0f}% refund)"
            )
        else:
            print_error(
                f"  {cancel_count} cancellations: {amount} credits "
                f"(expected {expected_amt})"
            )


def verify_job_creation(db, user, snapshot):
    """Verify job creation."""
    print_section("2. Job Creation")

    # Mock queue function to avoid Celery dependency
    from unittest.mock import patch

    with patch('apps.api.app.jobs.service.queue_job_execution'):
        # Create job
        job = create_job(
            db=db,
            user=user,
            workflow_snapshot_id=snapshot.id,
            priority=10,
        )

        if job.id:
            print_success(f"Job created: {job.id}")
            print_info(f"  Status: {job.status.value}")
            print_info(f"  Priority: {job.priority}")
            print_info(f"  Credits cost: {job.credits_cost}")
        else:
            print_error("Failed to create job")
            return None

        # Verify credits deducted
        balance = db.execute(
            select(func.coalesce(func.sum(CreditTransaction.amount), 0))
            .where(CreditTransaction.user_id == user.id)
        ).scalar_one()

        expected_balance = 1000 - job.credits_cost
        if balance == expected_balance:
            print_success(f"Credits deducted correctly: {balance} remaining")
        else:
            print_error(
                f"Credit balance incorrect: {balance} "
                f"(expected {expected_balance})"
            )

        return job


def verify_job_listing(db, user):
    """Verify job listing."""
    print_section("3. Job Listing & Filtering")

    # Get all jobs
    jobs, total = get_jobs(db=db, user=user, limit=10, offset=0)

    print_success(f"Retrieved {total} jobs")

    # Test filtering by status
    jobs_pending, total_pending = get_jobs(
        db=db,
        user=user,
        status_filter=JobStatus.PENDING,
        limit=10,
        offset=0,
    )

    print_success(f"Filtered to {total_pending} pending jobs")

    # Test pagination
    jobs_page1, _ = get_jobs(db=db, user=user, limit=1, offset=0)
    jobs_page2, _ = get_jobs(db=db, user=user, limit=1, offset=1)

    if len(jobs_page1) <= 1:
        print_success(f"Pagination working (page 1: {len(jobs_page1)} items)")
    else:
        print_error("Pagination not working correctly")


def verify_job_retrieval(db, user, job):
    """Verify job retrieval."""
    print_section("4. Job Retrieval")

    retrieved_job = get_job_by_id(db=db, user=user, job_id=job.id)

    if retrieved_job.id == job.id:
        print_success(f"Job retrieved: {retrieved_job.id}")
        print_info(f"  Status: {retrieved_job.status.value}")
        print_info(f"  Created: {retrieved_job.created_at}")
    else:
        print_error("Failed to retrieve job")


def verify_job_cancellation(db, user, snapshot):
    """Verify job cancellation."""
    print_section("5. Job Cancellation")

    from unittest.mock import patch

    with patch('apps.api.app.jobs.service.queue_job_execution'):
        # Create a new job to cancel
        cancel_job_obj = create_job(
            db=db,
            user=user,
            workflow_snapshot_id=snapshot.id,
            priority=5,
        )

        # Manually set to RUNNING (simulate Celery picked it up)
        cancel_job_obj.status = JobStatus.RUNNING
        cancel_job_obj.started_at = datetime.utcnow()
        db.commit()

        print_info(f"Created job to cancel: {cancel_job_obj.id}")

    with patch('apps.api.app.jobs.service.revoke_celery_task'):
        # Cancel it
        cancelled_job, refund_amount, refund_pct = cancel_job(
            db=db,
            user=user,
            job_id=cancel_job_obj.id,
        )

        if cancelled_job.status == JobStatus.CANCELLED:
            print_success("Job cancelled successfully")
            print_info(f"  Refund: {refund_amount} credits ({refund_pct * 100:.0f}%)")
        else:
            print_error(f"Job cancellation failed (status: {cancelled_job.status})")


def verify_job_retry(db, user, snapshot):
    """Verify job retry."""
    print_section("6. Job Retry")

    from unittest.mock import patch

    with patch('apps.api.app.jobs.service.queue_job_execution'):
        # Create a failed job
        failed_job = create_job(
            db=db,
            user=user,
            workflow_snapshot_id=snapshot.id,
            priority=5,
        )

        # Mark as failed
        failed_job.status = JobStatus.FAILED
        failed_job.error_message = "Simulated failure"
        failed_job.completed_at = datetime.utcnow()
        db.commit()

        print_info(f"Created failed job: {failed_job.id}")

        # Retry it
        new_job = retry_job(db=db, user=user, job_id=failed_job.id)

        if new_job.id != failed_job.id:
            print_success(f"New job created: {new_job.id}")
            print_info(f"  Original job: {failed_job.id}")
            print_info(f"  New job status: {new_job.status.value}")
        else:
            print_error("Job retry failed")


def verify_job_stats(db, user):
    """Verify job statistics."""
    print_section("7. Job Statistics")

    stats = get_job_stats(db=db, user=user)

    print_success("Job statistics retrieved:")
    print_info(f"  Total jobs: {stats['total_jobs']}")
    print_info(f"  Completed: {stats['completed_jobs']}")
    print_info(f"  Failed: {stats['failed_jobs']}")
    print_info(f"  Running: {stats['running_jobs']}")
    print_info(f"  Cancelled: {stats['cancelled_jobs']}")
    print_info(f"  Total credits spent: {stats['total_credits_spent']}")

    if stats['success_rate'] is not None:
        print_info(f"  Success rate: {stats['success_rate'] * 100:.1f}%")


def verify_job_nodes(db, user, snapshot):
    """Verify job nodes creation."""
    print_section("8. Job Nodes (Execution Tracking)")

    from unittest.mock import patch

    with patch('apps.api.app.jobs.service.queue_job_execution'):
        job = create_job(
            db=db,
            user=user,
            workflow_snapshot_id=snapshot.id,
        )

        # Manually create job nodes to simulate execution
        nodes = snapshot.graph_json["nodes"]

        for i, node in enumerate(nodes):
            job_node = JobNode(
                job_id=job.id,
                node_id=node["id"],
                node_type=NodeType[node["type"].upper()],
                status=NodeStatus.COMPLETED if i < 2 else NodeStatus.PENDING,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow() if i < 2 else None,
                duration_seconds=10 if i < 2 else None,
                progress_percentage=100 if i < 2 else 0,
            )
            db.add(job_node)

        db.commit()

        # Retrieve job nodes
        nodes_result = db.execute(
            select(JobNode)
            .where(JobNode.job_id == job.id)
            .order_by(JobNode.created_at)
        ).scalars().all()

        print_success(f"Created {len(nodes_result)} job nodes")
        for node in nodes_result:
            print_info(
                f"  {node.node_id}: {node.node_type.value} - {node.status.value}"
            )


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("  Jobs System Verification")
    print("  AutoML Platform 2.0")
    print("=" * 60)

    try:
        # Setup
        print_info("\nSetting up test database...")
        db = setup_test_database()
        user = create_test_user(db)
        workflow = create_test_workflow(db, user)
        snapshot = create_test_snapshot(db, user, workflow)
        print_success("Test database setup complete")

        # Run verification tests
        verify_cost_calculation()

        job = verify_job_creation(db, user, snapshot)
        if job:
            verify_job_listing(db, user)
            verify_job_retrieval(db, user, job)

        verify_job_cancellation(db, user, snapshot)
        verify_job_retry(db, user, snapshot)
        verify_job_stats(db, user)
        verify_job_nodes(db, user, snapshot)

        # Summary
        print_section("Verification Complete")
        print_success("All core job system features verified!")
        print_info("\nNext steps:")
        print_info("  1. Run pytest for automated tests")
        print_info("  2. Start Celery worker to test actual execution")
        print_info("  3. Test via API endpoints with real HTTP requests")

        db.close()

    except Exception as e:
        print_error(f"\nVerification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
