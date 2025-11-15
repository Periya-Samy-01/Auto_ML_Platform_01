# apps/workers/worker/tasks/train_task.py
from __future__ import annotations

from typing import Any, Dict
import time

from worker.celery_app import celery_app
from worker.logging_config import get_logger
from worker.utils import safe_call
from worker.errors import TrainingError

logger = get_logger(__name__)


@celery_app.task(bind=True, name="worker.tasks.train_task.simple_train")
def simple_train(self, dataset_path: str, config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Example Celery task that simulates a training job. In a real task you'd:
      - download dataset from R2 (boto3)
      - create a trainer instance (LogisticRegressionTrainer)
      - call trainer.fit(X, y) via safe_call
      - serialize model and update DB/job record

    This minimal task logs progress and returns a small payload for testing.
    """
    logger.info("Starting simple_train task (job id: %s)", self.request.id)
    try:
        # Simulate progress updates (in real app publish to Redis pubsub)
        for pct in (10, 40, 70, 100):
            logger.info("Job %s progress: %d%%", self.request.id, pct)
            time.sleep(0.2)

        # Example: if you had a trainer, you'd do:
        # trainer = LogisticRegressionTrainer(name="lr", task="classification")
        # safe_call(trainer.fit, X, y)

        # Return a small result payload (Celery will store in backend)
        result = {"job_id": self.request.id, "status": "completed", "metrics": {"dummy_accuracy": 0.95}}
        logger.info("Finished simple_train task (job id: %s)", self.request.id)
        return result

    except Exception as e:
        # Use logger and wrap into a TrainingError for consistent handling
        logger.exception("Training failed for job %s", self.request.id)
        raise TrainingError(str(e)) from e
