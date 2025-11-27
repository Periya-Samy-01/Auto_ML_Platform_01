"""
Error handling tests - validation, edge cases, error messages.
Tests that trainers fail gracefully with appropriate error messages.
"""

import pytest
import numpy as np
from worker.ml.trainers import (
    LogisticRegressionTrainer,
    KNNTrainer,
    DecisionTreeTrainer,
    RandomForestTrainer,
    XGBoostTrainer,
    KMeansTrainer,
    NeuralNetworkTrainer,
)


def test_predict_before_fit():
    """Test all trainers: predict before fit raises ValueError."""
    try:
        X_test = np.random.rand(10, 4)
        
        trainers = [
            LogisticRegressionTrainer("lr", "classification"),
            KNNTrainer("knn", "classification"),
            DecisionTreeTrainer("dt", "classification"),
        ]
        
        for trainer in trainers:
            with pytest.raises(ValueError, match="not been fitted"):
                trainer.predict(X_test)
        
        print("✅ Predict-before-fit error handling passed")
        
    except Exception as e:
        print(f"❌ Predict-before-fit error handling failed: {e}")
        raise


def test_invalid_hyperparameters_negative_values():
    """Test validation: negative hyperparameter values raise ValueError."""
    try:
        # Negative C for LogisticRegression
        with pytest.raises(ValueError, match="positive"):
            LogisticRegressionTrainer("lr", "classification", {"C": -1.0})
        
        # Negative n_neighbors for KNN
        with pytest.raises(ValueError, match="positive"):
            KNNTrainer("knn", "classification", {"n_neighbors": -5})
        
        # Negative learning_rate for XGBoost
        with pytest.raises(ValueError, match="positive"):
            XGBoostTrainer("xgb", "classification", {"learning_rate": -0.1}, use_gpu=False)
        
        print("✅ Invalid hyperparameter (negative) validation passed")
        
    except Exception as e:
        print(f"❌ Invalid hyperparameter (negative) validation failed: {e}")
        raise


def test_invalid_hyperparameters_wrong_types():
    """Test validation: wrong type hyperparameters raise ValueError."""
    try:
        # String instead of int for n_neighbors
        with pytest.raises(ValueError, match="integer"):
            KNNTrainer("knn", "classification", {"n_neighbors": "five"})
        
        # String instead of float for C
        with pytest.raises(ValueError, match="number"):
            LogisticRegressionTrainer("lr", "classification", {"C": "one"})
        
        print("✅ Invalid hyperparameter (wrong type) validation passed")
        
    except Exception as e:
        print(f"❌ Invalid hyperparameter (wrong type) validation failed: {e}")
        raise


def test_invalid_probability_values():
    """Test validation: probability values outside [0,1] raise ValueError."""
    try:
        # subsample > 1.0 for XGBoost
        with pytest.raises(ValueError, match="between 0 and 1"):
            XGBoostTrainer("xgb", "classification", {"subsample": 1.5}, use_gpu=False)
        
        # colsample_bytree < 0 for XGBoost
        with pytest.raises(ValueError, match="between 0 and 1"):
            XGBoostTrainer("xgb", "classification", {"colsample_bytree": -0.1}, use_gpu=False)
        
        print("✅ Invalid probability value validation passed")
        
    except Exception as e:
        print(f"❌ Invalid probability value validation failed: {e}")
        raise


def test_mismatched_feature_count(iris_data):
    """Test predict with different feature count raises ValueError."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = LogisticRegressionTrainer("lr", "classification")
        trainer.fit(X_train, y_train)  # Train on 4 features
        
        # Try to predict on 2 features
        X_wrong = np.random.rand(10, 2)
        
        with pytest.raises(ValueError, match="features"):
            trainer.predict(X_wrong)
        
        print("✅ Feature count validation passed")
        
    except Exception as e:
        print(f"❌ Feature count validation failed: {e}")
        raise


def test_supervised_task_requires_y(iris_data):
    """Test supervised tasks: fit without y raises ValueError."""
    try:
        X_train, _, _, _ = iris_data
        
        trainer = LogisticRegressionTrainer("lr", "classification")
        
        with pytest.raises(ValueError, match="requires target"):
            trainer.fit(X_train, y=None)
        
        print("✅ Supervised task y requirement passed")
        
    except Exception as e:
        print(f"❌ Supervised task y requirement failed: {e}")
        raise


def test_unsupervised_task_ignores_y(iris_data):
    """Test unsupervised tasks: y is ignored (no error)."""
    try:
        X_train, X_test, y_train, _ = iris_data
        
        trainer = KMeansTrainer("kmeans", "clustering")
        
        # Should work with y=None
        trainer.fit(X_train, y=None)
        predictions = trainer.predict(X_test)
        assert predictions is not None
        
        # Should also work if y is provided (just ignored)
        trainer2 = KMeansTrainer("kmeans2", "clustering")
        trainer2.fit(X_train, y=y_train)  # y is ignored
        predictions2 = trainer2.predict(X_test)
        assert predictions2 is not None
        
        print("✅ Unsupervised task y handling passed")
        
    except Exception as e:
        print(f"❌ Unsupervised task y handling failed: {e}")
        raise


def test_empty_data_raises_error():
    """Test fit with empty data raises ValueError."""
    try:
        X_empty = np.array([]).reshape(0, 4)
        y_empty = np.array([])
        
        trainer = LogisticRegressionTrainer("lr", "classification")
        
        with pytest.raises(ValueError, match="empty"):
            trainer.fit(X_empty, y_empty)
        
        print("✅ Empty data validation passed")
        
    except Exception as e:
        print(f"❌ Empty data validation failed: {e}")
        raise


def test_wrong_dimensionality_raises_error():
    """Test fit with 1D data raises ValueError."""
    try:
        X_1d = np.random.rand(10)  # Should be 2D
        y = np.random.randint(0, 2, 10)
        
        trainer = LogisticRegressionTrainer("lr", "classification")
        
        with pytest.raises(ValueError, match="2D"):
            trainer.fit(X_1d, y)
        
        print("✅ Data dimensionality validation passed")
        
    except Exception as e:
        print(f"❌ Data dimensionality validation failed: {e}")
        raise


def test_mismatched_sample_count():
    """Test fit with X and y having different sample counts raises ValueError."""
    try:
        X = np.random.rand(10, 4)
        y = np.random.randint(0, 2, 5)  # Wrong size
        
        trainer = LogisticRegressionTrainer("lr", "classification")
        
        with pytest.raises(ValueError, match="same number of samples"):
            trainer.fit(X, y)
        
        print("✅ Sample count validation passed")
        
    except Exception as e:
        print(f"❌ Sample count validation failed: {e}")
        raise


def test_predict_proba_on_regression_raises_error(diabetes_data):
    """Test predict_proba on regression task raises NotImplementedError."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        trainer = KNNTrainer("knn", "regression")
        trainer.fit(X_train, y_train)
        
        with pytest.raises(NotImplementedError, match="only available for classification"):
            trainer.predict_proba(X_test)
        
        print("✅ predict_proba on regression error passed")
        
    except Exception as e:
        print(f"❌ predict_proba on regression error failed: {e}")
        raise


def test_feature_importance_not_implemented():
    """Test feature_importance on models that don't support it raises NotImplementedError."""
    try:
        X_train = np.random.rand(10, 4)
        y_train = np.random.randint(0, 2, 10)
        
        # KNN doesn't have feature importance
        trainer = KNNTrainer("knn", "classification")
        trainer.fit(X_train, y_train)
        
        with pytest.raises(NotImplementedError, match="not available"):
            trainer.get_feature_importance()
        
        print("✅ Feature importance NotImplementedError passed")
        
    except Exception as e:
        print(f"❌ Feature importance NotImplementedError failed: {e}")
        raise


def test_optuna_not_implemented():
    """Test suggest_optuna_params raises NotImplementedError (placeholder for pro feature)."""
    try:
        trainer = LogisticRegressionTrainer("lr", "classification")
        
        with pytest.raises(NotImplementedError, match="Optuna"):
            trainer.suggest_optuna_params(None)
        
        print("✅ Optuna NotImplementedError passed")
        
    except Exception as e:
        print(f"❌ Optuna NotImplementedError failed: {e}")
        raise


def test_neural_network_hidden_layers_must_be_tuple():
    """Test NeuralNetwork: hidden_layer_sizes accepts list and auto-converts to tuple."""
    try:
        # List is accepted and auto-converted to tuple
        trainer = NeuralNetworkTrainer("nn", "classification", {"hidden_layer_sizes": [50]})
        
        # Verify it was auto-converted to tuple
        assert trainer.hyperparameters["hidden_layer_sizes"] == (50,)
        assert isinstance(trainer.hyperparameters["hidden_layer_sizes"], tuple)
        
        # Tuple is also accepted
        trainer2 = NeuralNetworkTrainer("nn2", "classification", {"hidden_layer_sizes": (100, 50)})
        assert trainer2.hyperparameters["hidden_layer_sizes"] == (100, 50)
        assert isinstance(trainer2.hyperparameters["hidden_layer_sizes"], tuple)
        
        print("✅ NeuralNetwork hidden_layer_sizes auto-conversion passed")
        
    except Exception as e:
        print(f"❌ NeuralNetwork hidden_layer_sizes auto-conversion failed: {e}")
        raise

def test_update_hyperparameters_validates():
    """Test update_hyperparameters validates new parameters."""
    try:
        trainer = LogisticRegressionTrainer("lr", "classification")
        
        # Try to update with invalid hyperparameter
        with pytest.raises(ValueError, match="positive"):
            trainer.update_hyperparameters({"C": -1.0})
        
        print("✅ update_hyperparameters validation passed")
        
    except Exception as e:
        print(f"❌ update_hyperparameters validation failed: {e}")
        raise


def test_unsupported_task_raises_error():
    """Test unsupported task for dual-task trainers raises ValueError during fit."""
    try:
        X_train = np.random.rand(10, 4)
        y_train = np.random.randint(0, 2, 10)
        
        # Create trainer with unsupported task
        trainer = KNNTrainer("knn", "unsupported_task")
        
        # Should fail during fit with unsupported task
        with pytest.raises(ValueError, match="Unsupported task"):
            trainer.fit(X_train, y_train)
        
        print("✅ Unsupported task error passed")
        
    except Exception as e:
        print(f"❌ Unsupported task error failed: {e}")
        raise


def test_zero_clusters_raises_error():
    """Test KMeans with n_clusters=0 raises ValueError."""
    try:
        with pytest.raises(ValueError, match="positive"):
            KMeansTrainer("kmeans", "clustering", {"n_clusters": 0})
        
        print("✅ Zero clusters validation passed")
        
    except Exception as e:
        print(f"❌ Zero clusters validation failed: {e}")
        raise


def test_zero_estimators_raises_error():
    """Test RandomForest with n_estimators=0 raises ValueError."""
    try:
        with pytest.raises(ValueError, match="positive"):
            RandomForestTrainer("rf", "classification", {"n_estimators": 0})
        
        print("✅ Zero estimators validation passed")
        
    except Exception as e:
        print(f"❌ Zero estimators validation failed: {e}")
        raise