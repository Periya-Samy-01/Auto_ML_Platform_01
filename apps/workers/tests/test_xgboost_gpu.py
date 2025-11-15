"""
XGBoost GPU tests - platform-controlled GPU access.
Tests that GPU support is properly secured and controlled by backend.
"""

import pytest
import numpy as np
from worker.ml.trainers import XGBoostTrainer


def test_xgboost_gpu_disabled_by_default():
    """Test XGBoost: use_gpu=False (default) forces CPU."""
    try:
        trainer = XGBoostTrainer(
            name="xgb_cpu",
            task="classification",
            use_gpu=False  # Free user
        )
        
        # Check tree_method is CPU-based or not set
        tree_method = trainer.hyperparameters.get("tree_method", "hist")
        assert "gpu" not in tree_method.lower()
        
        print("✅ XGBoost GPU disabled by default passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU disabled by default failed: {e}")
        raise


def test_xgboost_gpu_enabled_for_pro():
    """Test XGBoost: use_gpu=True enables GPU for pro users."""
    try:
        trainer = XGBoostTrainer(
            name="xgb_gpu",
            task="classification",
            use_gpu=True  # Pro user
        )
        
        # Check tree_method is set to GPU
        assert trainer.hyperparameters["tree_method"] == "gpu_hist"
        
        print("✅ XGBoost GPU enabled for pro users passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU enabled for pro users failed: {e}")
        raise


def test_xgboost_gpu_security_free_user_attempts_gpu():
    """Test XGBoost: free user trying to enable GPU is blocked."""
    try:
        # Free user tries to set GPU in hyperparameters
        trainer = XGBoostTrainer(
            name="xgb_hack",
            task="classification",
            hyperparameters={"tree_method": "gpu_hist"},  # Attempt to bypass
            use_gpu=False  # Backend says: NOT a pro user
        )
        
        # Should be overridden to CPU
        assert trainer.hyperparameters["tree_method"] == "hist"  # Forced to CPU
        assert "gpu" not in trainer.hyperparameters["tree_method"].lower()
        
        print("✅ XGBoost GPU security (blocking free user) passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU security (blocking free user) failed: {e}")
        raise


def test_xgboost_gpu_security_case_insensitive():
    """Test XGBoost: GPU blocking works with different cases."""
    try:
        # Try different GPU string variations
        variations = ["GPU_hist", "Gpu_Hist", "gpu_HIST"]
        
        for variation in variations:
            trainer = XGBoostTrainer(
                name=f"xgb_{variation}",
                task="classification",
                hyperparameters={"tree_method": variation},
                use_gpu=False  # Free user
            )
            
            # All should be blocked
            assert "gpu" not in trainer.hyperparameters["tree_method"].lower()
        
        print("✅ XGBoost GPU security (case-insensitive) passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU security (case-insensitive) failed: {e}")
        raise


def test_xgboost_gpu_pro_user_can_override():
    """Test XGBoost: pro user can override tree_method if desired."""
    try:
        # Pro user with use_gpu=True but wants specific tree_method
        trainer = XGBoostTrainer(
            name="xgb_pro_custom",
            task="classification",
            hyperparameters={"tree_method": "approx"},  # Custom method
            use_gpu=True  # Pro user
        )
        
        # Since use_gpu=True, it should default to gpu_hist UNLESS user explicitly set something
        # Our implementation uses setdefault, so user's "approx" should be kept
        assert trainer.hyperparameters["tree_method"] == "approx"
        
        print("✅ XGBoost GPU pro user override passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU pro user override failed: {e}")
        raise


def test_xgboost_with_gpu_flag_trains_successfully(iris_data):
    """Test XGBoost: can train successfully with both GPU flags."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # CPU training (free user)
        trainer_cpu = XGBoostTrainer("xgb_cpu", "classification", use_gpu=False)
        trainer_cpu.fit(X_train, y_train)
        pred_cpu = trainer_cpu.predict(X_test)
        assert pred_cpu is not None
        assert len(pred_cpu) == len(X_test)
        
        # GPU training (pro user) - may fail if no GPU available, but API should work
        trainer_gpu = XGBoostTrainer("xgb_gpu", "classification", use_gpu=True)
        
        # Check tree_method is set correctly
        assert trainer_gpu.hyperparameters["tree_method"] == "gpu_hist"
        
        # Note: We can't actually test GPU training in CI without GPU
        # But we can verify the parameter is set correctly
        
        print("✅ XGBoost GPU flag training passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU flag training failed: {e}")
        raise


def test_xgboost_gpu_flag_persists_after_save_load(iris_data, temp_model_dir):
    """Test XGBoost: GPU settings persist after save/load."""
    try:
        X_train, X_test, y_train, y_test = iris_data
        
        # Train with GPU enabled
        trainer = XGBoostTrainer("xgb_gpu_persist", "classification", use_gpu=True)
        trainer.fit(X_train, y_train)
        
        # Verify GPU setting
        assert trainer.hyperparameters["tree_method"] == "gpu_hist"
        
        # Save model
        save_path = str(temp_model_dir / "xgb_gpu_model")
        trainer.save(save_path)
        
        # Load model
        loaded_trainer = XGBoostTrainer.load(save_path)
        
        # GPU setting should be preserved
        assert loaded_trainer.hyperparameters["tree_method"] == "gpu_hist"
        
        print("✅ XGBoost GPU flag persistence passed")
        
    except Exception as e:
        print(f"❌ XGBoost GPU flag persistence failed: {e}")
        raise


def test_xgboost_default_hyperparameters_without_gpu():
    """Test XGBoost: default hyperparameters work without GPU flag."""
    try:
        # No use_gpu parameter (defaults to False)
        trainer = XGBoostTrainer("xgb_default", "classification")
        
        # Should have all default hyperparameters
        assert "n_estimators" in trainer.hyperparameters
        assert "max_depth" in trainer.hyperparameters
        assert "learning_rate" in trainer.hyperparameters
        
        # tree_method should not be GPU
        tree_method = trainer.hyperparameters.get("tree_method", "hist")
        assert "gpu" not in tree_method.lower()
        
        print("✅ XGBoost default hyperparameters passed")
        
    except Exception as e:
        print(f"❌ XGBoost default hyperparameters failed: {e}")
        raise