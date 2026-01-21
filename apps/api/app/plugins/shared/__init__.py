"""
Shared utilities for the plugin system.

Contains:
- constants: Metric and plot definitions
- evaluators: Shared evaluation metric functions
- visualizers: Shared visualization functions
"""

from app.plugins.shared.constants import (
    METRIC_DEFINITIONS,
    PLOT_DEFINITIONS,
    get_metric_definition,
    get_plot_definition,
)
from app.plugins.shared.evaluators import (
    compute_metric,
    compute_metrics,
    get_available_metrics,
)
from app.plugins.shared.visualizers import (
    generate_plot,
    get_available_plots,
)

__all__ = [
    # Constants
    "METRIC_DEFINITIONS",
    "PLOT_DEFINITIONS",
    "get_metric_definition",
    "get_plot_definition",
    # Evaluators
    "compute_metric",
    "compute_metrics",
    "get_available_metrics",
    # Visualizers
    "generate_plot",
    "get_available_plots",
]
