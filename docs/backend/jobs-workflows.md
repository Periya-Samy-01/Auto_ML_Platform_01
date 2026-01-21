# Jobs & Workflows

> **Note**: This documentation reflects the current job and workflow implementation. The system may evolve as the platform develops.

## Overview

The Jobs & Workflows system is responsible for executing ML pipelines in the background. It consists of:

1. **Workflows** - User-designed ML pipelines (nodes and edges)
2. **Jobs** - Individual executions of workflows
3. **Workers** - Background processes that run the actual ML training
4. **Real-time Updates** - WebSocket streaming of execution progress

---

## How It Works

### The Execution Flow

1. **User designs workflow** in the canvas (connects nodes)
2. **User clicks Execute** → API validates and creates job
3. **Job is queued** in Redis via ARQ
4. **Worker picks up job** from queue
5. **Executor runs nodes** in topological order
6. **Progress updates** published via Redis pub/sub
7. **Frontend receives updates** via WebSocket
8. **Results stored** when complete

---

## Workflows

A workflow represents a machine learning pipeline designed by the user.

### Workflow Structure

Workflows consist of two parts:

**Nodes** - Individual processing steps:
- Dataset selection
- Preprocessing operations
- Train/test splitting
- Model training
- Evaluation
- Visualization

**Edges** - Connections between nodes:
- Define data flow direction
- Source node → Target node
- Determine execution order

### Node Types

| Type | Purpose | Inputs | Outputs |
|------|---------|--------|---------|
| **dataset** | Load data | None | DataFrame |
| **preprocessing** | Transform data | DataFrame | DataFrame |
| **split** | Train/test split | DataFrame | Train + Test DataFrames |
| **model** | Train model | Train DataFrame | Trained Model + Predictions |
| **evaluate** | Calculate metrics | Model + Test Data | Metrics |
| **visualize** | Create plots | Model + Data | Plot Images |

### Node Configuration

Each node stores its configuration in a `data` object:

**Dataset Node**:
- `datasetId`: Which dataset to use
- `targetColumn`: Column to predict
- `problemType`: classification, regression, or clustering

**Preprocessing Node**:
- `method`: Which preprocessor to use
- `parameters`: Method-specific options

**Split Node**:
- `testSize`: Fraction for test set (0.1 to 0.5)
- `randomState`: Random seed for reproducibility

**Model Node**:
- `algorithm`: Which ML algorithm
- `hyperparameters`: Algorithm settings

**Evaluate Node**:
- `metrics`: Which metrics to calculate

**Visualize Node**:
- `plots`: Which visualizations to generate

### Workflow Validation

Before execution, workflows are validated:

1. **Structure Check**:
   - All nodes are connected
   - No orphan nodes
   - No self-loops

2. **Cycle Detection**:
   - Graph must be acyclic (DAG)
   - Uses topological sort to detect cycles

3. **Connection Validation**:
   - Output types match input types
   - Required connections present
   - Model → Evaluate properly connected

4. **Configuration Check**:
   - Required fields populated
   - Valid parameter values
   - Dataset exists and accessible

### Workflow Snapshots

When a workflow is executed:
1. Current state is saved as a "snapshot"
2. Snapshot captures nodes, edges, and all configurations
3. Job references the snapshot (not the live workflow)
4. Allows re-running same configuration later
5. Users can edit workflow without affecting running jobs

---

## Jobs

A job represents a single execution of a workflow.

### Job Lifecycle

```
Created → Pending → Queued → Running → Completed
                              ↓
                           Failed
                              ↓
                           (Retry)
```

**States**:
- **pending**: Job created, waiting for queue
- **queued**: Job in Redis queue, waiting for worker
- **running**: Worker actively executing
- **completed**: Finished successfully
- **failed**: Error occurred
- **cancelled**: User cancelled

### Job Properties

| Property | Description |
|----------|-------------|
| **id** | Unique identifier (UUID) |
| **user_id** | Owner of the job |
| **workflow_snapshot_id** | Which snapshot to execute |
| **status** | Current lifecycle state |
| **credit_cost** | Credits charged for this job |
| **started_at** | When execution began |
| **completed_at** | When execution finished |
| **error_message** | Error details if failed |

### Job Nodes

Each node in the job has its own status:

| Property | Description |
|----------|-------------|
| **node_id** | Which node in workflow |
| **status** | pending, running, completed, failed, skipped |
| **started_at** | When node execution started |
| **completed_at** | When node execution finished |
| **output_data** | Results from node (metrics, etc.) |
| **error_message** | Error if node failed |

### Credit Calculation

Jobs consume credits based on:
- Base cost per job
- Dataset size (rows × columns)
- Model complexity
- Number of preprocessing steps
- Visualization count

Credits are reserved when job starts, charged when complete, refunded if cancelled or failed.

---

## Workers

Workers are background processes that execute jobs.

### ARQ Worker

The platform uses ARQ (Async Redis Queue) for job processing:

**Advantages**:
- Async/await support (non-blocking)
- Redis-based (shared with caching)
- Simple configuration
- Automatic retries

**Configuration** (in `worker.py`):

| Setting | Value | Purpose |
|---------|-------|---------|
| **max_jobs** | 10 | Concurrent jobs per worker |
| **job_timeout** | 1800 | 30 minutes max per job |
| **max_tries** | 3 | Retry count on failure |
| **retry_jobs** | True | Enable retry on failure |
| **health_check_interval** | 60 | Health check frequency |
| **keep_result** | 3600 | Keep result for 1 hour |

### Job Handlers

Two main job types:

**handle_ingestion_job**:
- Processes dataset uploads
- Runs in thread pool (CPU-bound tasks)
- Profiles and converts to Parquet

**handle_workflow_job**:
- Executes ML workflows
- Creates executor with status callback
- Publishes real-time updates

### Running a Worker

```bash
cd apps/api
poetry run arq app.worker.WorkerSettings
```

Multiple workers can run in parallel for scaling.

---

## Workflow Executor

The executor runs the actual workflow logic.

### How Execution Works

1. **Initialize Context**:
   - Create `NodeExecutionContext` to hold state
   - Store data as it flows through nodes

2. **Sort Nodes**:
   - Use topological sort on the graph
   - Ensures dependencies run first

3. **Execute Each Node**:
   - Update status to "running"
   - Call appropriate handler based on type
   - Store outputs in context
   - Update status to "completed" or "failed"

4. **Build Results**:
   - Collect all metrics and plots
   - Calculate total time and credits
   - Return `WorkflowResults` object

### NodeExecutionContext

Holds state during execution:

| Property | Description |
|----------|-------------|
| **raw_data** | Original dataset |
| **processed_data** | After preprocessing |
| **X_train, y_train** | Training features/target |
| **X_test, y_test** | Test features/target |
| **model** | Trained model instance |
| **predictions** | Model predictions |
| **probabilities** | Prediction probabilities |
| **target_column** | Name of target column |
| **problem_type** | classification/regression/clustering |
| **algorithm_name** | Which algorithm was used |
| **metrics** | Evaluation results |
| **plots** | Generated visualizations |
| **training_time** | Model training duration |

### Node Execution Methods

**_execute_dataset_node**:
1. Get dataset ID from config
2. Load from storage (user dataset or sample)
3. Set target column and problem type
4. Store in context.raw_data

**_execute_preprocessing_node**:
1. Get preprocessing method from config
2. Instantiate appropriate preprocessor
3. Fit and transform data
4. Store in context.processed_data

**_execute_split_node**:
1. Get test size from config
2. Separate features and target
3. Use sklearn's train_test_split
4. Store train/test sets in context

**_execute_model_node**:
1. Get algorithm from config
2. Get hyperparameters from config
3. Instantiate trainer
4. Fit on training data
5. Make predictions on test data
6. Store model and predictions

**_execute_evaluate_node**:
1. Get metrics to calculate
2. Select appropriate evaluator
3. Calculate metrics
4. Store in context.metrics

**_execute_visualize_node**:
1. Get plots to generate
2. Create each visualization
3. Save as image files
4. Store paths in context.plots

---

## Real-Time Updates

The system provides real-time execution updates via WebSocket.

### How It Works

1. **Worker publishes** status changes to Redis pub/sub
2. **API subscribes** to job-specific channel
3. **WebSocket sends** updates to connected clients
4. **Frontend updates** UI in real-time

### Message Format

```json
{
  "type": "node_status",
  "job_id": "abc-123",
  "node_id": "node-1",
  "status": "running",
  "progress": 0.5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Message Types

| Type | When Sent |
|------|-----------|
| **job_started** | Job begins execution |
| **node_status** | Node status changes |
| **node_progress** | During long operations |
| **job_completed** | Job finishes successfully |
| **job_failed** | Job encounters error |
| **metrics** | Final metrics available |

### WebSocket Endpoint

```
ws://localhost:8000/api/workflows/{job_id}/stream
```

Client connects and receives messages until job completes.

---

## Error Handling

### Retry Logic

Failed jobs can be retried:
1. ARQ automatically retries up to `max_tries` times
2. Retries have exponential backoff
3. User can manually retry from UI

### Error Capture

When node fails:
1. Exception captured with full traceback
2. Node status set to "failed"
3. Subsequent nodes marked as "skipped"
4. Error message stored in job record
5. User notified via WebSocket

### Timeout Protection

Jobs have timeouts to prevent stuck workers:
- Default: 30 minutes per job
- Long-running tasks use progress updates
- Orphaned jobs cleaned up periodically

---

## Files Summary

| File | Purpose |
|------|---------|
| `workflows/router.py` | API endpoints for workflows |
| `workflows/schemas.py` | Request/response models |
| `workflows/validator.py` | Workflow validation logic |
| `workflows/executor.py` | Workflow execution engine |
| `jobs/router.py` | API endpoints for jobs |
| `jobs/service.py` | Job business logic |
| `jobs/schemas.py` | Job request/response models |
| `worker.py` | ARQ worker configuration |
