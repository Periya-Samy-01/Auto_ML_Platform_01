"""
Simple Test Runner for AutoML Backend
No testing experience required!
"""

import subprocess
import sys
from pathlib import Path

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_command(cmd, cwd=None, description=""):
    """Run a command and return success status."""
    print(f"📝 {description}")
    print(f"   Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        # Print errors if failed
        if result.returncode != 0 and result.stderr:
            print("❌ ERROR OUTPUT:")
            print(result.stderr)
            return False
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Test took longer than 60 seconds")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print_header("🧪 AutoML Backend Test Suite")
    print("This will test your backend in 3 steps:")
    print("1️⃣  Core business logic (no dependencies)")
    print("2️⃣  API endpoints (requires database)")
    print("3️⃣  Worker system (requires database + Redis)\n")
    
    project_root = Path(__file__).parent
    
    results = {
        "passed": [],
        "failed": [],
        "skipped": []
    }
    
    # ========================================
    # Test 1: Standalone Tests (No Dependencies)
    # ========================================
    print_header("Test 1: Core Business Logic (Standalone)")
    
    standalone_test = project_root / "test_jobs_standalone.py"
    if standalone_test.exists():
        success = run_command(
            [sys.executable, str(standalone_test)],
            cwd=str(project_root),
            description="Testing cost calculation and refund logic"
        )
        
        if success:
            results["passed"].append("Core Business Logic")
            print("✅ Core business logic tests PASSED!\n")
        else:
            results["failed"].append("Core Business Logic")
            print("❌ Core business logic tests FAILED\n")
    else:
        results["skipped"].append("Core Business Logic")
        print("⏭️  SKIPPED: test_jobs_standalone.py not found\n")
    
    # ========================================
    # Test 2: API Tests (Requires Database)
    # ========================================
    print_header("Test 2: API Tests (Requires Database)")
    
    api_dir = project_root / "apps" / "api"
    api_tests_dir = api_dir / "tests"
    
    if api_tests_dir.exists() and (api_tests_dir / "test_health.py").exists():
        print("Checking if pytest is available...")
        
        # Check if pytest is installed
        check_pytest = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            cwd=str(api_dir)
        )
        
        if check_pytest.returncode != 0:
            print("⚠️  pytest not found. Trying to install...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
        
        # Run API tests
        success = run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=str(api_dir),
            description="Testing API endpoints (auth, credits, jobs)"
        )
        
        if success:
            results["passed"].append("API Tests")
            print("✅ API tests PASSED!\n")
        else:
            results["failed"].append("API Tests")
            print("❌ API tests FAILED")
            print("💡 Tip: Make sure PostgreSQL is running and .env is configured\n")
    else:
        results["skipped"].append("API Tests")
        print("⏭️  SKIPPED: API tests not found\n")
    
    # ========================================
    # Test 3: Worker Tests (Requires Redis + DB)
    # ========================================
    print_header("Test 3: Worker Tests (Requires Redis)")
    
    workers_dir = project_root / "apps" / "workers"
    worker_tests_dir = workers_dir / "tests"
    
    if worker_tests_dir.exists():
        success = run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=str(workers_dir),
            description="Testing worker job execution and ML training"
        )
        
        if success:
            results["passed"].append("Worker Tests")
            print("✅ Worker tests PASSED!\n")
        else:
            results["failed"].append("Worker Tests")
            print("❌ Worker tests FAILED")
            print("💡 Tip: Make sure Redis is running and R2 credentials are set\n")
    else:
        results["skipped"].append("Worker Tests")
        print("⏭️  SKIPPED: Worker tests not found\n")
    
    # ========================================
    # Summary
    # ========================================
    print_header("📊 Test Summary")
    
    total = len(results["passed"]) + len(results["failed"]) + len(results["skipped"])
    
    if results["passed"]:
        print("✅ PASSED:")
        for test in results["passed"]:
            print(f"   • {test}")
    
    if results["failed"]:
        print("\n❌ FAILED:")
        for test in results["failed"]:
            print(f"   • {test}")
    
    if results["skipped"]:
        print("\n⏭️  SKIPPED:")
        for test in results["skipped"]:
            print(f"   • {test}")
    
    print(f"\nTotal: {total} test suites")
    print(f"Passed: {len(results['passed'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Skipped: {len(results['skipped'])}")
    
    print("\n" + "="*70)
    
    # Final verdict
    if len(results["failed"]) == 0 and len(results["passed"]) > 0:
        print("🎉 ALL TESTS PASSED! Your backend is solid!")
        print("="*70)
        return 0
    elif len(results["failed"]) == 0 and len(results["passed"]) == 0:
        print("⚠️  No tests were run. Please check your setup.")
        print("="*70)
        return 2
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Common Issues:")
        print("   1. PostgreSQL not running")
        print("   2. Redis not running")
        print("   3. .env file missing or incorrect")
        print("   4. Database migrations not run")
        print("\n📖 See testing_guide.md for detailed troubleshooting")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
