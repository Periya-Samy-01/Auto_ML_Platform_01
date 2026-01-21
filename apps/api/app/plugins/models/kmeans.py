"""
K-Means Clustering model plugin.
"""

from typing import Any, Dict, List

import numpy as np
from sklearn.cluster import KMeans

from app.plugins.base import (
    BaseModelPlugin,
    FieldType,
    HyperparameterField,
    HyperparameterSchema,
    ModelCategory,
    ProblemType,
)


class KMeansPlugin(BaseModelPlugin):
    """
    K-Means Clustering plugin.

    Unsupervised learning algorithm that partitions data into k clusters.
    """

    slug = "kmeans"
    name = "K-Means Clustering"
    description = "Partition data into k clusters based on feature similarity"
    icon = "🔵"
    problem_types = [ProblemType.CLUSTERING]
    category = ModelCategory.CLUSTERING
    best_for = "Customer segmentation and finding natural groupings"

    @classmethod
    def get_hyperparameters(cls) -> HyperparameterSchema:
        return HyperparameterSchema(
            main=[
                HyperparameterField(
                    key="n_clusters",
                    name="Number of Clusters (K)",
                    type=FieldType.INT,
                    default=3,
                    min=2,
                    max=20,
                    description="The number of clusters to form",
                ),
                HyperparameterField(
                    key="init",
                    name="Initialization Method",
                    type=FieldType.SELECT,
                    default="k-means++",
                    options=[
                        {"value": "k-means++", "label": "K-Means++ (smart)"},
                        {"value": "random", "label": "Random"},
                    ],
                    description="Method for initialization",
                ),
            ],
            advanced=[
                HyperparameterField(
                    key="n_init",
                    name="Number of Initializations",
                    type=FieldType.INT,
                    default=10,
                    min=1,
                    max=50,
                    description="Number of times to run with different seeds",
                ),
                HyperparameterField(
                    key="max_iter",
                    name="Max Iterations",
                    type=FieldType.INT,
                    default=300,
                    min=100,
                    max=1000,
                    description="Maximum iterations for a single run",
                ),
                HyperparameterField(
                    key="algorithm",
                    name="Algorithm",
                    type=FieldType.SELECT,
                    default="lloyd",
                    options=[
                        {"value": "lloyd", "label": "Lloyd (classic)"},
                        {"value": "elkan", "label": "Elkan (faster)"},
                    ],
                    description="K-means algorithm variant",
                ),
                HyperparameterField(
                    key="random_state",
                    name="Random Seed",
                    type=FieldType.INT,
                    default=42,
                    min=0,
                    max=9999,
                    description="Random seed for reproducibility",
                ),
            ],
        )

    @classmethod
    def get_supported_metrics(cls, problem_type: ProblemType) -> List[str]:
        return [
            "silhouette_score", "davies_bouldin_index",
            "calinski_harabasz_index", "inertia"
        ]

    @classmethod
    def get_default_metrics(cls, problem_type: ProblemType) -> List[str]:
        return ["silhouette_score", "inertia"]

    @classmethod
    def get_supported_plots(cls, problem_type: ProblemType) -> List[str]:
        return [
            "cluster_scatter", "elbow_plot", "silhouette_plot"
        ]

    @classmethod
    def get_default_plots(cls, problem_type: ProblemType) -> List[str]:
        return ["cluster_scatter"]

    @classmethod
    def train(
        cls,
        X_train: np.ndarray,
        y_train: np.ndarray,  # Ignored for clustering
        hyperparameters: Dict[str, Any],
        problem_type: ProblemType,
    ) -> Any:
        params = cls.get_default_hyperparameters()
        params.update(hyperparameters)

        model = KMeans(**params)
        model.fit(X_train)
        return model

    @classmethod
    def predict(cls, model: Any, X: np.ndarray) -> np.ndarray:
        """Get cluster labels for new data."""
        return model.predict(X)

    @classmethod
    def predict_proba(cls, model: Any, X: np.ndarray) -> None:
        """Clustering doesn't have probability predictions."""
        return None
