"""
Celery Tasks
Task stubs for API to queue work to the worker
"""

from celery import Celery
from app.core.config import settings

# Create Celery app (same configuration as worker)
celery_app = Celery(
    "api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    timezone="UTC",
)


# Task stub - the actual implementation is in the worker app
@celery_app.task(name='worker.process_dataset_ingestion')
def process_dataset_ingestion(job_id: str):
    """
    Queue dataset ingestion task to worker
    This is a stub that sends the task to the worker queue
    """
    pass  # Actual implementation in workers/worker/tasks/ingestion_task.py
