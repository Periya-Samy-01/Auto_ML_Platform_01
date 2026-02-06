"""
ARQ Worker Configuration
Async Redis Queue worker for processing background jobs
"""

import json
import logging
import asyncio
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Add project root to sys.path to allow importing from packages
# apps/api/app/worker.py -> ../../../
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from arq import cron
from arq.connections import RedisSettings
from arq.worker import Worker

from app.core.config import settings
from app.services.ingestion_processor import ingestion_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def handle_ingestion_job(ctx: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """
    Handle dataset ingestion job

    This function wraps the synchronous ingestion processor
    and runs it in a thread pool to avoid blocking the event loop.

    Args:
        ctx: ARQ context (contains redis connection, job info, etc.)
        job_id: The ingestion job ID to process

    Returns:
        Processing result dictionary
    """
    logger.info(f"Starting ingestion job: {job_id}")

    try:
        # Run the synchronous processor in a thread pool
        # This is necessary because the processor uses blocking I/O
        # (database queries, file downloads, etc.)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,  # Uses default ThreadPoolExecutor
            ingestion_processor.process_dataset_ingestion_sync,
            job_id
        )

        logger.info(f"Completed ingestion job {job_id}: {result.get('status')}")
        return result

    except Exception as e:
        logger.error(f"Failed to process ingestion job {job_id}: {e}")
        raise


async def handle_workflow_job(ctx: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """
    Handle workflow execution job

    This function executes a workflow in the background.

    Args:
        ctx: ARQ context (contains redis connection, job info, etc.)
        job_id: The workflow job ID to process

    Returns:
        Workflow execution result
    """
    logger.info(f"Starting workflow job: {job_id}")

    try:
        from app.services.cache import cache_service
        from app.workflows.schemas import (
            WorkflowNode,
            WorkflowEdge,
            WorkflowStatus,
            NodeStatus,
            WSMessage,
            WSMessageType,
        )
        from app.workflows.executor import WorkflowExecutor
        from app.workflows.router import publish_workflow_update
        
        # Database imports for persistence
        from app.core.database import SessionLocal
        from database.models import Job, Model
        from database.models.enums import JobStatus

        # Get workflow data from cache
        workflow_data = cache_service.get(f"workflow:{job_id}")
        if not workflow_data:
            raise ValueError(f"Workflow {job_id} not found in cache")

        data = json.loads(workflow_data)

        # Parse nodes and edges
        nodes = [WorkflowNode(**n) for n in data["nodes"]]
        edges = [WorkflowEdge(**e) for e in data["edges"]]
        user_id = data.get("user_id")
        
        # Extract dataset info from workflow nodes (find dataset node)
        dataset_id = None
        dataset_name = None
        is_sample = False
        for node in data["nodes"]:
            if node.get("type") == "dataset":
                config = node.get("config", {})
                is_sample = config.get("is_sample", False) or config.get("isSample", False)
                
                # Always extract dataset_name for display
                dataset_name = config.get("dataset_name") or config.get("datasetName")
                
                # For real datasets, get the UUID; for sample datasets, dataset_id is just a key like "iris"
                if not is_sample:
                    dataset_id = config.get("selectedDatasetId") or config.get("datasetId") or config.get("dataset_id")
                
                break

        # Create Job record in database
        db_job = None
        db = SessionLocal()
        try:
            import uuid
            db_job = Job(
                id=uuid.UUID(job_id),
                user_id=uuid.UUID(user_id) if user_id else None,
                status=JobStatus.RUNNING,
                started_at=datetime.utcnow(),
            )
            db.add(db_job)
            db.commit()
            logger.info(f"Created Job record: {db_job.id}")
        except Exception as e:
            logger.warning(f"Failed to create Job record: {e}")
            db.rollback()
        finally:
            db.close()

        # Update status to running
        data["status"] = WorkflowStatus.RUNNING.value
        data["started_at"] = datetime.utcnow().isoformat()
        cache_service.set_with_ttl(f"workflow:{job_id}", json.dumps(data), ttl=3600 * 24)

        # Publish status update
        publish_workflow_update(job_id, WSMessage(
            type=WSMessageType.STATUS_UPDATE,
            job_id=job_id,
            data={"status": WorkflowStatus.RUNNING.value},
            timestamp=datetime.utcnow().isoformat(),
        ))

        # Define status callback
        def status_callback(node_id: str, status: NodeStatus, error: Optional[str] = None):
            """Callback to update node status during execution."""
            # Update cache
            cached = cache_service.get(f"workflow:{job_id}")
            if cached:
                cache_data = json.loads(cached)
                if node_id in cache_data.get("node_statuses", {}):
                    cache_data["node_statuses"][node_id]["status"] = status.value
                    if error:
                        cache_data["node_statuses"][node_id]["error"] = error
                    cache_service.set_with_ttl(f"workflow:{job_id}", json.dumps(cache_data), ttl=3600 * 24)

            # Publish update
            msg_type = {
                NodeStatus.RUNNING: WSMessageType.NODE_STARTED,
                NodeStatus.COMPLETED: WSMessageType.NODE_COMPLETED,
                NodeStatus.FAILED: WSMessageType.NODE_FAILED,
            }.get(status, WSMessageType.STATUS_UPDATE)

            publish_workflow_update(job_id, WSMessage(
                type=msg_type,
                job_id=job_id,
                data={"node_id": node_id, "status": status.value, "error": error},
                timestamp=datetime.utcnow().isoformat(),
            ))

        # Execute workflow in thread pool (it uses sync ML libraries)
        loop = asyncio.get_event_loop()

        def sync_execute():
            executor = WorkflowExecutor(nodes, edges, job_id)
            return executor.execute()

        results = await loop.run_in_executor(None, sync_execute)

        # Calculate duration
        started_at_dt = datetime.fromisoformat(data["started_at"])
        completed_at_dt = datetime.utcnow()
        duration_seconds = int((completed_at_dt - started_at_dt).total_seconds())

        # Update final status
        data["status"] = WorkflowStatus.COMPLETED.value
        data["completed_at"] = completed_at_dt.isoformat()
        data["results"] = results.model_dump()
        cache_service.set_with_ttl(f"workflow:{job_id}", json.dumps(data), ttl=3600 * 24)

        # Save to database: Update Job and create Model record
        db = SessionLocal()
        try:
            import uuid
            
            # Update Job status
            db_job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
            if db_job:
                db_job.status = JobStatus.COMPLETED
                db_job.completed_at = completed_at_dt
                db_job.duration_seconds = duration_seconds
            
            # Create Model record with results
            results_dict = results.model_dump()
            
            # Create a descriptive name including dataset info
            algo_name = results_dict.get('algorithm_name', 'Model')
            if dataset_name:
                model_name = f"{algo_name} on {dataset_name.replace('_', ' ').title()} - {completed_at_dt.strftime('%Y-%m-%d %H:%M')}"
            else:
                model_name = f"{algo_name} - {completed_at_dt.strftime('%Y-%m-%d %H:%M')}"
            
            model = Model(
                user_id=uuid.UUID(user_id) if user_id else None,
                job_id=uuid.UUID(job_id),
                dataset_id=uuid.UUID(dataset_id) if dataset_id else None,
                name=model_name,
                # Store dataset_name in version field for display (works for both sample and real datasets)
                version=dataset_name if dataset_name else None,
                model_type=results_dict.get('algorithm'),
                s3_model_path=results_dict.get('model_path'),
                metrics_json={
                    m['key']: m['value'] for m in results_dict.get('metrics', [])
                } if results_dict.get('metrics') else {},
                hyperparameters_json=results_dict.get('hyperparameters', {}),
            )
            db.add(model)
            db.commit()
            logger.info(f"Created Model record: {model.id}")
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
            db.rollback()
        finally:
            db.close()

        # Publish completion
        publish_workflow_update(job_id, WSMessage(
            type=WSMessageType.RESULT,
            job_id=job_id,
            data={"status": WorkflowStatus.COMPLETED.value, "results": results.model_dump()},
            timestamp=datetime.utcnow().isoformat(),
        ))

        logger.info(f"Completed workflow job {job_id}")
        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        logger.error(f"Failed to execute workflow {job_id}: {e}")

        # Update status to failed in cache
        try:
            from app.services.cache import cache_service
            workflow_data = cache_service.get(f"workflow:{job_id}")
            if workflow_data:
                data = json.loads(workflow_data)
                data["status"] = WorkflowStatus.FAILED.value
                data["completed_at"] = datetime.utcnow().isoformat()
                data["error"] = str(e)
                cache_service.set_with_ttl(f"workflow:{job_id}", json.dumps(data), ttl=3600 * 24)
        except:
            pass

        # Update Job status to failed in database
        try:
            import uuid
            from app.core.database import SessionLocal
            from database.models import Job
            from database.models.enums import JobStatus
            
            db = SessionLocal()
            db_job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
            if db_job:
                db_job.status = JobStatus.FAILED
                db_job.completed_at = datetime.utcnow()
                db_job.error_message = str(e)[:500]  # Truncate to fit
                db.commit()
            db.close()
        except:
            pass

        raise


async def startup(ctx: Dict[str, Any]) -> None:
    """
    Worker startup handler
    Called once when the worker starts
    """
    logger.info("ARQ Worker starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Redis URL: {settings.REDIS_URL}")

    # The database session is created per-job in ingestion_processor
    # No need to initialize it here

    logger.info("ARQ Worker ready to process jobs")


async def shutdown(ctx: Dict[str, Any]) -> None:
    """
    Worker shutdown handler
    Called once when the worker shuts down
    """
    logger.info("ARQ Worker shutting down...")


def parse_redis_url(url: str) -> RedisSettings:
    """
    Parse a Redis URL into RedisSettings

    Args:
        url: Redis URL (e.g., redis://localhost:6379/0)

    Returns:
        RedisSettings object
    """
    from urllib.parse import urlparse

    # Auto-detect Upstash and ensure TLS is used
    use_ssl = False
    if "upstash.io" in url:
        use_ssl = True
        if url.startswith("redis://"):
            url = url.replace("redis://", "rediss://", 1)
    
    # Also detect if URL explicitly uses rediss://
    if url.startswith("rediss://"):
        use_ssl = True

    parsed = urlparse(url)

    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
        password=parsed.password,
        ssl=use_ssl,
    )


class WorkerSettings:
    """
    ARQ Worker Settings

    Run the worker with:
        arq app.worker.WorkerSettings

    Or from the project root:
        python -m arq apps.api.app.worker.WorkerSettings
    """

    # Job functions to register
    functions = [handle_ingestion_job, handle_workflow_job]

    # Startup/shutdown handlers
    on_startup = startup
    on_shutdown = shutdown

    # Redis connection settings
    redis_settings = parse_redis_url(settings.REDIS_URL)

    # Worker configuration
    max_jobs = 10  # Maximum concurrent jobs
    job_timeout = 1800  # 30 minutes max per job
    max_tries = 3  # Retry failed jobs up to 3 times
    retry_jobs = True  # Enable automatic retry

    # Queue configuration
    queue_name = "arq:queue"

    # Health check
    health_check_interval = 60  # seconds

    # Keep job results for 1 hour
    keep_result = 3600
