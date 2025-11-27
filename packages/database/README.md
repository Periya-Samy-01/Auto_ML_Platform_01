# AutoML Database Package

Shared SQLAlchemy models for the AutoML Platform. Used by both the API and Workers.

## Models

| Model | Description |
|-------|-------------|
| `User` | User accounts with soft-delete support |
| `Dataset` | Uploaded datasets with metadata |
| `Workflow` | Visual workflow definitions (mutable) |
| `WorkflowSnapshot` | Immutable snapshots for job execution |
| `Job` | Training job execution records |
| `JobNode` | Individual node execution within jobs |
| `Model` | Trained model artifacts |
| `CreditTransaction` | Immutable credit ledger |
| `CreditPackage` | Credit purchase packages |
| `Experiment` | Experiment groups for model comparison |
| `ExperimentRun` | Links jobs/models to experiments |
| `Tutorial` | Interactive learning content |
| `UserTutorialProgress` | User tutorial progress tracking |

## Enums

- `UserTier` - free, pro, enterprise
- `FileFormat` - csv, json, parquet, excel, unknown
- `ProblemType` - classification, regression, clustering, other
- `JobStatus` - pending, queued, running, failed, completed, cancelled
- `NodeType` - dataset, preprocess, model, visualize, save
- `NodeStatus` - pending, running, success, failed, skipped
- `TransactionType` - purchase, consumption, refund, adjustment
- `TutorialDifficulty` - beginner, intermediate, advanced
- `CreditTierRestriction` - none, pro_only, enterprise_only

## Usage

### In API (apps/api)

```python
from app.core.database import get_db, Base
from database.models import User, Dataset, Job

# In FastAPI endpoint
@app.get("/users/{user_id}")
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

### In Workers (apps/workers)

```python
import sys
from pathlib import Path

# Add packages to path
packages_path = Path(__file__).parent.parent.parent / "packages"
sys.path.insert(0, str(packages_path))

from database.session import get_db
from database.models import Job, JobNode
```

## Schema Notes

1. **Immutable Ledger**: `credit_transactions` table has triggers preventing UPDATE/DELETE
2. **Soft Deletes**: Users have `is_deleted` flag, hard delete after 30 days
3. **Counter Triggers**: `dataset_count`, `workflow_count`, `model_count` maintained by triggers
4. **Storage Tracking**: `storage_used_bytes` updated by triggers on dataset changes

## Database Triggers

The production PostgreSQL schema includes these triggers (applied via SQL, not Alembic):

- `credit_tx_before_insert` - Validates balance, updates user credits
- `credit_tx_no_update_delete` - Prevents modifications to ledger
- `users_inc/dec_*_count` - Maintains counter columns
- `users_adjust_storage_*` - Tracks storage usage
- `set_updated_at` - Auto-updates timestamps
