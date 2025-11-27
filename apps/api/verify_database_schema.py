"""
Database Schema Verification Script
Run after applying migration to verify schema is correct
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect, text

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings

print("=" * 70)
print("DATABASE SCHEMA VERIFICATION")
print("=" * 70)

# Connect to database
print("\n1. Connecting to database...")
try:
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    print("   ✅ Connected successfully!")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    print("\n   Troubleshooting:")
    print("   - Check .env file has DATABASE_URL")
    print("   - Check Neon database is running")
    print("   - Check network connection")
    sys.exit(1)

# Check tables exist
print("\n2. Checking required tables exist...")
required_tables = ['datasets', 'dataset_versions', 'dataset_profiles', 'ingestion_jobs']
existing_tables = inspector.get_table_names()

all_tables_exist = True
for table in required_tables:
    if table in existing_tables:
        print(f"   ✅ {table}")
    else:
        print(f"   ❌ {table} - MISSING")
        all_tables_exist = False

if not all_tables_exist:
    print("\n   ❌ Some tables are missing!")
    print("   Run: alembic upgrade head")
    sys.exit(1)

# Check datasets table
print("\n3. Verifying datasets table schema...")
datasets_cols = {col['name']: str(col['type']) for col in inspector.get_columns('datasets')}

required_cols = {
    'id': 'UUID',
    'user_id': 'UUID',
    'name': 'TEXT',
    'current_version_id': 'UUID'  # NOT latest_version_id
}

datasets_ok = True
for col_name, expected_type in required_cols.items():
    if col_name in datasets_cols:
        print(f"   ✅ {col_name}: {datasets_cols[col_name]}")
    else:
        print(f"   ❌ {col_name}: MISSING")
        datasets_ok = False

# Check for removed columns
removed_cols = ['version_count', 'is_deleted', 'deleted_at', 'latest_version_id']
for col_name in removed_cols:
    if col_name in datasets_cols:
        print(f"   ⚠️  {col_name}: SHOULD NOT EXIST (old migration field)")
        datasets_ok = False
    else:
        print(f"   ✅ {col_name}: Correctly removed")

# Check dataset_versions table
print("\n4. Verifying dataset_versions table schema...")
versions_cols = {col['name']: str(col['type']) for col in inspector.get_columns('dataset_versions')}

required_version_cols = {
    'id': 'UUID',
    'dataset_id': 'UUID',
    'version_number': 'INTEGER',
    's3_path': 'TEXT',  # NOT r2_parquet_path
    'columns_metadata': 'JSONB'  # NOT schema_json
}

versions_ok = True
for col_name, expected_type in required_version_cols.items():
    if col_name in versions_cols:
        print(f"   ✅ {col_name}: {versions_cols[col_name]}")
    else:
        print(f"   ❌ {col_name}: MISSING")
        versions_ok = False

# Check for old field names
old_version_cols = ['r2_parquet_path', 'schema_json']
for col_name in old_version_cols:
    if col_name in versions_cols:
        print(f"   ⚠️  {col_name}: SHOULD NOT EXIST (old migration field)")
        versions_ok = False
    else:
        print(f"   ✅ {col_name}: Correctly replaced")

# Check dataset_profiles table
print("\n5. Verifying dataset_profiles table schema...")
profiles_cols = {col['name']: str(col['type']) for col in inspector.get_columns('dataset_profiles')}

required_profile_cols = {
    'id': 'UUID',
    'dataset_version_id': 'UUID',  # NOT version_id
    'profile_data': 'JSONB'  # NOT profile_json
}

profiles_ok = True
for col_name, expected_type in required_profile_cols.items():
    if col_name in profiles_cols:
        print(f"   ✅ {col_name}: {profiles_cols[col_name]}")
    else:
        print(f"   ❌ {col_name}: MISSING")
        profiles_ok = False

# Check for old field names
old_profile_cols = ['version_id', 'profile_json']
for col_name in old_profile_cols:
    if col_name in profiles_cols:
        print(f"   ⚠️  {col_name}: SHOULD NOT EXIST (old migration field)")
        profiles_ok = False
    else:
        print(f"   ✅ {col_name}: Correctly replaced")

# Check ingestion_jobs table
print("\n6. Verifying ingestion_jobs table schema...")
jobs_cols = {col['name']: str(col['type']) for col in inspector.get_columns('ingestion_jobs')}

jobs_ok = True
if 'dataset_version_id' in jobs_cols:
    print(f"   ✅ dataset_version_id: {jobs_cols['dataset_version_id']}")
else:
    print(f"   ❌ dataset_version_id: MISSING")
    jobs_ok = False

if 'version_id' in jobs_cols:
    print(f"   ⚠️  version_id: SHOULD NOT EXIST (old migration field)")
    jobs_ok = False
else:
    print(f"   ✅ version_id: Correctly replaced")

# Check foreign keys
print("\n7. Checking foreign key relationships...")
fks_ok = True

fks = inspector.get_foreign_keys('datasets')
fk_names = [fk['constrained_columns'][0] for fk in fks]

if 'current_version_id' in fk_names:
    print("   ✅ datasets.current_version_id -> dataset_versions.id")
else:
    print("   ❌ Missing FK: datasets.current_version_id")
    fks_ok = False

fks = inspector.get_foreign_keys('dataset_profiles')
fk_names = [fk['constrained_columns'][0] for fk in fks]

if 'dataset_version_id' in fk_names:
    print("   ✅ dataset_profiles.dataset_version_id -> dataset_versions.id")
else:
    print("   ❌ Missing FK: dataset_profiles.dataset_version_id")
    fks_ok = False

fks = inspector.get_foreign_keys('ingestion_jobs')
fk_names = [fk['constrained_columns'][0] for fk in fks]

if 'dataset_version_id' in fk_names:
    print("   ✅ ingestion_jobs.dataset_version_id -> dataset_versions.id")
else:
    print("   ❌ Missing FK: ingestion_jobs.dataset_version_id")
    fks_ok = False

# Check alembic version
print("\n8. Checking migration version...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        print(f"   Current migration: {version}")
        
        if version == '20251126_dataset_versioning_clean':
            print("   ✅ Clean migration applied!")
        elif version == 'add_dataset_versioning':
            print("   ⚠️  OLD migration still applied - need to upgrade!")
            print("   Run: alembic upgrade head")
        else:
            print(f"   ℹ️  Different migration: {version}")
except Exception as e:
    print(f"   ⚠️  Could not check version: {e}")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

# Overall result
if all([datasets_ok, versions_ok, profiles_ok, jobs_ok, fks_ok]):
    print("\n🎉 ALL CHECKS PASSED! Schema is correctly aligned with architecture!")
    sys.exit(0)
else:
    print("\n⚠️  SOME CHECKS FAILED! Review the output above.")
    print("\nCommon fixes:")
    print("  - If columns missing: Run 'alembic upgrade head'")
    print("  - If old columns exist: Migration not applied correctly")
    print("  - Check EXECUTION_GUIDE.md for detailed troubleshooting")
    sys.exit(1)
