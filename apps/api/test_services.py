"""
Service Layer Integration Test
Tests dataset and ingestion services with new field names
"""

import sys
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

print("=" * 70)
print("SERVICE LAYER INTEGRATION TEST")
print("=" * 70)

# Setup
print("\n1. Setting up test environment...")
try:
    from app.core.database import SessionLocal
    from packages.database.models import User, Dataset, DatasetVersion
    from packages.database.models.enums import UserTier, ProblemType, FileFormat
    from app.services.datasets import dataset_service
    from app.services.ingestion import ingestion_service
    
    db = SessionLocal()
    print("   ✅ Database session created")
except Exception as e:
    print(f"   ❌ Setup failed: {e}")
    sys.exit(1)

# Create test user
print("\n2. Creating test user...")
test_user_id = uuid.uuid4()
try:
    test_user = User(
        id=test_user_id,
        email=f"test_{uuid.uuid4().hex[:8]}@test.com",
        password_hash="test_hash",
        full_name="Test User",
        tier=UserTier.FREE,
        credit_balance=1000
    )
    db.add(test_user)
    db.commit()
    print(f"   ✅ Test user created: {test_user.email}")
except Exception as e:
    print(f"   ❌ User creation failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 1: Create Dataset
print("\n3. Testing dataset_service.create_dataset()...")
try:
    dataset = dataset_service.create_dataset(
        db=db,
        user_id=test_user_id,
        name="Test Dataset",
        description="Test description",
        problem_type=ProblemType.CLASSIFICATION,
        target_column="target"
    )
    
    # Verify fields
    assert hasattr(dataset, 'current_version_id'), "Dataset missing current_version_id"
    assert not hasattr(dataset, 'latest_version_id'), "Dataset has old field latest_version_id"
    assert not hasattr(dataset, 'version_count'), "Dataset has old field version_count"
    
    print(f"   ✅ Dataset created: {dataset.id}")
    print(f"   ✅ Has current_version_id: {dataset.current_version_id}")
    print(f"   ✅ No old fields (latest_version_id, version_count)")
except Exception as e:
    print(f"   ❌ Dataset creation failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 2: Create Dataset Version
print("\n4. Testing dataset_service.create_dataset_version()...")
try:
    version = dataset_service.create_dataset_version(
        db=db,
        dataset_id=dataset.id,
        upload_id=uuid.uuid4(),
        original_filename="test.csv",
        original_size_bytes=1024,
        original_format=FileFormat.CSV,
        version_label="v1"
    )
    
    # Verify fields
    assert hasattr(version, 's3_path'), "Version missing s3_path"
    assert hasattr(version, 'columns_metadata'), "Version missing columns_metadata"
    assert not hasattr(version, 'r2_parquet_path'), "Version has old field r2_parquet_path"
    assert not hasattr(version, 'schema_json'), "Version has old field schema_json"
    
    print(f"   ✅ Version created: {version.id}")
    print(f"   ✅ Version number: {version.version_number}")
    print(f"   ✅ Has s3_path: {version.s3_path}")
    print(f"   ✅ Has columns_metadata: {version.columns_metadata}")
    print(f"   ✅ No old fields (r2_parquet_path, schema_json)")
except Exception as e:
    print(f"   ❌ Version creation failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 3: Update Version Status
print("\n5. Testing dataset_service.update_dataset_version_status()...")
try:
    test_schema = {
        "columns": [
            {"name": "feature1", "dtype": "float64", "null_count": 0},
            {"name": "target", "dtype": "int64", "null_count": 0}
        ]
    }
    
    dataset_service.update_dataset_version_status(
        db=db,
        version_id=version.id,
        status="completed",
        s3_path="datasets/test/version.parquet",
        parquet_size_bytes=512,
        row_count=100,
        column_count=2,
        columns_metadata=test_schema
    )
    
    # Refresh and verify
    db.refresh(version)
    db.refresh(dataset)
    
    assert version.s3_path == "datasets/test/version.parquet", "s3_path not updated"
    assert version.columns_metadata == test_schema, "columns_metadata not updated"
    assert dataset.current_version_id == version.id, "current_version_id not set"
    
    print(f"   ✅ Version status updated")
    print(f"   ✅ s3_path set: {version.s3_path}")
    print(f"   ✅ columns_metadata set: {len(version.columns_metadata['columns'])} columns")
    print(f"   ✅ Dataset current_version_id set: {dataset.current_version_id}")
except Exception as e:
    print(f"   ❌ Version update failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 4: Create Ingestion Job
print("\n6. Testing ingestion_service.create_ingestion_job()...")
try:
    job = ingestion_service.create_ingestion_job(
        db=db,
        user_id=test_user_id,
        dataset_id=dataset.id,
        dataset_version_id=version.id,
        upload_id=uuid.uuid4(),
        original_filename="test.csv",
        original_size_bytes=1024
    )
    
    # Verify fields
    assert hasattr(job, 'dataset_version_id'), "Job missing dataset_version_id"
    assert not hasattr(job, 'version_id'), "Job has old field version_id"
    assert job.dataset_version_id == version.id, "dataset_version_id not set correctly"
    
    print(f"   ✅ Job created: {job.id}")
    print(f"   ✅ Has dataset_version_id: {job.dataset_version_id}")
    print(f"   ✅ No old field (version_id)")
except Exception as e:
    print(f"   ❌ Job creation failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 5: Create Dataset Profile
print("\n7. Testing ingestion_service.create_dataset_profile()...")
try:
    test_profile = {
        "row_count": 100,
        "column_count": 2,
        "columns": [
            {"name": "feature1", "dtype": "float64", "min": 0.0, "max": 1.0},
            {"name": "target", "dtype": "int64", "unique_count": 2}
        ]
    }
    
    profile = ingestion_service.create_dataset_profile(
        db=db,
        dataset_version_id=version.id,
        profile_data=test_profile
    )
    
    # Verify fields
    assert hasattr(profile, 'dataset_version_id'), "Profile missing dataset_version_id"
    assert hasattr(profile, 'profile_data'), "Profile missing profile_data"
    assert not hasattr(profile, 'version_id'), "Profile has old field version_id"
    assert not hasattr(profile, 'profile_json'), "Profile has old field profile_json"
    assert profile.dataset_version_id == version.id, "dataset_version_id not set"
    assert profile.profile_data == test_profile, "profile_data not set"
    
    print(f"   ✅ Profile created: {profile.id}")
    print(f"   ✅ Has dataset_version_id: {profile.dataset_version_id}")
    print(f"   ✅ Has profile_data: {len(profile.profile_data['columns'])} columns")
    print(f"   ✅ No old fields (version_id, profile_json)")
except Exception as e:
    print(f"   ❌ Profile creation failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 6: Get Dataset with Relationships
print("\n8. Testing dataset retrieval with relationships...")
try:
    retrieved = dataset_service.get_dataset(
        db=db,
        dataset_id=dataset.id,
        user_id=test_user_id,
        include_versions=True
    )
    
    # Verify relationship
    assert retrieved.current_version is not None, "current_version relationship not loaded"
    assert retrieved.current_version.id == version.id, "current_version incorrect"
    assert not hasattr(retrieved, 'latest_version'), "Has old relationship latest_version"
    
    print(f"   ✅ Dataset retrieved: {retrieved.id}")
    print(f"   ✅ current_version relationship works")
    print(f"   ✅ Current version: v{retrieved.current_version.version_number}")
    print(f"   ✅ No old relationship (latest_version)")
except Exception as e:
    print(f"   ❌ Dataset retrieval failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Test 7: List Datasets
print("\n9. Testing dataset listing...")
try:
    datasets, total = dataset_service.list_user_datasets(
        db=db,
        user_id=test_user_id,
        skip=0,
        limit=10
    )
    
    assert len(datasets) > 0, "No datasets returned"
    assert datasets[0].id == dataset.id, "Wrong dataset returned"
    
    print(f"   ✅ Listed {len(datasets)} dataset(s)")
    print(f"   ✅ Total count: {total}")
except Exception as e:
    print(f"   ❌ Dataset listing failed: {e}")
    db.rollback()
    db.close()
    sys.exit(1)

# Cleanup
print("\n10. Cleaning up test data...")
try:
    db.delete(test_user)  # CASCADE will delete dataset, versions, jobs, profiles
    db.commit()
    print("   ✅ Test data cleaned up")
except Exception as e:
    print(f"   ⚠️  Cleanup warning: {e}")
    db.rollback()
finally:
    db.close()

# Summary
print("\n" + "=" * 70)
print("SERVICE LAYER TEST COMPLETE")
print("=" * 70)
print("\n🎉 ALL SERVICE TESTS PASSED!")
print("\nVerified:")
print("  ✅ Dataset uses current_version_id (not latest_version_id)")
print("  ✅ DatasetVersion uses s3_path (not r2_parquet_path)")
print("  ✅ DatasetVersion uses columns_metadata (not schema_json)")
print("  ✅ IngestionJob uses dataset_version_id (not version_id)")
print("  ✅ DatasetProfile uses dataset_version_id (not version_id)")
print("  ✅ DatasetProfile uses profile_data (not profile_json)")
print("  ✅ Relationships work correctly")
print("  ✅ Services interact properly with new schema")
