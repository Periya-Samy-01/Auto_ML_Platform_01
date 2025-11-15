# apps/workers/worker/utils.py
from __future__ import annotations

import traceback
from typing import Callable, TypeVar, Any

from worker.logging_config import get_logger
from worker.errors import WorkerError

T = TypeVar("T")

logger = get_logger(__name__)


def safe_call(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Wrap calls inside trainers/evaluators to ensure errors
    are logged with stack traces and re-wrapped in WorkerError.

    Example:
        result = safe_call(model.fit, X, y)
    """
    try:
        return fn(*args, **kwargs)

    except WorkerError:
        # If it's already a WorkerError, don't wrap again
        logger.error("WorkerError raised:\n%s", traceback.format_exc())
        raise

    except Exception as e:
        logger.error("Unhandled error in worker function:\n%s", traceback.format_exc())
        raise WorkerError(str(e)) from e
