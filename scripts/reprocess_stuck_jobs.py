
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.api.app.services.ingestion_processor import ingestion_processor
from packages.database.session import SessionLocal
from packages.database.models import IngestionJob

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reprocess_stuck_jobs():
    db = SessionLocal()
    try:
        # Find jobs that are not completed
        # We look for pending, processing (stuck), or failed jobs
        jobs = db.query(IngestionJob).filter(
            IngestionJob.status.in_(['pending', 'processing', 'failed'])
        ).all()
        
        logger.info(f"Found {len(jobs)} stuck jobs to reprocess.")
        
        for job in jobs:
            logger.info(f"Reprocessing Job ID: {job.id} (Status: {job.status})")
            
            # Reset status to pending so processor accepts it if needed
            # (though processor generally handles idempotency, resetting ensures a clean state)
            job.status = 'pending'
            db.commit()
            
            try:
                result = ingestion_processor.process_dataset_ingestion_sync(str(job.id))
                logger.info(f"Result for job {job.id}: {result}")
            except Exception as e:
                logger.error(f"Failed to process job {job.id}: {e}")
                
    except Exception as e:
        logger.error(f"Script failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting stuck job reprocessing...")
    reprocess_stuck_jobs()
    print("Done.")
