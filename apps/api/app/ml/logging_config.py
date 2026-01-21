# apps/api/app/ml/logging_config.py
import logging
from logging import Logger
from typing import Optional


def get_logger(name: Optional[str] = None, level: int = logging.INFO) -> Logger:
    """
    Simple logger factory for workers.

    Usage:
        from app.ml.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("hello")
    """
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt)
    return logging.getLogger(name)
