# TypeScript Types

> **Note**: This documentation reflects the current type definitions. The types may evolve as the platform develops.

## Overview

The frontend uses TypeScript for type safety. All types are defined in the `types/` directory and organized by domain. Types are designed to match backend API schemas for seamless integration.

---

## Type Files

```
types/
├── index.ts       # Re-exports all types
├── auth.ts        # Authentication types
├── dataset.ts     # Dataset types
├── job.ts         # Job types
├── workflow.ts    # Workflow types
├── model.ts       # Model types
└── api.ts         # API response types
```

---

## Auth Types

**File**: `types/auth.ts`

Types for authentication and user management.

### User

Represents a user profile.

```typescript
interface User {
  id: string;
  email: string;
  full_name: string;
  tier: "free" | "pro" | "enterprise";
  credit_balance: number;
  email_verified: boolean;
  oauth_provider: "google" | "github" | null;
  created_at: string;
  dataset_count: number;
  workflow_count: number;
  model_count: number;
  storage_used_bytes: number;
}
```

### AuthState

State stored in the auth store.

```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
}
```

### TokenPair

JWT token pair returned from login.

```typescript
interface TokenPair {
  access_token: string;
  refresh_token: string;
}
```

---

## Dataset Types

**File**: `types/dataset.ts`

Types for dataset management.

### Enums

```typescript
type FileFormat = "csv" | "json" | "parquet" | "excel" | "unknown";
type ProblemType = "classification" | "regression" | "clustering" | "other";
```

### ColumnMetadata

Metadata for a single column after profiling.

```typescript
interface ColumnMetadata {
  name: string;           // Column name
  dtype: string;          // Data type (object, int64, float64, etc.)
  null_count: number;     // Number of null values
  null_percentage: number; // Percentage of nulls
  unique_count: number;   // Number of unique values
  sample_values?: unknown[]; // Sample values (optional)
}
```

### Dataset

A dataset record from the backend.

```typescript
interface Dataset {
  id: string;
  name: string;
  description: string | null;
  problem_type: ProblemType | null;
  target_column: string | null;
  current_version_id: string | null;
  row_count: number | null;
  column_count: number | null;
  columns_metadata: ColumnMetadata[] | null;
  file_size_bytes: number | null;
  created_at: string;
  updated_at: string;
  // Frontend-only fields for tracking uploads
  processing_job_id?: string;
  processing_status?: string;
  processing_progress?: number;
}
```

### Upload Types

For the multi-step upload flow:

```typescript
// Request presigned URL
interface UploadURLRequest {
  filename: string;
  size_bytes: number;
}

// Presigned URL response
interface UploadURLResponse {
  upload_id: string;
  upload_url: string;
  expires_at: string;
  max_size_bytes: number;
}

// Confirm upload request
interface ConfirmUploadRequest {
  upload_id: string;
  dataset_name: string;
  description?: string;
  problem_type?: ProblemType;
  target_column?: string;
  create_new_version?: boolean;
  dataset_id?: string;
  version_label?: string;
}

// Confirm upload response
interface ConfirmUploadResponse {
  job_id: string;
  dataset_id: string;
  dataset_version_id: string;
  version_number: number;
  status: string;
  estimated_duration_seconds: number;
}
```

### UploadState

Frontend-only state for tracking upload progress.

```typescript
interface UploadState {
  step: "idle" | "getting-url" | "uploading" | "confirming" | "processing" | "completed" | "error";
  progress: number;
  uploadId?: string;
  jobId?: string;
  datasetId?: string;
  error?: string;
}
```

### Pagination

```typescript
interface DatasetListResponse {
  datasets: Dataset[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

interface DatasetListParams {
  page?: number;
  per_page?: number;
  problem_type?: ProblemType;
  search?: string;
  sort_by?: "created_at" | "updated_at" | "name";
  sort_order?: "asc" | "desc";
  is_sample?: boolean;
}
```

---

## Workflow Types

**File**: `types/workflow.ts`

Types for workflows and the canvas.

### WorkflowNode

A node in the workflow graph.

```typescript
interface WorkflowNode {
  id: string;                        // Unique identifier
  type: string;                      // Node type (dataset, model, etc.)
  position: { x: number; y: number }; // Position on canvas
  data: Record<string, unknown>;     // Node-specific data
}
```

### WorkflowEdge

A connection between two nodes.

```typescript
interface WorkflowEdge {
  id: string;
  source: string;        // Source node ID
  target: string;        // Target node ID
  sourceHandle?: string; // Source connection point
  targetHandle?: string; // Target connection point
}
```

### WorkflowGraph

The complete workflow graph structure.

```typescript
interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}
```

### Workflow

A workflow record from the backend.

```typescript
interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  graph_json: WorkflowGraph | null;
  thumbnail_url: string | null;
  last_modified: string | null;
  created_at: string;
}
```

### WorkflowSnapshot

Immutable snapshot for execution.

```typescript
interface WorkflowSnapshot {
  id: string;
  workflow_id: string;
  user_id: string;
  graph_json: WorkflowGraph;
  snapshot_name: string | null;
  created_at: string;
}
```

---

## Job Types

**File**: `types/job.ts`

Types for job execution and monitoring.

### JobStatus Enum

```typescript
type JobStatus = "pending" | "queued" | "running" | "completed" | "failed" | "cancelled";
```

### Job

A job record with execution details.

```typescript
interface Job {
  id: string;
  user_id: string;
  workflow_snapshot_id: string;
  status: JobStatus;
  credit_cost: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}
```

### JobStatusResponse

Ingestion job status (for dataset processing).

```typescript
interface JobStatusResponse {
  job_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress_percentage: number;
  error_message: string | null;
  dataset_id: string;
  dataset_version_id: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}
```

---

## Model Types

**File**: `types/model.ts`

Types for trained models.

### Model

A trained model artifact.

```typescript
interface Model {
  id: string;
  user_id: string;
  job_id: string;
  name: string;
  algorithm: string;
  problem_type: ProblemType;
  metrics: Record<string, number>;
  hyperparameters: Record<string, unknown>;
  created_at: string;
}
```

---

## API Types

**File**: `types/api.ts`

Common API response types.

### ApiError

Standard error response structure.

```typescript
interface ApiError {
  detail: string;
  status_code?: number;
}
```

### PaginatedResponse

Generic paginated response.

```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

---

## Algorithm Types

**File**: `configs/algorithms/types.ts`

Types for algorithm configuration.

### AlgorithmId

Union of all valid algorithm identifiers.

```typescript
type AlgorithmId = 
  | "logisticRegression"
  | "decisionTree"
  | "randomForest"
  | "xgboost"
  | "knn"
  | "naiveBayes"
  | "svm"
  | "linearRegression"
  | "kmeans"
  | "neuralNetwork";
```

### HyperparameterDef

Definition for a configurable hyperparameter.

```typescript
interface HyperparameterDef {
  key: string;           // Parameter name
  name: string;          // Display name
  type: "number" | "select" | "boolean" | "string";
  default: unknown;      // Default value
  description: string;   // Help text
  min?: number;          // For number type
  max?: number;          // For number type
  step?: number;         // For number type
  options?: { value: unknown; label: string }[]; // For select type
  required?: boolean;
  advanced?: boolean;    // Show in advanced section
}
```

### AlgorithmConfig

Complete algorithm configuration.

```typescript
interface AlgorithmConfig {
  id: AlgorithmId;
  name: string;
  description: string;
  icon: string;
  category: string;
  problemTypes: ProblemType[];
  
  hyperparameters: {
    main: HyperparameterDef[];
    advanced: HyperparameterDef[];
  };
  
  capabilities: {
    supportsMulticlass: boolean;
    supportsProbabilities: boolean;
    supportsFeatureImportance: boolean;
    supportedMetrics: string[];
    supportedPlots: string[];
  };
}
```

---

## Using Types

### Importing Types

```typescript
// Import from index
import { User, Dataset, Workflow } from "@/types";

// Or from specific file
import { Dataset, ColumnMetadata } from "@/types/dataset";
```

### Type Assertions

```typescript
// Type-safe API responses
const response = await api.get<Dataset>(`/datasets/${id}`);
const dataset: Dataset = response.data;
```

### Type Guards

```typescript
function isProcessing(dataset: Dataset): boolean {
  return dataset.processing_status === "processing";
}
```

---

## Type Alignment with Backend

Types are designed to match backend Pydantic schemas:

| Frontend Type | Backend Schema |
|---------------|----------------|
| `User` | `UserResponse` |
| `Dataset` | `DatasetResponse` |
| `Workflow` | `WorkflowResponse` |
| `Job` | `JobResponse` |

This ensures:
- API responses can be directly typed
- Compile-time validation of data structures
- IntelliSense support in IDE
