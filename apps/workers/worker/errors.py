# apps/workers/worker/errors.py

class WorkerError(Exception):
    """Base class for all worker-level errors."""
    pass


class TrainingError(WorkerError):
    """Raised when model training fails."""
    pass


class EvaluationError(WorkerError):
    """Raised when metric computation or evaluation fails."""
    pass


class SerializationError(WorkerError):
    """Raised if model save/load fails."""
    pass
