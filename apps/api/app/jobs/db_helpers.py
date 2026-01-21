"""
Database helper functions for job operations
"""

import uuid
from typing import Optional, Union

from sqlalchemy.orm import Session

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from packages.database.models.workflow_snapshot import WorkflowSnapshot


def _normalize_uuid(value: Union[uuid.UUID, str], db: Session) -> Union[uuid.UUID, str]:
    """
    Normalize UUID for database compatibility.
    SQLite needs string UUIDs, PostgreSQL can use native UUID type.
    
    Args:
        value: UUID or string
        db: Database session
        
    Returns:
        UUID for PostgreSQL, string for SQLite
    """
    if db.bind.dialect.name == 'sqlite':
        return str(value) if isinstance(value, uuid.UUID) else value
    return value if isinstance(value, uuid.UUID) else uuid.UUID(value)


def get_workflow_snapshot(
    db: Session,
    snapshot_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Optional[WorkflowSnapshot]:
    """
    Fetch workflow snapshot with authorization check.

    Args:
        db: Database session
        snapshot_id: Workflow snapshot UUID
        user_id: User UUID (for authorization)

    Returns:
        WorkflowSnapshot if found and authorized, None otherwise
    """
    # Normalize UUIDs for database compatibility
    snapshot_id_normalized = _normalize_uuid(snapshot_id, db)
    user_id_normalized = _normalize_uuid(user_id, db)
    
    snapshot = db.get(WorkflowSnapshot, snapshot_id_normalized)

    # Check ownership
    if snapshot and str(snapshot.user_id) == str(user_id_normalized):
        return snapshot

    return None
