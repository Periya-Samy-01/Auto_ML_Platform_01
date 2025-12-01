# apps/workers/worker/celery_app.py
from __future__ import annotations

import os
from celery import Celery
from kombu import Queue, Exchange

# Read broker/result URLs from env
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Define exchanges and queues for priority-based routing
default_exchange = Exchange("default", type="direct")

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    enable_utc=True,
    timezone="UTC",

    # Task execution
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (prevent memory leaks)

    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,  # Persist results

    # Task acknowledgment
    task_acks_late=True,  # Acknowledge tasks after completion (for reliability)
    task_reject_on_worker_lost=True,  # Requeue task if worker crashes

    # Queue configuration
    task_default_queue="normal",
    task_default_exchange="default",
    task_default_routing_key="normal",

    # Define queues with priorities
    task_queues=(
        Queue(
            "high_priority",
            exchange=default_exchange,
            routing_key="high",
            priority=10,  # Highest priority
        ),
        Queue(
            "normal",
            exchange=default_exchange,
            routing_key="normal",
            priority=5,  # Normal priority
        ),
        Queue(
            "overflow",
            exchange=default_exchange,
            routing_key="low",
            priority=1,  # Lowest priority
        ),
    ),

    # Task routing
    task_routes={
        "worker.tasks.job_execution_task.execute_job": {
            "queue": "normal",  # Default, will be overridden at runtime
        },
        "worker.tasks.ingestion_task.*": {
            "queue": "normal",
        },
        "worker.tasks.cleanup_task.*": {
            "queue": "overflow",
        },
    },
)

# Autodiscover tasks in worker.tasks package
celery_app.autodiscover_tasks(["worker.tasks"])
