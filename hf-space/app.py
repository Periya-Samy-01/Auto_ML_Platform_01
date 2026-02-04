"""
AutoML Worker - Hugging Face Spaces

A Gradio-based ML execution service for the AutoML Platform.
Receives workflow JSON, trains models, and returns results.
"""

import json
import logging
import time
import base64
import io
from typing import Any, Dict, List, Optional
from enum import Enum

import gradio as gr
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report, roc_curve, auc
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class ProblemType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"


class NodeType(str, Enum):
    DATASET = "dataset"
    PREPROCESSING = "preprocessing"
    SPLIT = "trainTestSplit"
    MODEL = "model"
    EVALUATE = "evaluate"
    VISUALIZE = "visualize"


# =============================================================================
# SAMPLE DATASETS
# =============================================================================

SKLEARN_DATASETS = {
    "iris": ("load_iris", "target"),
    "breast_cancer": ("load_breast_cancer", "target"),
    "diabetes": ("load_diabetes", "target"),
    "wine": ("load_wine", "target"),
    "digits": ("load_digits", "target"),
    "california_housing": ("fetch_california_housing", "target"),
}


def load_sample_dataset(dataset_id: str) -> pd.DataFrame:
    """Load a sample dataset by ID."""
    # Normalize ID (remove "sample-" prefix if present)
    if dataset_id.startswith("sample-"):
        dataset_id = dataset_id[7:]
    
    if dataset_id not in SKLEARN_DATASETS:
        raise ValueError(f"Unknown sample dataset: {dataset_id}")
    
    loader_name, target_col = SKLEARN_DATASETS[dataset_id]
    data = getattr(datasets, loader_name)()
    
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df[target_col] = data.target
    
    logger.info(f"Loaded dataset '{dataset_id}' with shape {df.shape}")
    return df


# =============================================================================
# ML MODELS
# =============================================================================

def get_model(algorithm: str, hyperparameters: Dict, problem_type: ProblemType):
    """Get a scikit-learn model instance."""
    
    # Classification models
    if algorithm == "random_forest":
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        if problem_type == ProblemType.REGRESSION:
            return RandomForestRegressor(
                n_estimators=hyperparameters.get("n_estimators", 100),
                max_depth=hyperparameters.get("max_depth"),
                random_state=42,
            )
        return RandomForestClassifier(
            n_estimators=hyperparameters.get("n_estimators", 100),
            max_depth=hyperparameters.get("max_depth"),
            random_state=42,
        )
    
    elif algorithm == "logistic_regression":
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(
            C=hyperparameters.get("C", 1.0),
            max_iter=hyperparameters.get("max_iter", 100),
            random_state=42,
        )
    
    elif algorithm == "linear_regression":
        from sklearn.linear_model import LinearRegression
        return LinearRegression()
    
    elif algorithm == "decision_tree":
        from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
        if problem_type == ProblemType.REGRESSION:
            return DecisionTreeRegressor(
                max_depth=hyperparameters.get("max_depth"),
                random_state=42,
            )
        return DecisionTreeClassifier(
            max_depth=hyperparameters.get("max_depth"),
            random_state=42,
        )
    
    elif algorithm == "svm":
        from sklearn.svm import SVC, SVR
        if problem_type == ProblemType.REGRESSION:
            return SVR(
                C=hyperparameters.get("C", 1.0),
                kernel=hyperparameters.get("kernel", "rbf"),
            )
        return SVC(
            C=hyperparameters.get("C", 1.0),
            kernel=hyperparameters.get("kernel", "rbf"),
            probability=True,
            random_state=42,
        )
    
    elif algorithm == "knn":
        from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
        if problem_type == ProblemType.REGRESSION:
            return KNeighborsRegressor(
                n_neighbors=hyperparameters.get("n_neighbors", 5),
            )
        return KNeighborsClassifier(
            n_neighbors=hyperparameters.get("n_neighbors", 5),
        )
    
    elif algorithm == "naive_bayes":
        from sklearn.naive_bayes import GaussianNB
        return GaussianNB()
    
    elif algorithm == "xgboost":
        try:
            from xgboost import XGBClassifier, XGBRegressor
            if problem_type == ProblemType.REGRESSION:
                return XGBRegressor(
                    n_estimators=hyperparameters.get("n_estimators", 100),
                    max_depth=hyperparameters.get("max_depth", 6),
                    learning_rate=hyperparameters.get("learning_rate", 0.1),
                    random_state=42,
                )
            return XGBClassifier(
                n_estimators=hyperparameters.get("n_estimators", 100),
                max_depth=hyperparameters.get("max_depth", 6),
                learning_rate=hyperparameters.get("learning_rate", 0.1),
                random_state=42,
            )
        except ImportError:
            raise ValueError("XGBoost not installed")
    
    elif algorithm == "kmeans":
        from sklearn.cluster import KMeans
        return KMeans(
            n_clusters=hyperparameters.get("n_clusters", 3),
            random_state=42,
        )
    
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


# =============================================================================
# METRICS
# =============================================================================

def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray],
    problem_type: ProblemType,
    selected_metrics: List[str],
) -> List[Dict]:
    """Compute evaluation metrics."""
    results = []
    
    for metric_key in selected_metrics:
        try:
            value = None
            name = metric_key.replace("_", " ").title()
            
            if problem_type == ProblemType.CLASSIFICATION:
                if metric_key == "accuracy":
                    value = accuracy_score(y_true, y_pred)
                elif metric_key == "precision":
                    value = precision_score(y_true, y_pred, average="weighted", zero_division=0)
                elif metric_key == "recall":
                    value = recall_score(y_true, y_pred, average="weighted", zero_division=0)
                elif metric_key == "f1":
                    value = f1_score(y_true, y_pred, average="weighted", zero_division=0)
            
            elif problem_type == ProblemType.REGRESSION:
                if metric_key == "mse":
                    value = mean_squared_error(y_true, y_pred)
                    name = "Mean Squared Error"
                elif metric_key == "rmse":
                    value = np.sqrt(mean_squared_error(y_true, y_pred))
                    name = "Root Mean Squared Error"
                elif metric_key == "mae":
                    value = mean_absolute_error(y_true, y_pred)
                    name = "Mean Absolute Error"
                elif metric_key == "r2":
                    value = r2_score(y_true, y_pred)
                    name = "R² Score"
            
            if value is not None:
                results.append({
                    "key": metric_key,
                    "name": name,
                    "value": float(value),
                })
        except Exception as e:
            logger.warning(f"Failed to compute {metric_key}: {e}")
    
    return results


# =============================================================================
# PLOTS
# =============================================================================

def generate_plots(
    model,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray],
    problem_type: ProblemType,
    selected_plots: List[str],
    feature_names: List[str],
) -> List[Dict]:
    """Generate visualization plots."""
    results = []
    
    for plot_key in selected_plots:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            name = plot_key.replace("_", " ").title()
            
            if plot_key == "confusion_matrix" and problem_type == ProblemType.CLASSIFICATION:
                cm = confusion_matrix(y_test, y_pred)
                im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
                ax.figure.colorbar(im, ax=ax)
                ax.set_xlabel('Predicted')
                ax.set_ylabel('Actual')
                ax.set_title('Confusion Matrix')
                
            elif plot_key == "feature_importance":
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    indices = np.argsort(importances)[-10:]  # Top 10
                    names = [feature_names[i] if i < len(feature_names) else f"Feature {i}" for i in indices]
                    ax.barh(range(len(indices)), importances[indices])
                    ax.set_yticks(range(len(indices)))
                    ax.set_yticklabels(names)
                    ax.set_xlabel('Importance')
                    ax.set_title('Feature Importance')
                else:
                    plt.close(fig)
                    continue
                    
            elif plot_key == "actual_vs_predicted" and problem_type == ProblemType.REGRESSION:
                ax.scatter(y_test, y_pred, alpha=0.5)
                ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
                ax.set_xlabel('Actual')
                ax.set_ylabel('Predicted')
                ax.set_title('Actual vs Predicted')
                
            elif plot_key == "residuals" and problem_type == ProblemType.REGRESSION:
                residuals = y_test - y_pred
                ax.scatter(y_pred, residuals, alpha=0.5)
                ax.axhline(y=0, color='r', linestyle='--')
                ax.set_xlabel('Predicted')
                ax.set_ylabel('Residuals')
                ax.set_title('Residual Plot')
                
            else:
                plt.close(fig)
                continue
            
            # Convert to base64
            buffer = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='png', dpi=100)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)
            
            results.append({
                "key": plot_key,
                "name": name,
                "url": f"data:image/png;base64,{image_base64}",
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate {plot_key}: {e}")
            plt.close('all')
    
    return results


# =============================================================================
# WORKFLOW EXECUTOR
# =============================================================================

class WorkflowExecutor:
    """Executes ML workflows."""
    
    def __init__(self, nodes: List[Dict], edges: List[Dict]):
        self.nodes = {n["id"]: n for n in nodes}
        self.edges = edges
        
        # Execution context
        self.raw_data: Optional[pd.DataFrame] = None
        self.X_train: Optional[np.ndarray] = None
        self.X_test: Optional[np.ndarray] = None
        self.y_train: Optional[np.ndarray] = None
        self.y_test: Optional[np.ndarray] = None
        self.model = None
        self.predictions: Optional[np.ndarray] = None
        self.probabilities: Optional[np.ndarray] = None
        
        self.problem_type: Optional[ProblemType] = None
        self.target_column: Optional[str] = None
        self.feature_names: List[str] = []
        self.algorithm: Optional[str] = None
        self.hyperparameters: Dict = {}
        self.metrics: List[Dict] = []
        self.plots: List[Dict] = []
        self.training_time: float = 0.0
    
    def execute(self) -> Dict:
        """Execute the workflow and return results."""
        start_time = time.time()
        
        # Get execution order (simple topological sort based on edges)
        node_list = list(self.nodes.values())
        
        # Sort by type priority
        type_order = {
            "dataset": 0,
            "preprocessing": 1,
            "trainTestSplit": 2,
            "model": 3,
            "evaluate": 4,
            "visualize": 5,
        }
        node_list.sort(key=lambda n: type_order.get(n.get("type"), 99))
        
        for node in node_list:
            node_type = node.get("type")
            config = node.get("config", {})
            
            logger.info(f"Executing node: {node['id']} ({node_type})")
            
            if node_type == "dataset":
                self._execute_dataset(config)
            elif node_type == "trainTestSplit":
                self._execute_split(config)
            elif node_type == "model":
                self._execute_model(config)
            elif node_type == "evaluate":
                self._execute_evaluate(config)
            elif node_type == "visualize":
                self._execute_visualize(config)
        
        total_time = time.time() - start_time
        
        return {
            "algorithm": self.algorithm or "unknown",
            "algorithmName": self.algorithm.replace("_", " ").title() if self.algorithm else "Unknown",
            "problemType": self.problem_type.value if self.problem_type else "unknown",
            "trainingMode": "single",
            "trainingTimeSeconds": self.training_time,
            "hyperparameters": self.hyperparameters,
            "metrics": self.metrics,
            "plots": self.plots,
            "trainSamples": len(self.X_train) if self.X_train is not None else 0,
            "testSamples": len(self.X_test) if self.X_test is not None else 0,
            "featuresCount": len(self.feature_names),
            "creditsUsed": 0,
        }
    
    def _execute_dataset(self, config: Dict):
        """Load dataset."""
        dataset_id = config.get("dataset_id") or config.get("datasetId")
        is_sample = config.get("is_sample") or config.get("isSample", True)
        
        problem_type_str = config.get("problem_type") or config.get("problemType")
        self.target_column = config.get("target_column") or config.get("targetColumn")
        
        if problem_type_str:
            self.problem_type = ProblemType(problem_type_str)
        
        if is_sample:
            self.raw_data = load_sample_dataset(dataset_id)
        else:
            raise ValueError("Only sample datasets are supported in HF Space")
        
        logger.info(f"Loaded dataset with shape: {self.raw_data.shape}")
    
    def _execute_split(self, config: Dict):
        """Split data into train/test sets."""
        test_size = config.get("test_size") or config.get("testSize", 0.2)
        random_seed = config.get("random_seed") or config.get("randomSeed", 42)
        
        if self.raw_data is None:
            raise ValueError("No data available for splitting")
        
        logger.info(f"Raw data columns: {list(self.raw_data.columns)}")
        logger.info(f"Target column from config: {self.target_column}")
        
        # Determine target column with fallbacks
        target_col = None
        
        # First try the configured target column
        if self.target_column and self.target_column in self.raw_data.columns:
            target_col = self.target_column
        # Fallback to "target" (sklearn default)
        elif "target" in self.raw_data.columns:
            target_col = "target"
            self.target_column = target_col
            logger.info(f"Using fallback target column: {target_col}")
        # Fallback to last column
        else:
            target_col = self.raw_data.columns[-1]
            self.target_column = target_col
            logger.info(f"Using last column as target: {target_col}")
        
        logger.info(f"Final target column: {target_col}")
        
        # Separate features and target
        X = self.raw_data.drop(columns=[target_col])
        y = self.raw_data[target_col]
        
        self.feature_names = list(X.columns)
        X = X.values
        y = y.values
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_seed
        )
        
        logger.info(f"Split complete. Train: {len(self.X_train)}, Test: {len(self.X_test)}, y_train shape: {self.y_train.shape}")
    
    def _execute_model(self, config: Dict):
        """Train the model."""
        self.algorithm = config.get("algorithm")
        self.hyperparameters = config.get("hyperparameters", {})
        
        logger.info(f"Training {self.algorithm}...")
        start_time = time.time()
        
        self.model = get_model(self.algorithm, self.hyperparameters, self.problem_type)
        self.model.fit(self.X_train, self.y_train)
        
        self.training_time = time.time() - start_time
        
        # Make predictions
        self.predictions = self.model.predict(self.X_test)
        if hasattr(self.model, 'predict_proba'):
            try:
                self.probabilities = self.model.predict_proba(self.X_test)
            except:
                self.probabilities = None
        
        logger.info(f"Training complete in {self.training_time:.2f}s")
    
    def _execute_evaluate(self, config: Dict):
        """Evaluate the model."""
        selected_metrics = config.get("selected_metrics") or config.get("selectedMetrics", [])
        
        if self.model is None or self.predictions is None:
            raise ValueError("No model or predictions available")
        
        self.metrics = compute_metrics(
            self.y_test,
            self.predictions,
            self.probabilities,
            self.problem_type,
            selected_metrics,
        )
        
        logger.info(f"Evaluated {len(self.metrics)} metrics")
    
    def _execute_visualize(self, config: Dict):
        """Generate visualizations."""
        selected_plots = config.get("selected_plots") or config.get("selectedPlots", [])
        
        if not selected_plots:
            return
        
        self.plots = generate_plots(
            self.model,
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test,
            self.predictions,
            self.probabilities,
            self.problem_type,
            selected_plots,
            self.feature_names,
        )
        
        logger.info(f"Generated {len(self.plots)} plots")


# =============================================================================
# GRADIO INTERFACE
# =============================================================================

def execute_workflow(workflow_json: str) -> str:
    """
    Execute an ML workflow.
    
    Args:
        workflow_json: JSON string containing nodes and edges
        
    Returns:
        JSON string with execution results
    """
    try:
        logger.info("Received workflow execution request")
        workflow = json.loads(workflow_json)
        
        nodes = workflow.get("nodes", [])
        edges = workflow.get("edges", [])
        
        if not nodes:
            return json.dumps({"error": "No nodes in workflow"})
        
        executor = WorkflowExecutor(nodes, edges)
        results = executor.execute()
        
        logger.info("Workflow execution completed successfully")
        return json.dumps({"status": "completed", "results": results})
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return json.dumps({"status": "failed", "error": str(e)})


# Create Gradio interface
demo = gr.Interface(
    fn=execute_workflow,
    inputs=gr.Textbox(
        label="Workflow JSON",
        placeholder='{"nodes": [...], "edges": [...]}',
        lines=10,
    ),
    outputs=gr.Textbox(
        label="Results JSON",
        lines=20,
    ),
    title="AutoML Worker",
    description="ML execution service for AutoML Platform. Send workflow JSON to train models and get results.",
    examples=[
        # Example workflow JSON
        [json.dumps({
            "nodes": [
                {"id": "1", "type": "dataset", "config": {"datasetId": "iris", "isSample": True, "problemType": "classification", "targetColumn": "target"}},
                {"id": "2", "type": "trainTestSplit", "config": {"testSize": 0.2}},
                {"id": "3", "type": "model", "config": {"algorithm": "random_forest", "hyperparameters": {"n_estimators": 100}}},
                {"id": "4", "type": "evaluate", "config": {"selectedMetrics": ["accuracy", "precision", "recall", "f1"]}},
                {"id": "5", "type": "visualize", "config": {"selectedPlots": ["confusion_matrix", "feature_importance"]}},
            ],
            "edges": []
        }, indent=2)]
    ],
)


if __name__ == "__main__":
    demo.launch()
