# Database Models

> **Note**: This documentation reflects the current database schema. The structure may evolve as the platform develops.

## Overview

The AutoML Platform uses PostgreSQL as its primary database with SQLAlchemy as the ORM (Object-Relational Mapper). The database schema is designed to support:

- User accounts and authentication
- Dataset storage and versioning
- Workflow definitions (mutable) and snapshots (immutable)
- Job execution tracking
- Credit system for usage billing
- Trained model artifacts
- Experiments and tutorials

---

## Model Summary

| Model | Purpose |
|-------|---------|
| **User** | User accounts with authentication and billing info |
| **Dataset** | Metadata for uploaded datasets |
| **DatasetVersion** | Versioned dataset files with profiling data |
| **DatasetProfile** | Statistical profiles for dataset versions |
| **IngestionJob** | Dataset upload processing jobs |
| **Workflow** | User-designed ML pipelines (mutable) |
| **WorkflowSnapshot** | Immutable copies for job execution |
| **Job** | ML training job execution records |
| **JobNode** | Individual node status within jobs |
| **Model** | Trained model artifacts |
| **CreditTransaction** | Immutable credit ledger entries |
| **CreditPackage** | Available credit purchase packages |
| **Experiment** | Groups of related model comparisons |
| **ExperimentRun** | Links jobs and models to experiments |
| **Tutorial** | Interactive learning content |
| **UserTutorialProgress** | User progress through tutorials |

---

## Core Models

### User

Stores user account information and aggregated statistics.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **email** | String | Unique email address |
| **full_name** | String | Display name |
| **oauth_provider** | Enum | google, github, or null |
| **oauth_id** | String | ID from OAuth provider |
| **tier** | Enum | free, pro, enterprise |
| **credit_balance** | Integer | Current credit balance |
| **email_verified** | Boolean | Whether email is verified |
| **is_deleted** | Boolean | Soft delete flag |
| **dataset_count** | Integer | Number of datasets owned |
| **workflow_count** | Integer | Number of workflows owned |
| **model_count** | Integer | Number of trained models |
| **storage_used_bytes** | BigInt | Total storage consumption |
| **created_at** | DateTime | Account creation time |
| **updated_at** | DateTime | Last update time |

**Relationships**:
- Has many Datasets
- Has many Workflows
- Has many Jobs
- Has many CreditTransactions
- Has many Models

**Notes**:
- Counter fields (dataset_count, etc.) are maintained by database triggers
- Soft delete allows account recovery within 30 days
- Storage tracking enables quota enforcement

---

### Dataset

Represents an uploaded dataset (the container, not the actual file).

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **user_id** | UUID | Owner (foreign key) |
| **name** | String | Display name |
| **description** | Text | Optional description |
| **problem_type** | Enum | classification, regression, clustering |
| **target_column** | String | Column to predict |
| **current_version_id** | UUID | Active version (foreign key) |
| **created_at** | DateTime | Creation time |
| **updated_at** | DateTime | Last update time |

**Relationships**:
- Belongs to User
- Has many DatasetVersions
- Has one current_version

**Notes**:
- A dataset can have multiple versions (for iterative updates)
- Deleting a dataset cascades to all versions

---

### DatasetVersion

A specific version of a dataset with its processed file.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **dataset_id** | UUID | Parent dataset (foreign key) |
| **upload_id** | UUID | Upload tracking ID |
| **version_number** | Integer | Sequential version (1, 2, 3...) |
| **version_label** | String | Optional label (e.g., "cleaned") |
| **original_filename** | String | Original uploaded filename |
| **original_format** | Enum | csv, json, parquet, excel |
| **original_size_bytes** | BigInt | Original file size |
| **s3_path** | String | Path to processed Parquet file |
| **parquet_size_bytes** | BigInt | Processed file size |
| **row_count** | Integer | Number of rows |
| **column_count** | Integer | Number of columns |
| **columns_metadata** | JSONB | Column names, types, stats |
| **status** | String | pending, processing, completed, failed |
| **created_at** | DateTime | Creation time |

**Relationships**:
- Belongs to Dataset
- Has one DatasetProfile
- Has many IngestionJobs

---

### Workflow

A mutable workflow design that users can edit.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **user_id** | UUID | Owner (foreign key) |
| **name** | String | Workflow name |
| **description** | Text | Optional description |
| **definition** | JSONB | Nodes and edges as JSON |
| **is_deleted** | Boolean | Soft delete flag |
| **created_at** | DateTime | Creation time |
| **updated_at** | DateTime | Last update time |

**Relationships**:
- Belongs to User
- Has many WorkflowSnapshots
- Has many Jobs (through snapshots)

---

### WorkflowSnapshot

Immutable copy of a workflow at execution time.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **workflow_id** | UUID | Source workflow (foreign key, nullable) |
| **user_id** | UUID | Owner (foreign key) |
| **snapshot_data** | JSONB | Complete workflow definition |
| **created_at** | DateTime | Snapshot time |

**Relationships**:
- Belongs to Workflow (optionally)
- Belongs to User
- Has many Jobs

**Notes**:
- Snapshots preserve exact state for reproducibility
- workflow_id can be null (workflow deleted but jobs remain)

---

### Job

An execution of a workflow snapshot.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **user_id** | UUID | Owner (foreign key) |
| **workflow_snapshot_id** | UUID | What to execute (foreign key) |
| **status** | Enum | pending, queued, running, completed, failed, cancelled |
| **credit_cost** | Integer | Credits charged |
| **priority** | Integer | Queue priority |
| **celery_task_id** | String | ARQ job tracking ID |
| **results** | JSONB | Execution results |
| **error_message** | Text | Error details if failed |
| **error_traceback** | Text | Full stack trace if failed |
| **created_at** | DateTime | Job creation time |
| **started_at** | DateTime | Execution start time |
| **completed_at** | DateTime | Execution end time |

**Relationships**:
- Belongs to User
- Belongs to WorkflowSnapshot
- Has many JobNodes
- Has many Models (created by this job)

---

### JobNode

Status of individual nodes within a job.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **job_id** | UUID | Parent job (foreign key) |
| **node_id** | String | Node ID from workflow |
| **node_type** | Enum | dataset, preprocess, model, etc. |
| **status** | Enum | pending, running, success, failed, skipped |
| **output_data** | JSONB | Node-specific outputs |
| **error_message** | Text | Error if failed |
| **started_at** | DateTime | Node start time |
| **completed_at** | DateTime | Node end time |

**Relationships**:
- Belongs to Job

---

### Model

A trained machine learning model artifact.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **user_id** | UUID | Owner (foreign key) |
| **job_id** | UUID | Job that created it (foreign key) |
| **name** | String | Model name |
| **algorithm** | String | Algorithm used (e.g., "random_forest") |
| **problem_type** | Enum | classification, regression, clustering |
| **metrics** | JSONB | Performance metrics |
| **hyperparameters** | JSONB | Training hyperparameters |
| **s3_path** | String | Path to saved model file |
| **is_deployed** | Boolean | Whether model is deployed |
| **created_at** | DateTime | Creation time |

**Relationships**:
- Belongs to User
- Belongs to Job
- Has many ExperimentRuns

---

## Credit System Models

### CreditTransaction

Immutable ledger of all credit operations.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **user_id** | UUID | User (foreign key) |
| **type** | Enum | purchase, consumption, refund, adjustment |
| **amount** | Integer | Credit amount (positive or negative) |
| **balance_after** | Integer | Balance after transaction |
| **description** | Text | Transaction description |
| **job_id** | UUID | Related job (for consumption) |
| **package_id** | UUID | Related package (for purchase) |
| **stripe_payment_id** | String | Stripe reference (for purchase) |
| **created_at** | DateTime | Transaction time |

**Notes**:
- Table has triggers preventing UPDATE and DELETE
- Ensures audit trail is immutable
- balance_after calculated from previous transaction

---

### CreditPackage

Available credit purchase options.

| Field | Type | Description |
|-------|------|-------------|
| **id** | UUID | Primary key |
| **name** | String | Package name |
| **credits** | Integer | Credits in package |
| **price_cents** | Integer | Price in cents |
| **stripe_price_id** | String | Stripe price reference |
| **is_active** | Boolean | Whether available for purchase |
| **tier_restriction** | Enum | none, pro_only, enterprise_only |

---

## Enums

### UserTier
- **free**: Default tier with limited resources
- **pro**: Paid tier with increased limits
- **enterprise**: Business tier with highest limits

### FileFormat
- **csv**: Comma-separated values
- **json**: JSON format
- **parquet**: Apache Parquet
- **excel**: Excel spreadsheet
- **unknown**: Unrecognized format

### ProblemType
- **classification**: Predict categories
- **regression**: Predict continuous values
- **clustering**: Group similar items
- **other**: Other ML tasks

### JobStatus
- **pending**: Created, not yet queued
- **queued**: In queue, waiting for worker
- **running**: Currently executing
- **completed**: Finished successfully
- **failed**: Encountered error
- **cancelled**: Stopped by user

### NodeStatus
- **pending**: Not yet started
- **running**: Currently executing
- **success**: Completed successfully
- **failed**: Encountered error
- **skipped**: Skipped due to upstream failure

### TransactionType
- **purchase**: Bought credits
- **consumption**: Used credits (job execution)
- **refund**: Credits returned
- **adjustment**: Manual adjustment by admin

---

## Database Features

### Triggers

PostgreSQL triggers maintain data consistency:

**Credit Triggers**:
- Validate balance before insert
- Update user credit_balance automatically
- Prevent UPDATE and DELETE on transactions

**Counter Triggers**:
- Increment/decrement dataset_count, workflow_count, model_count
- Update when records are created/deleted

**Storage Triggers**:
- Adjust storage_used_bytes on dataset changes
- Enables quota enforcement

**Timestamp Triggers**:
- Auto-update updated_at on record changes

### Soft Deletes

Users and some resources have soft delete:
- is_deleted flag set to true
- Record remains in database
- Hard delete after retention period (30 days)
- Allows account recovery

### Connection Pooling

SQLAlchemy manages connections efficiently:
- Pool size: 20 connections
- Max overflow: 10 additional
- Pre-ping: Verify connection health

---

## Database Location

Models are defined in the shared package:

```
packages/database/
├── __init__.py         # Package exports
├── base.py             # SQLAlchemy Base class
├── config.py           # Database configuration
├── session.py          # Session management
├── types.py            # Custom column types
└── models/
    ├── __init__.py     # Model exports
    ├── enums.py        # Enum definitions
    ├── user.py         # User model
    ├── dataset.py      # Dataset model
    ├── dataset_version.py
    ├── dataset_profile.py
    ├── ingestion_job.py
    ├── workflow.py
    ├── workflow_snapshot.py
    ├── job.py
    ├── job_node.py
    ├── model.py
    ├── credit_transaction.py
    ├── credit_package.py
    ├── experiment.py
    ├── experiment_run.py
    ├── tutorial.py
    └── user_tutorial_progress.py
```

---

## Migrations

Database migrations are managed with Alembic:

```
apps/api/alembic/
├── alembic.ini         # Configuration
├── env.py              # Environment setup
└── versions/           # Migration scripts
```

**Running migrations**:
```bash
cd apps/api
alembic upgrade head
```

**Creating new migration**:
```bash
alembic revision --autogenerate -m "description"
```
