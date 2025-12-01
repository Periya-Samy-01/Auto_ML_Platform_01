"""
Standalone test for job cost calculation and refund logic
No database required
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from apps.api.app.jobs.cost_calculator import (
    calculate_job_cost,
    calculate_refund_amount,
    get_refund_percentage,
)


def test_cost_calculation():
    """Test job cost calculation."""
    print("\n" + "="*60)
    print("Testing Cost Calculation")
    print("="*60 + "\n")

    # Test 1: Empty workflow
    workflow = {"nodes": []}
    cost = calculate_job_cost(workflow)
    assert cost == 10, f"Empty workflow should cost 10 credits, got {cost}"
    print("[OK] Empty workflow: 10 credits")

    # Test 2: Simple workflow
    workflow = {
        "nodes": [
            {"type": "dataset", "data": {}},
            {"type": "model", "data": {"algorithms": ["logistic_regression"]}},
        ]
    }
    cost = calculate_job_cost(workflow)
    # BASE (10) + DATASET (0) + MODEL (20 + 10 for 1 algo) = 40
    assert cost == 40, f"Simple workflow should cost 40 credits, got {cost}"
    print("[OK] Simple workflow: 40 credits")

    # Test 3: Workflow with preprocessing
    workflow = {
        "nodes": [
            {"type": "dataset", "data": {}},
            {"type": "preprocess", "data": {}},
            {"type": "preprocess", "data": {}},
            {"type": "model", "data": {"algorithms": ["random_forest"]}},
        ]
    }
    cost = calculate_job_cost(workflow)
    # BASE (10) + DATASET (0) + PREPROCESS (5) + PREPROCESS (5) + MODEL (20 + 10) = 50
    assert cost == 50, f"Preprocessing workflow should cost 50 credits, got {cost}"
    print("[OK] Preprocessing workflow: 50 credits")

    # Test 4: Complex workflow with HPO
    workflow = {
        "nodes": [
            {"type": "dataset", "data": {}},
            {"type": "preprocess", "data": {}},
            {
                "type": "model",
                "data": {
                    "algorithms": ["random_forest", "xgboost", "logistic_regression"],
                    "hpo_enabled": True
                }
            },
            {"type": "evaluation", "data": {}},
        ]
    }
    cost = calculate_job_cost(workflow)
    # BASE (10) + DATASET (0) + PREPROCESS (5) + MODEL (20 + 10 HPO + 30 for 3 algos) + EVAL (5) = 80
    assert cost == 80, f"Complex workflow should cost 80 credits, got {cost}"
    print("[OK] Complex workflow with HPO: 80 credits")

    # Test 5: All node types
    workflow = {
        "nodes": [
            {"type": "dataset", "data": {}},
            {"type": "preprocess", "data": {}},
            {"type": "model", "data": {"algorithms": ["knn"]}},
            {"type": "evaluate", "data": {}},
            {"type": "visualize", "data": {}},
            {"type": "save", "data": {}},
        ]
    }
    cost = calculate_job_cost(workflow)
    # BASE (10) + DATASET (0) + PREPROCESS (5) + MODEL (20 + 10) + EVAL (5) + VIZ (3) + SAVE (2) = 55
    assert cost == 55, f"Full workflow should cost 55 credits, got {cost}"
    print("[OK] Full workflow with all nodes: 55 credits")


def test_refund_calculation():
    """Test refund calculation with penalties."""
    print("\n" + "="*60)
    print("Testing Refund Calculation")
    print("="*60 + "\n")

    # Test 1: No prior cancellations - 100% refund
    amount, percentage = calculate_refund_amount(100, 0)
    assert amount == 100, f"Should get 100 credits, got {amount}"
    assert percentage == 1.0, f"Should get 100% refund, got {percentage}"
    print("[OK] 0 cancellations: 100 credits (100% refund)")

    # Test 2: 5 prior cancellations - 75% refund
    amount, percentage = calculate_refund_amount(100, 5)
    assert amount == 75, f"Should get 75 credits, got {amount}"
    assert percentage == 0.75, f"Should get 75% refund, got {percentage}"
    print("[OK] 5 cancellations: 75 credits (75% refund)")

    # Test 3: 10 prior cancellations - 50% refund (minimum)
    amount, percentage = calculate_refund_amount(100, 10)
    assert amount == 50, f"Should get 50 credits, got {amount}"
    assert percentage == 0.5, f"Should get 50% refund, got {percentage}"
    print("[OK] 10 cancellations: 50 credits (50% refund)")

    # Test 4: 20+ prior cancellations - still 50% minimum
    amount, percentage = calculate_refund_amount(100, 20)
    assert amount == 50, f"Should get 50 credits, got {amount}"
    assert percentage == 0.5, f"Should get 50% refund, got {percentage}"
    print("[OK] 20 cancellations: 50 credits (50% minimum refund)")

    # Test 5: Different amounts
    amount, percentage = calculate_refund_amount(250, 3)
    expected_pct = 0.85  # 1.0 - (3 * 0.05)
    expected_amt = 212  # int(250 * 0.85)
    assert amount == expected_amt, f"Should get {expected_amt} credits, got {amount}"
    assert percentage == expected_pct, f"Should get {expected_pct} refund, got {percentage}"
    print(f"[OK] 3 cancellations on 250 credits: {amount} credits ({percentage*100:.0f}% refund)")


def test_refund_percentage_logic():
    """Test get_refund_percentage function."""
    print("\n" + "="*60)
    print("Testing Refund Percentage Logic")
    print("="*60 + "\n")

    test_cases = [
        (0, 1.0),
        (1, 0.95),
        (2, 0.90),
        (5, 0.75),
        (10, 0.5),
        (15, 0.5),  # Capped at 50%
        (100, 0.5),  # Capped at 50%
    ]

    for cancellation_count, expected_pct in test_cases:
        actual_pct = get_refund_percentage(cancellation_count)
        assert actual_pct == expected_pct, \
            f"{cancellation_count} cancellations: expected {expected_pct}, got {actual_pct}"
        print(f"[OK] {cancellation_count} cancellations: {actual_pct*100:.0f}% refund")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Job System Standalone Tests")
    print("="*60)

    try:
        test_cost_calculation()
        test_refund_calculation()
        test_refund_percentage_logic()

        print("\n" + "="*60)
        print("All Tests Passed!")
        print("="*60 + "\n")

        print("Summary:")
        print("  [OK] Cost calculation working correctly")
        print("  [OK] Refund calculation working correctly")
        print("  [OK] Penalty system working correctly")
        print("\nCore business logic verified successfully!")

        return 0
    except AssertionError as e:
        print(f"\n[ERROR] Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
