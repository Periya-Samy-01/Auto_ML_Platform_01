# apps/workers/worker/ml/evaluators/base.py
from __future__ import annotations

import abc
from typing import Any, Dict, Iterable, Mapping, Optional

import numpy as np
import pandas as pd


ArrayLike = Optional[np.ndarray]


class BaseEvaluator(abc.ABC):
    """
    Abstract base class for model evaluators.

    Concrete evaluators should compute metrics for classification and regression tasks.

    Methods
    -------
    evaluate(y_true, y_pred, *, sample_weight=None)
        Returns a mapping of metric_name -> numeric value.
    """

    def __init__(self, name: str = "base_evaluator"):
        self.name = name

    @abc.abstractmethod
    def evaluate(
        self,
        y_true: Iterable,
        y_pred: Iterable,
        *,
        sample_weight: Optional[Iterable] = None,
    ) -> Mapping[str, float]:
        """
        Compute evaluation metrics.

        Parameters
        ----------
        y_true:
            Ground-truth targets (iterable/array-like).
        y_pred:
            Predictions from the model (iterable/array-like).
        sample_weight:
            Optional sample weights.

        Returns
        -------
        Mapping[str, float]
            Dictionary mapping metric names to values (e.g. {"accuracy": 0.91}).
        """
        raise NotImplementedError
