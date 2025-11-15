# apps/workers/worker/celery_app.py
from __future__ import annotations

import os
from celery import Celery

# Read broker/result URLs from env (see .env.example below)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Optional: basic config
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    timezone="UTC",
)

# Autodiscover tasks in worker.tasks package
celery_app.autodiscover_tasks(["worker.tasks"])
