"""
Basic trainer tests - instantiation, fit, predict.
Tests fundamental functionality for all 10 trainers.
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
    KMeansTrainer,
    PCATrainer,
    NeuralNetworkTrainer,
)


def test_logistic_regression_basic(iris_data):
    """Test LogisticRegression: instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = LogisticRegressionTrainer(
            name="lr_test",
            task="classification"
        )
        assert trainer.name == "lr_test"
        assert trainer.task == "classification"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        # Check predictions are valid class labels
        assert set(predictions).issubset(set([0, 1, 2]))
        
        print("✅ LogisticRegression basic tests passed")
        
    except Exception as e:
        print(f"❌ LogisticRegression basic tests failed: {e}")
        raise


def test_naive_bayes_basic(iris_data):
    """Test NaiveBayes: instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = NaiveBayesTrainer(
            name="nb_test",
            task="classification"
        )
        assert trainer.name == "nb_test"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        print("✅ NaiveBayes basic tests passed")
        
    except Exception as e:
        print(f"❌ NaiveBayes basic tests failed: {e}")
        raise


def test_knn_classification_basic(iris_data):
    """Test KNN (classification): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = KNNTrainer(
            name="knn_clf_test",
            task="classification"
        )
        assert trainer.task == "classification"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        print("✅ KNN (classification) basic tests passed")
        
    except Exception as e:
        print(f"❌ KNN (classification) basic tests failed: {e}")
        raise


def test_knn_regression_basic(diabetes_data):
    """Test KNN (regression): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        # Instantiate
        trainer = KNNTrainer(
            name="knn_reg_test",
            task="regression"
        )
        assert trainer.task == "regression"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.float32, np.float64]
        
        print("✅ KNN (regression) basic tests passed")
        
    except Exception as e:
        print(f"❌ KNN (regression) basic tests failed: {e}")
        raise


def test_decision_tree_classification_basic(iris_data):
    """Test DecisionTree (classification): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = DecisionTreeTrainer(
            name="dt_clf_test",
            task="classification"
        )
        assert trainer.task == "classification"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        print("✅ DecisionTree (classification) basic tests passed")
        
    except Exception as e:
        print(f"❌ DecisionTree (classification) basic tests failed: {e}")
        raise


def test_decision_tree_regression_basic(diabetes_data):
    """Test DecisionTree (regression): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        # Instantiate
        trainer = DecisionTreeTrainer(
            name="dt_reg_test",
            task="regression"
        )
        assert trainer.task == "regression"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.float32, np.float64]
        
        print("✅ DecisionTree (regression) basic tests passed")
        
    except Exception as e:
        print(f"❌ DecisionTree (regression) basic tests failed: {e}")
        raise


def test_random_forest_classification_basic(iris_data):
    """Test RandomForest (classification): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = RandomForestTrainer(
            name="rf_clf_test",
            task="classification"
        )
        assert trainer.task == "classification"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        print("✅ RandomForest (classification) basic tests passed")
        
    except Exception as e:
        print(f"❌ RandomForest (classification) basic tests failed: {e}")
        raise


def test_random_forest_regression_basic(diabetes_data):
    """Test RandomForest (regression): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        # Instantiate
        trainer = RandomForestTrainer(
            name="rf_reg_test",
            task="regression"
        )
        assert trainer.task == "regression"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.float32, np.float64]
        
        print("✅ RandomForest (regression) basic tests passed")
        
    except Exception as e:
        print(f"❌ RandomForest (regression) basic tests failed: {e}")
        raise


def test_xgboost_classification_basic(iris_data):
    """Test XGBoost (classification): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = XGBoostTrainer(
            name="xgb_clf_test",
            task="classification",
            use_gpu=False
        )
        assert trainer.task == "classification"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        print("✅ XGBoost (classification) basic tests passed")
        
    except Exception as e:
        print(f"❌ XGBoost (classification) basic tests failed: {e}")
        raise


def test_xgboost_regression_basic(diabetes_data):
    """Test XGBoost (regression): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        # Instantiate
        trainer = XGBoostTrainer(
            name="xgb_reg_test",
            task="regression",
            use_gpu=False
        )
        assert trainer.task == "regression"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.float32, np.float64]
        
        print("✅ XGBoost (regression) basic tests passed")
        
    except Exception as e:
        print(f"❌ XGBoost (regression) basic tests failed: {e}")
        raise


def test_linear_regression_basic(diabetes_data):
    """Test LinearRegression: instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        # Instantiate
        trainer = LinearRegressionTrainer(
            name="linreg_test",
            task="regression"
        )
        assert trainer.task == "regression"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.float32, np.float64]
        
        print("✅ LinearRegression basic tests passed")
        
    except Exception as e:
        print(f"❌ LinearRegression basic tests failed: {e}")
        raise


def test_kmeans_basic(iris_unsupervised):
    """Test KMeans: instantiate, fit, predict."""
    try:
        X_train, X_test = iris_unsupervised
        
        # Instantiate
        trainer = KMeansTrainer(
            name="kmeans_test",
            task="clustering"
        )
        assert trainer.task == "clustering"
        
        # Fit (y is None for unsupervised)
        trainer.fit(X_train, y=None)
        assert trainer.model is not None
        
        # Predict (returns cluster IDs)
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        # Check cluster IDs are in valid range
        n_clusters = trainer.hyperparameters["n_clusters"]
        assert set(predictions).issubset(set(range(n_clusters)))
        
        print("✅ KMeans basic tests passed")
        
    except Exception as e:
        print(f"❌ KMeans basic tests failed: {e}")
        raise


def test_pca_basic(iris_unsupervised):
    """Test PCA: instantiate, fit, predict (transform)."""
    try:
        X_train, X_test = iris_unsupervised
        
        # Instantiate
        trainer = PCATrainer(
            name="pca_test",
            task="dimensionality_reduction"
        )
        assert trainer.task == "dimensionality_reduction"
        
        # Fit (y is None for unsupervised)
        trainer.fit(X_train, y=None)
        assert trainer.model is not None
        
        # Predict (returns transformed features)
        transformed = trainer.predict(X_test)
        assert transformed.shape[0] == len(X_test)
        assert transformed.shape[1] == trainer.hyperparameters["n_components"]
        assert transformed.dtype in [np.float32, np.float64]
        
        print("✅ PCA basic tests passed")
        
    except Exception as e:
        print(f"❌ PCA basic tests failed: {e}")
        raise


def test_neural_network_classification_basic(iris_data):
    """Test NeuralNetwork (classification): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Instantiate
        trainer = NeuralNetworkTrainer(
            name="nn_clf_test",
            task="classification"
        )
        assert trainer.task == "classification"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.int32, np.int64]
        
        print("✅ NeuralNetwork (classification) basic tests passed")
        
    except Exception as e:
        print(f"❌ NeuralNetwork (classification) basic tests failed: {e}")
        raise


def test_neural_network_regression_basic(diabetes_data):
    """Test NeuralNetwork (regression): instantiate, fit, predict."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        # Instantiate
        trainer = NeuralNetworkTrainer(
            name="nn_reg_test",
            task="regression"
        )
        assert trainer.task == "regression"
        
        # Fit
        trainer.fit(X_train, y_train)
        assert trainer.model is not None
        
        # Predict
        predictions = trainer.predict(X_test)
        assert predictions.shape == (len(X_test),)
        assert predictions.dtype in [np.float32, np.float64]
        
        print("✅ NeuralNetwork (regression) basic tests passed")
        
    except Exception as e:
        print(f"❌ NeuralNetwork (regression) basic tests failed: {e}")
        raise