# cli/commands/train.py
"""
Train command implementation for CLI.
Orchestrates data loading, training, evaluation, and output handling.
Supports both supervised and unsupervised learning tasks.
"""

from typing import Optional
import numpy as np

from cli.utils.data_loader import load_and_split_data
from cli.utils.trainer_factory import get_trainer, is_supervised_trainer
from cli.utils.output_handler import save_all_outputs
from apps.workers.worker.constants import (
    TASK_CLASSIFICATION, 
    TASK_REGRESSION,
    TASK_CLUSTERING,
    TASK_DIMENSIONALITY_REDUCTION
)
from apps.workers.worker.ml.evaluators.classification_evaluator import ClassificationEvaluator
from apps.workers.worker.ml.evaluators.regression_evaluator import RegressionEvaluator
from apps.workers.worker.ml.evaluators.clustering_evaluator import ClusteringEvaluator


def train_command(
    algorithm: str,
    task: str,
    dataset: str,
    target: Optional[str] = None,
    use_full_dataset: bool = False,
    n_components: Optional[int] = None
) -> None:
    """
    Execute the training workflow for a given algorithm and dataset.
    
    Supports supervised (classification, regression) and unsupervised (clustering, 
    dimensionality_reduction) tasks.
    
    Args:
        algorithm: Algorithm name (e.g., "decision_tree", "kmeans", "pca")
        task: Task type (classification, regression, clustering, dimensionality_reduction)
        dataset: Path to CSV dataset
        target: Target column name (required for supervised, ignored for unsupervised)
        use_full_dataset: If True, use full dataset without train/test split
        n_components: For PCA only - number of components to reduce to
        
    Raises:
        ValueError: If task type is invalid or required parameters missing
        FileNotFoundError: If dataset file not found
    """
    try:
        # Validate task type
        valid_tasks = {TASK_CLASSIFICATION, TASK_REGRESSION, TASK_CLUSTERING, TASK_DIMENSIONALITY_REDUCTION}
        task = task.lower()
        if task not in valid_tasks:
            raise ValueError(
                f"Invalid task '{task}'. "
                f"Available: {', '.join(sorted(valid_tasks))}"
            )
        
        # Step 1: Load data
        print(f"\n📦 Loading data from {dataset}...")
        
        # For unsupervised, target is not needed
        if task in {TASK_CLUSTERING, TASK_DIMENSIONALITY_REDUCTION}:
            X, X_test, _, _ = load_and_split_data(
                dataset, 
                target_col=None, 
                use_full_dataset=use_full_dataset
            )
            y_train = None
            y_test = None
            print(f"✓ Data loaded: {X.shape[0]} samples")
        else:
            # For supervised, target is required
            if target is None:
                raise ValueError(
                    f"Task '{task}' requires --target column. "
                    f"Use --target <column_name>"
                )
            
            X, X_test, y_train, y_test = load_and_split_data(
                dataset,
                target_col=target,
                use_full_dataset=use_full_dataset
            )
            print(f"✓ Data loaded: {X.shape[0]} training samples")
            if X_test is not None:
                print(f"✓ Test set: {X_test.shape[0]} samples")
        
        print(f"✓ Features: {X.shape[1]}")
        
        # Step 2: Get trainer
        print(f"\n🤖 Initializing {algorithm} trainer for {task}...")
        
        # Handle PCA n_components
        hyperparams = {}
        if task == TASK_DIMENSIONALITY_REDUCTION and n_components:
            hyperparams = {"n_components": n_components}
        
        trainer = get_trainer(algorithm, task, hyperparameters=hyperparams if hyperparams else None)
        print(f"✓ Trainer initialized with default hyperparameters")
        
        # Step 3: Train model
        print(f"\n🚀 Training model...")
        trainer.fit(X, y_train)
        print(f"✓ Model trained successfully")
        
        # Step 4: Make predictions
        print(f"\n🔮 Making predictions...")
        y_pred = trainer.predict(X)
        print(f"✓ Predictions generated")
        
        # Step 5: Handle task-specific outputs
        y_pred_proba: Optional[np.ndarray] = None
        
        if task == TASK_CLASSIFICATION:
            # Get probabilities for classification
            try:
                y_pred_proba = trainer.predict_proba(X)
            except NotImplementedError:
                pass
        elif task == TASK_DIMENSIONALITY_REDUCTION:
            # For PCA, y_pred is transformed features
            print(f"✓ Transformed to {y_pred.shape[1]} dimensions")
            # For PCA, we don't evaluate - just show variance explained
            y_test = None
            y_pred = y_pred
        
        # Step 6: Evaluate (if not unsupervised without labels)
        metrics = {}
        if task in {TASK_CLASSIFICATION, TASK_REGRESSION}:
            # Supervised: evaluate on test set
            print(f"\n📊 Evaluating model...")
            
            if X_test is not None:
                y_pred_test = trainer.predict(X_test)
            else:
                # If use_full_dataset, evaluate on training set
                y_pred_test = y_pred
                y_test = y_train
            
            if task == TASK_CLASSIFICATION:
                evaluator = ClassificationEvaluator()
                y_proba_test = None
                if y_pred_proba is not None:
                    y_proba_test = trainer.predict_proba(X_test) if X_test is not None else y_pred_proba
                metrics = evaluator.evaluate(y_test, y_pred_test, y_proba_test)
            
            elif task == TASK_REGRESSION:
                evaluator = RegressionEvaluator()
                metrics = evaluator.evaluate(y_test, y_pred_test)
        
        elif task == TASK_CLUSTERING:
            # Unsupervised: evaluate clustering
            print(f"\n📊 Evaluating clusters...")
            evaluator = ClusteringEvaluator()
            inertia = trainer.model.inertia_ if hasattr(trainer.model, 'inertia_') else None
            metrics = evaluator.evaluate(X, y_pred, inertia=inertia)
        
        # Step 7: Save outputs
        print(f"\n💾 Saving results...")
        output_dir = save_all_outputs(
            trainer=trainer,
            y_test=y_test if task in {TASK_CLASSIFICATION, TASK_REGRESSION} else None,
            y_pred=y_pred,
            metrics=metrics,
            algorithm=algorithm,
            task=task,
            y_pred_proba=y_pred_proba,
            X=X,
            X_test=X_test
        )
        print(f"✓ Results saved to {output_dir}")
        
        # Step 8: Print results
        print("\n" + "="*50)
        print("TRAINING RESULTS")
        print("="*50)
        print(f"Algorithm: {algorithm}")
        print(f"Task: {task}")
        print(f"Samples: {X.shape[0]}")
        print(f"Features: {X.shape[1]}")
        
        if task == TASK_DIMENSIONALITY_REDUCTION:
            print(f"Components: {y_pred.shape[1]}")
            if hasattr(trainer.model, 'explained_variance_ratio_'):
                total_variance = np.sum(trainer.model.explained_variance_ratio_)
                print(f"Variance explained: {total_variance*100:.2f}%")
        
        print("-"*50)
        
        if metrics:
            for metric_name, metric_value in metrics.items():
                if metric_name == "confusion_matrix":
                    continue
                
                if isinstance(metric_value, float):
                    print(f"{metric_name}: {metric_value:.4f}")
                else:
                    print(f"{metric_name}: {metric_value}")
        
        print("-"*50)
        print(f"Model saved: {output_dir}/model.joblib")
        print(f"Results saved: {output_dir}/results.json")
        
        if task == TASK_CLASSIFICATION:
            print(f"Visualization: {output_dir}/confusion_matrix.png")
        elif task == TASK_REGRESSION:
            print(f"Visualization: {output_dir}/predictions_plot.png")
        elif task == TASK_CLUSTERING:
            print(f"Visualization: {output_dir}/clusters_plot.png")
        
        print("="*50 + "\n")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        raise
    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise
