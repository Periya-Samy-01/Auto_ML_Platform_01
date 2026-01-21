"""
Workflow API Router

Endpoints for workflow validation and execution.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.services.cache import cache_service

# Import models from shared package
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from database.models import User

from .schemas import (
    WorkflowValidateRequest,
    WorkflowValidateResponse,
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
    WorkflowStatusResponse,
    WorkflowStatus,
    NodeStatus,
    NodeExecutionStatus,
    WSMessage,
    WSMessageType,
    WorkflowResults,
)
from .validator import validate_workflow
from .executor import execute_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


# =============================================================================
# REST Endpoints
# =============================================================================

@router.post("/validate", response_model=WorkflowValidateResponse)
async def validate_workflow_endpoint(
    request: WorkflowValidateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Validate a workflow without executing it.

    Checks for:
    - Valid graph structure
    - Proper node connections
    - Required configurations
    - No cycles
    """
    result = validate_workflow(request.nodes, request.edges)
    return result


@router.post("/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow_endpoint(
    request: WorkflowExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Queue a workflow for execution.

    The workflow is validated first. If valid, it's queued for
    background execution and a job ID is returned.

    The client can then:
    - Poll GET /workflows/{job_id}/status for status
    - Connect to WS /workflows/{job_id}/stream for real-time updates
    """
    # Validate first
    validation = validate_workflow(request.nodes, request.edges)
    if not validation.valid:
        return WorkflowExecuteResponse(
            job_id="",
            status=WorkflowStatus.FAILED,
            message=f"Validation failed: {validation.errors[0].message if validation.errors else 'Unknown error'}",
        )

    # Dry run - just validate
    if request.dry_run:
        return WorkflowExecuteResponse(
            job_id="",
            status=WorkflowStatus.COMPLETED,
            message="Validation successful (dry run)",
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Store workflow in cache for worker to pick up
    workflow_data = {
        "job_id": job_id,
        "user_id": str(current_user.id),
        "nodes": [n.model_dump() for n in request.nodes],
        "edges": [e.model_dump() for e in request.edges],
        "status": WorkflowStatus.PENDING.value,
        "created_at": datetime.utcnow().isoformat(),
        "node_statuses": {
            n.id: NodeExecutionStatus(
                node_id=n.id,
                status=NodeStatus.PENDING,
            ).model_dump()
            for n in request.nodes
        },
    }

    # Store in Redis
    cache_service.set_with_ttl(
        f"workflow:{job_id}",
        json.dumps(workflow_data),
        ttl=3600 * 24,  # 24 hours
    )

    # Queue the job
    await _queue_workflow_job(job_id, request.priority)

    return WorkflowExecuteResponse(
        job_id=job_id,
        status=WorkflowStatus.PENDING,
        message="Workflow queued for execution",
    )


@router.get("/{job_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get the current status of a workflow execution.
    """
    # Get from cache
    workflow_data = cache_service.get(f"workflow:{job_id}")
    if not workflow_data:
        raise HTTPException(status_code=404, detail="Workflow not found")

    data = json.loads(workflow_data)

    # Check ownership
    if data.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Convert results through Pydantic model for camelCase serialization
    results_data = data.get("results")
    if results_data:
        results_obj = WorkflowResults(**results_data)
        # model_dump with by_alias=True gives camelCase
        results_dict = results_obj.model_dump(by_alias=True)
    else:
        results_dict = None

    return WorkflowStatusResponse(
        job_id=job_id,
        status=WorkflowStatus(data.get("status", "pending")),
        node_statuses={
            k: NodeExecutionStatus(**v)
            for k, v in data.get("node_statuses", {}).items()
        },
        started_at=data.get("started_at"),
        completed_at=data.get("completed_at"),
        error=data.get("error"),
        results=results_dict,
    )


@router.delete("/{job_id}")
async def cancel_workflow(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a running workflow.
    """
    # Get from cache
    workflow_data = cache_service.get(f"workflow:{job_id}")
    if not workflow_data:
        raise HTTPException(status_code=404, detail="Workflow not found")

    data = json.loads(workflow_data)

    # Check ownership
    if data.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if can be cancelled
    status = data.get("status")
    if status not in [WorkflowStatus.PENDING.value, WorkflowStatus.RUNNING.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel workflow in status: {status}",
        )

    # Update status
    data["status"] = WorkflowStatus.CANCELLED.value
    data["completed_at"] = datetime.utcnow().isoformat()

    cache_service.set_with_ttl(
        f"workflow:{job_id}",
        json.dumps(data),
        ttl=3600 * 24,
    )

    # TODO: Send cancel signal to worker

    return {"message": "Workflow cancelled"}


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@router.websocket("/{job_id}/stream")
async def workflow_stream(
    websocket: WebSocket,
    job_id: str,
):
    """
    WebSocket endpoint for real-time workflow status updates.

    Clients can connect to receive:
    - Node status changes
    - Progress updates
    - Log messages
    - Final results
    """
    await websocket.accept()

    try:
        # Verify workflow exists
        workflow_data = cache_service.get(f"workflow:{job_id}")
        if not workflow_data:
            await websocket.send_json({
                "type": "error",
                "message": "Workflow not found",
            })
            await websocket.close()
            return

        # Subscribe to Redis pub/sub for this workflow
        pubsub = cache_service.redis_client.pubsub()
        pubsub.subscribe(f"workflow:{job_id}:updates")

        # Send initial status
        data = json.loads(workflow_data)
        await websocket.send_json({
            "type": WSMessageType.STATUS_UPDATE.value,
            "job_id": job_id,
            "data": {
                "status": data.get("status"),
                "node_statuses": data.get("node_statuses", {}),
            },
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Listen for updates
        for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_json(json.loads(message["data"]))

            # Refresh data to check status
            workflow_data = cache_service.get(f"workflow:{job_id}")
            if workflow_data:
                data = json.loads(workflow_data)
                if data.get("status") in [
                    WorkflowStatus.COMPLETED.value,
                    WorkflowStatus.FAILED.value,
                    WorkflowStatus.CANCELLED.value,
                ]:
                    break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for workflow {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for workflow {job_id}: {e}")
    finally:
        try:
            pubsub.unsubscribe(f"workflow:{job_id}:updates")
        except:
            pass


# =============================================================================
# Helper Functions
# =============================================================================

async def _queue_workflow_job(job_id: str, priority: int = 0):
    """
    Queue a workflow execution job.

    Uses ARQ for background job processing.
    """
    from arq.connections import RedisSettings, create_pool
    from urllib.parse import urlparse
    from app.core.config import settings

    # Parse Redis URL into RedisSettings
    parsed = urlparse(settings.REDIS_URL)
    redis_settings = RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
        password=parsed.password,
    )

    # Create ARQ connection
    redis = await create_pool(redis_settings)

    # Enqueue the job
    await redis.enqueue_job(
        "handle_workflow_job",
        job_id,
        _queue_name="arq:queue",
    )

    await redis.close()


def publish_workflow_update(job_id: str, message: WSMessage):
    """
    Publish a workflow update to Redis pub/sub.

    This is called by the worker to notify connected WebSocket clients.
    """
    try:
        cache_service.redis_client.publish(
            f"workflow:{job_id}:updates",
            message.model_dump_json(),
        )
    except Exception as e:
        logger.error(f"Failed to publish workflow update: {e}")
