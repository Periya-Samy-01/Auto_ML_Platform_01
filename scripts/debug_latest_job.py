import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
# Script is in scripts/debug_latest_job.py
# Root is one level up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from packages.database.models import IngestionJob, Dataset, DatasetVersion

def check_latest_job():
    # Connect to DB
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/automl_platform"
    # Try to get from env or use default
    db_url = os.getenv("DATABASE_URL", DATABASE_URL)
    
    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("Connected to database.")
        
        # Get latest job
        job = db.query(IngestionJob).order_by(IngestionJob.created_at.desc()).first()
        
        if not job:
            print("No jobs found!")
            return
            
        print("\n=== Latest Job ===")
        print(f"ID: {job.id}")
        print(f"Status: {job.status}")
        print(f"Created At: {job.created_at}")
        print(f"Updated At: {job.updated_at}")
        print(f"Error Message: {job.error_message}")
        print(f"Dataset ID: {job.dataset_id}")
        
        # Get Dataset
        dataset = db.query(Dataset).filter(Dataset.id == job.dataset_id).first()
        if dataset:
            print("\n=== Dataset ===")
            print(f"ID: {dataset.id}")
            print(f"Name: {dataset.name}")
            print(f"Current Version ID: {dataset.current_version_id}")
            
            if dataset.current_version_id:
                version = db.query(DatasetVersion).filter(DatasetVersion.id == dataset.current_version_id).first()
                if version:
                     print("\n=== Current Version ===")
                     print(f"ID: {version.id}")
                     print(f"Row Count: {version.row_count}")
                     print(f"Col Count: {version.column_count}")
                else:
                    print("\nWARNING: Current Version ID exists but Version record not found!")
            else:
                print("\nWARNING: Dataset has no current_version_id set!")
        else:
            print("\nWARNING: Dataset for job not found!")

    except Exception as e:
        print(f"Error connecting to DB: {e}")
        # Try finding the correct DB url from env file if possible
        pass

if __name__ == "__main__":
    check_latest_job()
