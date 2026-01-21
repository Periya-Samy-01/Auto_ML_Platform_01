#apps/workers/worker/ml/evaluators/clustering_evaluator.py
"""
Clustering metrics evaluator.
Computes Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index, and Inertia.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)
from .base import BaseEvaluator


class ClusteringEvaluator(BaseEvaluator):
    """
    Evaluator for clustering tasks (unsupervised).
    
    Computes:
    - Silhouette Score: Measures how similar points are to their own cluster vs other clusters
      Range: [-1, 1], Higher is better (1 = perfect clustering, -1 = wrong clustering)
    
    - Davies-Bouldin Index: Average similarity ratio of each cluster with its most similar cluster
      Range: [0, ∞), Lower is better (0 = perfect clustering)
    
    - Calinski-Harabasz Index: Ratio of between-cluster to within-cluster dispersion
      Range: [0, ∞), Higher is better
    
    - Inertia (WCSS): Sum of squared distances of samples to their nearest cluster center
      Range: [0, ∞), Lower is better (only meaningful when comparing same n_clusters)
    """
    
    def evaluate(
        self,
        X: np.ndarray,
        y_pred: np.ndarray,
        inertia: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Compute clustering evaluation metrics.
        
        Args:
            X: Feature matrix (n_samples, n_features) - used for distance calculations
            y_pred: Predicted cluster IDs (n_samples,) - integers from 0 to n_clusters-1
            inertia: Optional inertia value from KMeans.inertia_ (for convenience)
            
        Returns:
            Dictionary with 4 metrics:
            - silhouette_score: [-1, 1], higher is better
            - davies_bouldin_index: [0, ∞), lower is better
            - calinski_harabasz_index: [0, ∞), higher is better
            - inertia: [0, ∞), lower is better
            
        Raises:
            ValueError: If y_pred contains only one cluster (metrics undefined)
        """
        metrics = {}
        
        # Check if we have more than 1 cluster
        n_clusters = len(np.unique(y_pred))
        if n_clusters <= 1:
            raise ValueError(
                f"Clustering evaluation requires at least 2 clusters. "
                f"Found {n_clusters} cluster(s). "
                f"Check your n_clusters parameter."
            )
        
        # 1. Silhouette Score
        try:
            silhouette = silhouette_score(X, y_pred)
            metrics["silhouette_score"] = float(silhouette)
        except Exception as e:
            metrics["silhouette_score"] = None
            print(f"⚠️  Warning: Could not compute Silhouette Score: {str(e)}")
        
        # 2. Davies-Bouldin Index
        try:
            davies_bouldin = davies_bouldin_score(X, y_pred)
            metrics["davies_bouldin_index"] = float(davies_bouldin)
        except Exception as e:
            metrics["davies_bouldin_index"] = None
            print(f"⚠️  Warning: Could not compute Davies-Bouldin Index: {str(e)}")
        
        # 3. Calinski-Harabasz Index
        try:
            calinski_harabasz = calinski_harabasz_score(X, y_pred)
            metrics["calinski_harabasz_index"] = float(calinski_harabasz)
        except Exception as e:
            metrics["calinski_harabasz_index"] = None
            print(f"⚠️  Warning: Could not compute Calinski-Harabasz Index: {str(e)}")
        
        # 4. Inertia (sum of squared distances to cluster center)
        if inertia is not None:
            metrics["inertia"] = float(inertia)
        else:
            # If not provided, compute manually (slower)
            try:
                inertia_computed = compute_inertia(X, y_pred)
                metrics["inertia"] = float(inertia_computed)
            except Exception as e:
                metrics["inertia"] = None
                print(f"⚠️  Warning: Could not compute Inertia: {str(e)}")
        
        return metrics


def compute_inertia(X: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Compute inertia (within-cluster sum of squared distances).
    
    This is useful if the model doesn't provide inertia directly.
    
    Args:
        X: Feature matrix (n_samples, n_features)
        y_pred: Cluster IDs (n_samples,)
        
    Returns:
        Inertia value (sum of squared distances)
    """
    inertia = 0.0
    
    for cluster_id in np.unique(y_pred):
        # Get points in this cluster
        cluster_mask = y_pred == cluster_id
        cluster_points = X[cluster_mask]
        
        if len(cluster_points) == 0:
            continue
        
        # Compute cluster center
        center = cluster_points.mean(axis=0)
        
        # Compute sum of squared distances
        distances = np.linalg.norm(cluster_points - center, axis=1)
        inertia += np.sum(distances ** 2)
    
    return inertia
