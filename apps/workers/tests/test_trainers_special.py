"""
Special feature tests - predict_proba, feature_importance, dual-task behavior.
Tests optional methods and special capabilities.
"""

import pytest
import numpy as np
from worker.ml.trainers import (
    LogisticRegressionTrainer,
    NaiveBayesTrainer,
    KNNTrainer,
    DecisionTreeTrainer,
    RandomForestTrainer,
    XGBoostTrainer,
    LinearRegressionTrainer,
    NeuralNetworkTrainer,
)


def test_logistic_regression_predict_proba(iris_data):
    """Test LogisticRegression: predict_proba returns valid probabilities."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = LogisticRegressionTrainer("lr_proba", "classification")
        trainer.fit(X_train, y_train)
        
        # Get probabilities
        probas = trainer.predict_proba(X_test)
        
        # Check shape
        n_classes = len(np.unique(y_train))
        assert probas.shape == (len(X_test), n_classes)
        
        # Check probabilities sum to 1
        sums = np.sum(probas, axis=1)
        np.testing.assert_array_almost_equal(sums, np.ones(len(X_test)))
        
        # Check all probabilities are between 0 and 1
        assert np.all(probas >= 0)
        assert np.all(probas <= 1)
        
        print("✅ LogisticRegression predict_proba passed")
        
    except Exception as e:
        print(f"❌ LogisticRegression predict_proba failed: {e}")
        raise


def test_naive_bayes_predict_proba(iris_data):
    """Test NaiveBayes: predict_proba returns valid probabilities."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = NaiveBayesTrainer("nb_proba", "classification")
        trainer.fit(X_train, y_train)
        
        probas = trainer.predict_proba(X_test)
        
        n_classes = len(np.unique(y_train))
        assert probas.shape == (len(X_test), n_classes)
        
        sums = np.sum(probas, axis=1)
        np.testing.assert_array_almost_equal(sums, np.ones(len(X_test)))
        
        print("✅ NaiveBayes predict_proba passed")
        
    except Exception as e:
        print(f"❌ NaiveBayes predict_proba failed: {e}")
        raise


def test_knn_predict_proba(iris_data):
    """Test KNN: predict_proba returns valid probabilities for classification."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = KNNTrainer("knn_proba", "classification")
        trainer.fit(X_train, y_train)
        
        probas = trainer.predict_proba(X_test)
        
        n_classes = len(np.unique(y_train))
        assert probas.shape == (len(X_test), n_classes)
        
        sums = np.sum(probas, axis=1)
        np.testing.assert_array_almost_equal(sums, np.ones(len(X_test)))
        
        print("✅ KNN predict_proba passed")
        
    except Exception as e:
        print(f"❌ KNN predict_proba failed: {e}")
        raise


def test_decision_tree_feature_importance(iris_data):
    """Test DecisionTree: get_feature_importance returns valid array."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = DecisionTreeTrainer("dt_importance", "classification")
        trainer.fit(X_train, y_train)
        
        # Get feature importance
        importances = trainer.get_feature_importance()
        
        # Check shape
        assert importances.shape == (X_train.shape[1],)
        
        # Check sum to 1 (normalized)
        assert np.isclose(np.sum(importances), 1.0)
        
        # Check all non-negative
        assert np.all(importances >= 0)
        
        print("✅ DecisionTree feature_importance passed")
        
    except Exception as e:
        print(f"❌ DecisionTree feature_importance failed: {e}")
        raise


def test_random_forest_feature_importance(iris_data):
    """Test RandomForest: get_feature_importance returns valid array."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = RandomForestTrainer("rf_importance", "classification")
        trainer.fit(X_train, y_train)
        
        importances = trainer.get_feature_importance()
        
        assert importances.shape == (X_train.shape[1],)
        assert np.isclose(np.sum(importances), 1.0)
        assert np.all(importances >= 0)
        
        print("✅ RandomForest feature_importance passed")
        
    except Exception as e:
        print(f"❌ RandomForest feature_importance failed: {e}")
        raise


def test_xgboost_feature_importance(iris_data):
    """Test XGBoost: get_feature_importance returns valid array."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = XGBoostTrainer("xgb_importance", "classification", use_gpu=False)
        trainer.fit(X_train, y_train)
        
        importances = trainer.get_feature_importance()
        
        assert importances.shape == (X_train.shape[1],)
        # XGBoost importance doesn't necessarily sum to 1
        assert np.all(importances >= 0)
        
        print("✅ XGBoost feature_importance passed")
        
    except Exception as e:
        print(f"❌ XGBoost feature_importance failed: {e}")
        raise


def test_linear_regression_feature_importance(diabetes_data):
    """Test LinearRegression: get_feature_importance returns valid array (coefficients)."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        trainer = LinearRegressionTrainer("linreg_importance", "regression")
        trainer.fit(X_train, y_train)
        
        importances = trainer.get_feature_importance()
        
        # Check shape
        assert importances.shape == (X_train.shape[1],)
        
        # Check all non-negative (absolute values of coefficients)
        assert np.all(importances >= 0)
        
        print("✅ LinearRegression feature_importance passed")
        
    except Exception as e:
        print(f"❌ LinearRegression feature_importance failed: {e}")
        raise


def test_knn_dual_task_classification(iris_data):
    """Test KNN: works correctly for classification task."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = KNNTrainer("knn_dual_clf", "classification")
        trainer.fit(X_train, y_train)
        predictions = trainer.predict(X_test)
        
        # Should return integer class labels
        assert predictions.dtype in [np.int32, np.int64]
        
        # Should have predict_proba
        probas = trainer.predict_proba(X_test)
        assert probas.shape[0] == len(X_test)
        
        print("✅ KNN dual-task (classification) passed")
        
    except Exception as e:
        print(f"❌ KNN dual-task (classification) failed: {e}")
        raise


def test_knn_dual_task_regression(diabetes_data):
    """Test KNN: works correctly for regression task."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        trainer = KNNTrainer("knn_dual_reg", "regression")
        trainer.fit(X_train, y_train)
        predictions = trainer.predict(X_test)
        
        # Should return float values
        assert predictions.dtype in [np.float32, np.float64]
        
        # Should NOT have predict_proba for regression
        with pytest.raises(NotImplementedError):
            trainer.predict_proba(X_test)
        
        print("✅ KNN dual-task (regression) passed")
        
    except Exception as e:
        print(f"❌ KNN dual-task (regression) failed: {e}")
        raise


def test_decision_tree_dual_task(iris_data, diabetes_data):
    """Test DecisionTree: works for both classification and regression."""
    try:
        # Classification
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = iris_data
        trainer_clf = DecisionTreeTrainer("dt_dual_clf", "classification")
        trainer_clf.fit(X_train_clf, y_train_clf)
        pred_clf = trainer_clf.predict(X_test_clf)
        assert pred_clf.dtype in [np.int32, np.int64]
        
        # Regression
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = diabetes_data
        trainer_reg = DecisionTreeTrainer("dt_dual_reg", "regression")
        trainer_reg.fit(X_train_reg, y_train_reg)
        pred_reg = trainer_reg.predict(X_test_reg)
        assert pred_reg.dtype in [np.float32, np.float64]
        
        print("✅ DecisionTree dual-task passed")
        
    except Exception as e:
        print(f"❌ DecisionTree dual-task failed: {e}")
        raise


def test_random_forest_dual_task(iris_data, diabetes_data):
    """Test RandomForest: works for both classification and regression."""
    try:
        # Classification
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = iris_data
        trainer_clf = RandomForestTrainer("rf_dual_clf", "classification")
        trainer_clf.fit(X_train_clf, y_train_clf)
        pred_clf = trainer_clf.predict(X_test_clf)
        assert pred_clf.dtype in [np.int32, np.int64]
        
        # Regression
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = diabetes_data
        trainer_reg = RandomForestTrainer("rf_dual_reg", "regression")
        trainer_reg.fit(X_train_reg, y_train_reg)
        pred_reg = trainer_reg.predict(X_test_reg)
        assert pred_reg.dtype in [np.float32, np.float64]
        
        print("✅ RandomForest dual-task passed")
        
    except Exception as e:
        print(f"❌ RandomForest dual-task failed: {e}")
        raise


def test_xgboost_dual_task(iris_data, diabetes_data):
    """Test XGBoost: works for both classification and regression."""
    try:
        # Classification
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = iris_data
        trainer_clf = XGBoostTrainer("xgb_dual_clf", "classification", use_gpu=False)
        trainer_clf.fit(X_train_clf, y_train_clf)
        pred_clf = trainer_clf.predict(X_test_clf)
        assert pred_clf.dtype in [np.int32, np.int64]
        
        # Regression
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = diabetes_data
        trainer_reg = XGBoostTrainer("xgb_dual_reg", "regression", use_gpu=False)
        trainer_reg.fit(X_train_reg, y_train_reg)
        pred_reg = trainer_reg.predict(X_test_reg)
        assert pred_reg.dtype in [np.float32, np.float64]
        
        print("✅ XGBoost dual-task passed")
        
    except Exception as e:
        print(f"❌ XGBoost dual-task failed: {e}")
        raise


def test_neural_network_dual_task(iris_data, diabetes_data):
    """Test NeuralNetwork: works for both classification and regression."""
    try:
        # Classification
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = iris_data
        trainer_clf = NeuralNetworkTrainer("nn_dual_clf", "classification")
        trainer_clf.fit(X_train_clf, y_train_clf)
        pred_clf = trainer_clf.predict(X_test_clf)
        assert pred_clf.dtype in [np.int32, np.int64]
        
        # Regression
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = diabetes_data
        trainer_reg = NeuralNetworkTrainer("nn_dual_reg", "regression")
        trainer_reg.fit(X_train_reg, y_train_reg)
        pred_reg = trainer_reg.predict(X_test_reg)
        assert pred_reg.dtype in [np.float32, np.float64]
        
        print("✅ NeuralNetwork dual-task passed")
        
    except Exception as e:
        print(f"❌ NeuralNetwork dual-task failed: {e}")
        raise


def test_model_type_constants():
    """Test all trainers return correct model type constants."""
    try:
        from worker.constants import (
            MODEL_TYPE_LINEAR,
            MODEL_TYPE_TREE,
            MODEL_TYPE_NEURAL,
            MODEL_TYPE_DISTANCE,
            MODEL_TYPE_CLUSTERING,
            MODEL_TYPE_DIMENSIONALITY,
        )
        
        # Create dummy data
        X = np.random.rand(10, 4)
        y = np.random.randint(0, 2, 10)
        
        # Linear models
        lr = LogisticRegressionTrainer("lr", "classification")
        assert lr.get_model_type() == MODEL_TYPE_LINEAR
        
        nb = NaiveBayesTrainer("nb", "classification")
        assert nb.get_model_type() == MODEL_TYPE_LINEAR
        
        # Distance models
        knn = KNNTrainer("knn", "classification")
        assert knn.get_model_type() == MODEL_TYPE_DISTANCE
        
        # Tree models
        dt = DecisionTreeTrainer("dt", "classification")
        assert dt.get_model_type() == MODEL_TYPE_TREE
        
        rf = RandomForestTrainer("rf", "classification")
        assert rf.get_model_type() == MODEL_TYPE_TREE
        
        xgb = XGBoostTrainer("xgb", "classification", use_gpu=False)
        assert xgb.get_model_type() == MODEL_TYPE_TREE
        
        # Neural models
        nn = NeuralNetworkTrainer("nn", "classification")
        assert nn.get_model_type() == MODEL_TYPE_NEURAL
        
        print("✅ Model type constants passed")
        
    except Exception as e:
        print(f"❌ Model type constants failed: {e}")
        raise