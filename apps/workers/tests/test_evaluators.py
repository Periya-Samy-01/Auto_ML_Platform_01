"""
Evaluator tests - classification and regression metrics.
Tests metric computation and edge cases for evaluators.
"""

import pytest
import numpy as np
from worker.ml.evaluators import ClassificationEvaluator, RegressionEvaluator


def test_classification_evaluator_binary():
    """Test ClassificationEvaluator: binary classification metrics."""
    try:
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 0, 1, 1])
        
        evaluator = ClassificationEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # Check all metrics are present
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "confusion_matrix" in metrics
        assert "roc_auc" in metrics  # None without probabilities
        
        # Check accuracy
        # 6 correct out of 8 = 0.75
        assert metrics["accuracy"] == 0.75
        
        # Check metrics are floats
        assert isinstance(metrics["accuracy"], float)
        assert isinstance(metrics["precision"], float)
        assert isinstance(metrics["recall"], float)
        assert isinstance(metrics["f1_score"], float)
        
        # Check confusion matrix is list (for JSON serialization)
        assert isinstance(metrics["confusion_matrix"], list)
        
        print("✅ ClassificationEvaluator binary classification passed")
        
    except Exception as e:
        print(f"❌ ClassificationEvaluator binary classification failed: {e}")
        raise


def test_classification_evaluator_multiclass():
    """Test ClassificationEvaluator: multiclass classification metrics."""
    try:
        y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 2, 1, 0, 1, 2])
        
        evaluator = ClassificationEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # Check all metrics are present
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "confusion_matrix" in metrics
        
        # Accuracy: 7 correct out of 9 = ~0.778
        assert 0.7 < metrics["accuracy"] < 0.8
        
        # Confusion matrix should be 3x3 for 3 classes
        cm = metrics["confusion_matrix"]
        assert len(cm) == 3
        assert len(cm[0]) == 3
        
        print("✅ ClassificationEvaluator multiclass classification passed")
        
    except Exception as e:
        print(f"❌ ClassificationEvaluator multiclass classification failed: {e}")
        raise


def test_classification_evaluator_with_probabilities():
    """Test ClassificationEvaluator: ROC-AUC with probabilities."""
    try:
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 0, 1, 1])
        
        # Probabilities for positive class (class 1)
        y_pred_proba = np.array([
            [0.9, 0.1],  # High prob for class 0
            [0.2, 0.8],  # High prob for class 1
            [0.6, 0.4],  # Medium prob
            [0.8, 0.2],
            [0.1, 0.9],
            [0.7, 0.3],
            [0.3, 0.7],
            [0.4, 0.6],
        ])
        
        evaluator = ClassificationEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred, y_pred_proba=y_pred_proba)
        
        # ROC-AUC should be computed
        assert metrics["roc_auc"] is not None
        assert isinstance(metrics["roc_auc"], float)
        assert 0 <= metrics["roc_auc"] <= 1
        
        print("✅ ClassificationEvaluator with probabilities passed")
        
    except Exception as e:
        print(f"❌ ClassificationEvaluator with probabilities failed: {e}")
        raise


def test_classification_evaluator_perfect_predictions():
    """Test ClassificationEvaluator: perfect predictions."""
    try:
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 1, 2])  # Perfect predictions
        
        evaluator = ClassificationEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # All metrics should be 1.0
        assert metrics["accuracy"] == 1.0
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1_score"] == 1.0
        
        print("✅ ClassificationEvaluator perfect predictions passed")
        
    except Exception as e:
        print(f"❌ ClassificationEvaluator perfect predictions failed: {e}")
        raise


def test_classification_evaluator_all_wrong():
    """Test ClassificationEvaluator: all predictions wrong."""
    try:
        y_true = np.array([0, 0, 0, 0])
        y_pred = np.array([1, 1, 1, 1])  # All wrong
        
        evaluator = ClassificationEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # Accuracy should be 0.0
        assert metrics["accuracy"] == 0.0
        
        print("✅ ClassificationEvaluator all wrong predictions passed")
        
    except Exception as e:
        print(f"❌ ClassificationEvaluator all wrong predictions failed: {e}")
        raise


def test_regression_evaluator_basic():
    """Test RegressionEvaluator: basic regression metrics."""
    try:
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
        
        evaluator = RegressionEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # Check all metrics are present
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "mae" in metrics
        assert "r2_score" in metrics
        
        # Check metrics are floats
        assert isinstance(metrics["mse"], float)
        assert isinstance(metrics["rmse"], float)
        assert isinstance(metrics["mae"], float)
        assert isinstance(metrics["r2_score"], float)
        
        # Check RMSE is sqrt of MSE
        assert np.isclose(metrics["rmse"], np.sqrt(metrics["mse"]))
        
        # R2 should be close to 1 for good predictions
        assert metrics["r2_score"] > 0.9
        
        print("✅ RegressionEvaluator basic metrics passed")
        
    except Exception as e:
        print(f"❌ RegressionEvaluator basic metrics failed: {e}")
        raise


def test_regression_evaluator_perfect_predictions():
    """Test RegressionEvaluator: perfect predictions."""
    try:
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # Perfect
        
        evaluator = RegressionEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # MSE, RMSE, MAE should all be 0
        assert metrics["mse"] == 0.0
        assert metrics["rmse"] == 0.0
        assert metrics["mae"] == 0.0
        
        # R2 should be 1.0
        assert metrics["r2_score"] == 1.0
        
        print("✅ RegressionEvaluator perfect predictions passed")
        
    except Exception as e:
        print(f"❌ RegressionEvaluator perfect predictions failed: {e}")
        raise


def test_regression_evaluator_constant_predictions():
    """Test RegressionEvaluator: constant predictions."""
    try:
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([3.0, 3.0, 3.0, 3.0, 3.0])  # All same
        
        evaluator = RegressionEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # MSE should be positive
        assert metrics["mse"] > 0
        
        # R2 should be 0 (as good as predicting mean)
        assert np.isclose(metrics["r2_score"], 0.0)
        
        print("✅ RegressionEvaluator constant predictions passed")
        
    except Exception as e:
        print(f"❌ RegressionEvaluator constant predictions failed: {e}")
        raise


def test_regression_evaluator_negative_predictions():
    """Test RegressionEvaluator: negative predictions."""
    try:
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([-1.0, -2.0, -3.0, -4.0, -5.0])  # All wrong sign
        
        evaluator = RegressionEvaluator()
        metrics = evaluator.evaluate(y_true, y_pred)
        
        # Metrics should still be computed
        assert metrics["mse"] > 0
        assert metrics["rmse"] > 0
        assert metrics["mae"] > 0
        
        # R2 should be negative (worse than predicting mean)
        assert metrics["r2_score"] < 0
        
        print("✅ RegressionEvaluator negative predictions passed")
        
    except Exception as e:
        print(f"❌ RegressionEvaluator negative predictions failed: {e}")
        raise


def test_evaluators_with_real_model_predictions(iris_data, diabetes_data):
    """Test evaluators: with real model predictions."""
    try:
        from worker.ml.trainers import LogisticRegressionTrainer, LinearRegressionTrainer
        
        # Classification
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = iris_data
        clf = LogisticRegressionTrainer("clf", "classification")
        clf.fit(X_train_clf, y_train_clf)
        y_pred_clf = clf.predict(X_test_clf)
        y_proba_clf = clf.predict_proba(X_test_clf)
        
        clf_evaluator = ClassificationEvaluator()
        clf_metrics = clf_evaluator.evaluate(y_test_clf, y_pred_clf, y_pred_proba=y_proba_clf)
        
        assert clf_metrics["accuracy"] > 0.5  # Should be better than random
        assert "confusion_matrix" in clf_metrics
        
        # Regression
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = diabetes_data
        reg = LinearRegressionTrainer("reg", "regression")
        reg.fit(X_train_reg, y_train_reg)
        y_pred_reg = reg.predict(X_test_reg)
        
        reg_evaluator = RegressionEvaluator()
        reg_metrics = reg_evaluator.evaluate(y_test_reg, y_pred_reg)
        
        assert reg_metrics["r2_score"] > 0  # Should explain some variance
        assert reg_metrics["mse"] > 0
        
        print("✅ Evaluators with real model predictions passed")
        
    except Exception as e:
        print(f"❌ Evaluators with real model predictions failed: {e}")
        raise