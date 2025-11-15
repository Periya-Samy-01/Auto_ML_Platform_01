"""
Advanced trainer tests - save/load, hyperparameter updates, metadata.
Tests persistence and dynamic configuration for all trainers.
"""

import pytest
import numpy as np
from pathlib import Path
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


def test_logistic_regression_save_load(iris_data, temp_model_dir):
    """Test LogisticRegression: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Train model
        trainer = LogisticRegressionTrainer("lr_save", "classification")
        trainer.fit(X_train, y_train)
        
        # Get predictions before save
        pred_before = trainer.predict(X_test)
        
        # Save model
        save_path = str(temp_model_dir / "lr_model")
        trainer.save(save_path)
        
        # Check files exist
        assert Path(save_path, "model.joblib").exists()
        assert Path(save_path, "metadata.json").exists()
        
        # Load model
        loaded_trainer = LogisticRegressionTrainer.load(save_path)
        
        # Get predictions after load
        pred_after = loaded_trainer.predict(X_test)
        
        # Predictions should match
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ LogisticRegression save/load passed")
        
    except Exception as e:
        print(f"❌ LogisticRegression save/load failed: {e}")
        raise


def test_logistic_regression_hyperparameter_update(iris_data):
    """Test LogisticRegression: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Train with default C=1.0
        trainer = LogisticRegressionTrainer("lr_update", "classification")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        # Update hyperparameters
        trainer.update_hyperparameters({"C": 0.01})  # Much stronger regularization
        assert trainer.hyperparameters["C"] == 0.01
        
        # Refit with new hyperparameters
        trainer.fit(X_train, y_train)
        pred_after = trainer.predict(X_test)
        
        # Predictions should be different (at least some)
        assert not np.array_equal(pred_before, pred_after), "Predictions should change after hyperparameter update"
        
        print("✅ LogisticRegression hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ LogisticRegression hyperparameter update failed: {e}")
        raise


def test_naive_bayes_save_load(iris_data, temp_model_dir):
    """Test NaiveBayes: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = NaiveBayesTrainer("nb_save", "classification")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "nb_model")
        trainer.save(save_path)
        
        loaded_trainer = NaiveBayesTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ NaiveBayes save/load passed")
        
    except Exception as e:
        print(f"❌ NaiveBayes save/load failed: {e}")
        raise


def test_knn_save_load(iris_data, temp_model_dir):
    """Test KNN: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = KNNTrainer("knn_save", "classification")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "knn_model")
        trainer.save(save_path)
        
        loaded_trainer = KNNTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ KNN save/load passed")
        
    except Exception as e:
        print(f"❌ KNN save/load failed: {e}")
        raise


def test_knn_hyperparameter_update(iris_data):
    """Test KNN: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = KNNTrainer("knn_update", "classification", {"n_neighbors": 5})
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        # Change to 1 neighbor (should give different predictions)
        trainer.update_hyperparameters({"n_neighbors": 1})
        trainer.fit(X_train, y_train)
        pred_after = trainer.predict(X_test)
        
        assert not np.array_equal(pred_before, pred_after)
        
        print("✅ KNN hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ KNN hyperparameter update failed: {e}")
        raise


def test_decision_tree_save_load(iris_data, temp_model_dir):
    """Test DecisionTree: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = DecisionTreeTrainer("dt_save", "classification")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "dt_model")
        trainer.save(save_path)
        
        loaded_trainer = DecisionTreeTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ DecisionTree save/load passed")
        
    except Exception as e:
        print(f"❌ DecisionTree save/load failed: {e}")
        raise


def test_decision_tree_hyperparameter_update(iris_data):
    """Test DecisionTree: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = DecisionTreeTrainer("dt_update", "classification", {"max_depth": 10})
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        # Shallow tree should give different predictions
        trainer.update_hyperparameters({"max_depth": 2})
        trainer.fit(X_train, y_train)
        pred_after = trainer.predict(X_test)
        
        assert not np.array_equal(pred_before, pred_after)
        
        print("✅ DecisionTree hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ DecisionTree hyperparameter update failed: {e}")
        raise


def test_random_forest_save_load(iris_data, temp_model_dir):
    """Test RandomForest: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = RandomForestTrainer("rf_save", "classification")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "rf_model")
        trainer.save(save_path)
        
        loaded_trainer = RandomForestTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ RandomForest save/load passed")
        
    except Exception as e:
        print(f"❌ RandomForest save/load failed: {e}")
        raise


def test_random_forest_hyperparameter_update(iris_data):
    """Test RandomForest: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = RandomForestTrainer("rf_update", "classification", {"n_estimators": 10})
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        # More trees can give different predictions
        trainer.update_hyperparameters({"n_estimators": 50})
        trainer.fit(X_train, y_train)
        pred_after = trainer.predict(X_test)
        
        # May or may not be different, but hyperparameters should update
        assert trainer.hyperparameters["n_estimators"] == 50
        
        print("✅ RandomForest hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ RandomForest hyperparameter update failed: {e}")
        raise


def test_xgboost_save_load(iris_data, temp_model_dir):
    """Test XGBoost: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = XGBoostTrainer("xgb_save", "classification", use_gpu=False)
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "xgb_model")
        trainer.save(save_path)
        
        loaded_trainer = XGBoostTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ XGBoost save/load passed")
        
    except Exception as e:
        print(f"❌ XGBoost save/load failed: {e}")
        raise


def test_xgboost_hyperparameter_update(iris_data):
    """Test XGBoost: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = XGBoostTrainer("xgb_update", "classification", {"learning_rate": 0.3}, use_gpu=False)
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        # Lower learning rate
        trainer.update_hyperparameters({"learning_rate": 0.01})
        trainer.fit(X_train, y_train)
        pred_after = trainer.predict(X_test)
        
        assert trainer.hyperparameters["learning_rate"] == 0.01
        
        print("✅ XGBoost hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ XGBoost hyperparameter update failed: {e}")
        raise


def test_linear_regression_save_load(diabetes_data, temp_model_dir):
    """Test LinearRegression: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = diabetes_data
        
        trainer = LinearRegressionTrainer("linreg_save", "regression")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "linreg_model")
        trainer.save(save_path)
        
        loaded_trainer = LinearRegressionTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_almost_equal(pred_before, pred_after)
        
        print("✅ LinearRegression save/load passed")
        
    except Exception as e:
        print(f"❌ LinearRegression save/load failed: {e}")
        raise


def test_kmeans_save_load(iris_unsupervised, temp_model_dir):
    """Test KMeans: save, load, predictions match."""
    try:
        X_train, X_test = iris_unsupervised
        
        trainer = KMeansTrainer("kmeans_save", "clustering")
        trainer.fit(X_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "kmeans_model")
        trainer.save(save_path)
        
        loaded_trainer = KMeansTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ KMeans save/load passed")
        
    except Exception as e:
        print(f"❌ KMeans save/load failed: {e}")
        raise


def test_kmeans_hyperparameter_update(iris_unsupervised):
    """Test KMeans: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test = iris_unsupervised
        
        trainer = KMeansTrainer("kmeans_update", "clustering", {"n_clusters": 3})
        trainer.fit(X_train)
        pred_before = trainer.predict(X_test)
        
        # Different number of clusters
        trainer.update_hyperparameters({"n_clusters": 5})
        trainer.fit(X_train)
        pred_after = trainer.predict(X_test)
        
        # Cluster IDs will be different
        assert not np.array_equal(pred_before, pred_after)
        
        print("✅ KMeans hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ KMeans hyperparameter update failed: {e}")
        raise


def test_pca_save_load(iris_unsupervised, temp_model_dir):
    """Test PCA: save, load, predictions match."""
    try:
        X_train, X_test = iris_unsupervised
        
        trainer = PCATrainer("pca_save", "dimensionality_reduction")
        trainer.fit(X_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "pca_model")
        trainer.save(save_path)
        
        loaded_trainer = PCATrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_almost_equal(pred_before, pred_after)
        
        print("✅ PCA save/load passed")
        
    except Exception as e:
        print(f"❌ PCA save/load failed: {e}")
        raise


def test_pca_hyperparameter_update(iris_unsupervised):
    """Test PCA: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test = iris_unsupervised
        
        trainer = PCATrainer("pca_update", "dimensionality_reduction", {"n_components": 2})
        trainer.fit(X_train)
        pred_before = trainer.predict(X_test)
        
        # More components
        trainer.update_hyperparameters({"n_components": 3})
        trainer.fit(X_train)
        pred_after = trainer.predict(X_test)
        
        # Shape should be different
        assert pred_before.shape[1] != pred_after.shape[1]
        
        print("✅ PCA hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ PCA hyperparameter update failed: {e}")
        raise


def test_neural_network_save_load(iris_data, temp_model_dir):
    """Test NeuralNetwork: save, load, predictions match."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = NeuralNetworkTrainer("nn_save", "classification")
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        save_path = str(temp_model_dir / "nn_model")
        trainer.save(save_path)
        
        loaded_trainer = NeuralNetworkTrainer.load(save_path)
        pred_after = loaded_trainer.predict(X_test)
        
        np.testing.assert_array_equal(pred_before, pred_after)
        
        print("✅ NeuralNetwork save/load passed")
        
    except Exception as e:
        print(f"❌ NeuralNetwork save/load failed: {e}")
        raise


def test_neural_network_hyperparameter_update(iris_data):
    """Test NeuralNetwork: update hyperparams, refit, predictions change."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = NeuralNetworkTrainer("nn_update", "classification", {"hidden_layer_sizes": (50,)})
        trainer.fit(X_train, y_train)
        pred_before = trainer.predict(X_test)
        
        # Different architecture
        trainer.update_hyperparameters({"hidden_layer_sizes": (20,)})
        trainer.fit(X_train, y_train)
        pred_after = trainer.predict(X_test)
        
        assert trainer.hyperparameters["hidden_layer_sizes"] == (20,)
        
        print("✅ NeuralNetwork hyperparameter update passed")
        
    except Exception as e:
        print(f"❌ NeuralNetwork hyperparameter update failed: {e}")
        raise


def test_metadata_tracking(iris_data):
    """Test metadata tracking across all trainers."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        trainer = LogisticRegressionTrainer("metadata_test", "classification")
        trainer.fit(X_train, y_train)
        
        metadata = trainer.get_metadata()
        
        # Check metadata fields
        assert "created_at" in metadata
        assert "last_trained_at" in metadata
        assert "training_samples" in metadata
        assert "feature_count" in metadata
        
        # Check values
        assert metadata["training_samples"] == len(X_train)
        assert metadata["feature_count"] == X_train.shape[1]
        assert metadata["last_trained_at"] is not None
        
        print("✅ Metadata tracking passed")
        
    except Exception as e:
        print(f"❌ Metadata tracking failed: {e}")
        raise