import os
import sys
import logging
import uuid
import traceback

# Configuration logic to setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
apps_workers = os.path.join(project_root, 'apps', 'workers')
apps_api = os.path.join(project_root, 'apps', 'api')

print(f"Adding to sys.path: {project_root}")
sys.path.append(project_root)
print(f"Adding to sys.path: {apps_workers}")
sys.path.append(apps_workers)
print(f"Adding to sys.path: {apps_api}")
sys.path.append(apps_api)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose():
    try:
        from packages.database.models import IngestionJob, Dataset
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Connect to DB
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/automl_platform")
        print(f"Connecting to DB: {DATABASE_URL}")
        
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Get latest job
        job = db.query(IngestionJob).order_by(IngestionJob.created_at.desc()).first()
        
        if not job:
            print("No jobs found.")
            return

        print(f"Latest Job ID: {job.id}")
        print(f"Status: {job.status}")
        
        if job.status in ['completed']:
            print("Job is already completed. Nothing to debug unless you want to re-run it.")
            # return
            
        print("Attempting to import worker task...")
        # Import the task function
        from worker.tasks.ingestion_task import process_dataset_ingestion
        
        print(f"Running ingestion for job {job.id} synchronously...")
        
        # Manually run the task (bypassing Celery)
        # We need to simulate the 'bind=True' by handling the instance if needed, 
        # but calling the decorated function directly usually works if we use .run() or just call it 
        # depending on how Celery is mocked/loaded. 
        # However, since we are not in a worker context, we might need to be careful.
        # The safest way to test the logic is to call the underlying function if available, 
        # or just try calling the wrapper.
        
        try:
             # Try calling the underlying run method if it's a celery task class instance
            if hasattr(process_dataset_ingestion, 'run'):
                 # We need to pass 'self'. The task expects 'self' as first arg because of bind=True.
                 # We can pass a mock self.
                 
                class MockTask:
                    def __init__(self):
                        self.request = type('Request', (), {'id': str(job.id)})
                        self.r2_service = None
                        self.cache_service = None
                        
                    def retry(self, exc=None, countdown=None, **kwargs):
                        print(f"Task requested retry: {exc}")
                        raise exc
                
                mock_task = MockTask()
                
                # We also need to Initialize services as done in __call__
                from worker.services.r2_service import R2Service
                from worker.services.cache_service import CacheService
                mock_task.r2_service = R2Service()
                mock_task.cache_service = CacheService()
                
                print("Invoking .run() with mock task instance...")
                result = process_dataset_ingestion.run(mock_task, job_id=str(job.id))
                print("Job finished successfully!")
                print("Result:", result)
            else:
                print("Not a class based task? Calling directly...")
                process_dataset_ingestion(job_id=str(job.id))
                
        except Exception as e:
            print("\n!!! EXCEPTION DURING EXECUTION !!!")
            traceback.print_exc()
            
    except ImportError as e:
        print("\n!!! IMPORT ERROR !!!")
        print("Could not import necessary modules. Check python path.")
        traceback.print_exc()
    except Exception as e:
        print(f"\n!!! UNEXPECTED ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
