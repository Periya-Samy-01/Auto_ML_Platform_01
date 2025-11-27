"""
Master Test Runner
Runs all verification tests in sequence
"""

import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("AUTOML PLATFORM - OPTION 2 VERIFICATION")
print("Field Name Alignment Test Suite")
print("=" * 70)

# Test configurations
tests = [
    {
        "name": "Model Import Test",
        "script": "test_field_alignment.py",
        "description": "Verifies SQLAlchemy models have correct field names"
    },
    {
        "name": "Database Schema Test",
        "script": "verify_database_schema.py",
        "description": "Verifies database tables have correct columns"
    }
]

results = []
api_dir = Path(__file__).parent

for i, test in enumerate(tests, 1):
    print(f"\n{'=' * 70}")
    print(f"TEST {i}/{len(tests)}: {test['name']}")
    print(f"Description: {test['description']}")
    print(f"{'=' * 70}")
    
    script_path = api_dir / test['script']
    
    if not script_path.exists():
        print(f"❌ SKIP: Script not found: {test['script']}")
        results.append({
            "name": test['name'],
            "status": "SKIP",
            "reason": "Script not found"
        })
        continue
    
    try:
        # Run test script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(api_dir)
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print("STDERR:", result.stderr)
        
        # Check result
        if result.returncode == 0:
            print(f"\n✅ {test['name']}: PASSED")
            results.append({
                "name": test['name'],
                "status": "PASS"
            })
        else:
            print(f"\n❌ {test['name']}: FAILED (exit code {result.returncode})")
            results.append({
                "name": test['name'],
                "status": "FAIL",
                "exit_code": result.returncode
            })
            
    except subprocess.TimeoutExpired:
        print(f"\n❌ {test['name']}: TIMEOUT (>30s)")
        results.append({
            "name": test['name'],
            "status": "TIMEOUT"
        })
    except Exception as e:
        print(f"\n❌ {test['name']}: ERROR - {e}")
        results.append({
            "name": test['name'],
            "status": "ERROR",
            "error": str(e)
        })

# Print summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

for result in results:
    status_icon = {
        "PASS": "✅",
        "FAIL": "❌",
        "SKIP": "⏭️",
        "TIMEOUT": "⏱️",
        "ERROR": "💥"
    }.get(result['status'], "❓")
    
    print(f"{status_icon} {result['name']}: {result['status']}")
    
    if result['status'] == "FAIL" and 'exit_code' in result:
        print(f"   Exit code: {result['exit_code']}")
    elif result['status'] == "ERROR" and 'error' in result:
        print(f"   Error: {result['error']}")
    elif result['status'] == "SKIP" and 'reason' in result:
        print(f"   Reason: {result['reason']}")

# Overall result
passed = sum(1 for r in results if r['status'] == "PASS")
failed = sum(1 for r in results if r['status'] in ["FAIL", "TIMEOUT", "ERROR"])
skipped = sum(1 for r in results if r['status'] == "SKIP")

print(f"\nTotal: {len(results)} tests")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Skipped: {skipped}")

print("\n" + "=" * 70)

if failed == 0 and passed > 0:
    print("🎉 ALL TESTS PASSED! Option 2 implementation is correct!")
    print("=" * 70)
    print("\n✅ NEXT STEPS:")
    print("1. Apply migration: alembic upgrade head")
    print("2. Run database verification again: python verify_database_schema.py")
    print("3. Start the API server: uvicorn app.main:app --reload")
    print("4. Test endpoints manually or with Postman")
    print("5. Proceed with Week 2 development!")
    sys.exit(0)
elif skipped == len(results):
    print("⚠️  ALL TESTS SKIPPED - Please check if scripts exist")
    sys.exit(2)
else:
    print("❌ SOME TESTS FAILED - Review output above and fix issues")
    print("\nCommon fixes:")
    print("- Import errors: Run 'poetry install' and restart shell")
    print("- Database errors: Check .env file and database connection")
    print("- Check EXECUTION_GUIDE.md for detailed troubleshooting")
    sys.exit(1)
