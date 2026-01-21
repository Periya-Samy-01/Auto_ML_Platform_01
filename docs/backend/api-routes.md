# API Routes

> **Note**: This documentation reflects the current API structure. The endpoints may evolve as the platform develops.

## Overview

The AutoML Platform API provides RESTful endpoints for all platform functionality. All API endpoints (except health checks) require authentication via JWT tokens.

**Base URL**: `http://localhost:8000` (development)

**Authentication**: Include the JWT access token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## System Endpoints

These endpoints are used for monitoring and health checks. They don't require authentication.

### GET /

**Purpose**: Returns basic API information.

**Response**:
- `name`: Project name
- `version`: API version
- `docs`: Link to API documentation (only in development)
- `health`: Link to health check endpoint

---

### GET /health

**Purpose**: Basic health check to verify the API is running.

**Response**:
- `status`: "healthy"
- `service`: Service name
- `version`: API version
- `timestamp`: Current time

---

### GET /health/db

**Purpose**: Checks if the database connection is working.

**Response**:
- `status`: "healthy" or "unhealthy"
- `database`: "connected" or "disconnected"
- `error`: Error message (if unhealthy)

---

### GET /health/redis

**Purpose**: Checks if the Redis connection is working.

**Response**:
- `status`: "healthy" or "unhealthy"
- `redis`: "connected" or "disconnected"
- `error`: Error message (if unhealthy)

---

## Authentication Endpoints

Prefix: `/api/auth`

These endpoints handle user authentication and session management.

### GET /api/auth/google

**Purpose**: Initiates Google OAuth login flow.

**How it works**:
1. Frontend redirects user to this endpoint
2. Backend generates a state token for security (stored in Redis)
3. User is redirected to Google's login page
4. After login, Google redirects back to the callback URL

---

### GET /api/auth/google/callback

**Purpose**: Handles the redirect from Google after login.

**Query Parameters**:
- `code`: Authorization code from Google
- `state`: Security token (must match what was stored)
- `error`: Error message if login failed

**How it works**:
1. Validates the state token to prevent CSRF attacks
2. Exchanges the code for user information from Google
3. Creates a new user or finds existing user by email
4. Generates JWT tokens
5. Redirects to frontend with tokens in URL

---

### GET /api/auth/github

**Purpose**: Initiates GitHub OAuth login flow (same pattern as Google).

---

### GET /api/auth/github/callback

**Purpose**: Handles the redirect from GitHub after login (same pattern as Google).

---

### POST /api/auth/refresh

**Purpose**: Gets new access token using a refresh token.

**Request Body**:
- `refresh_token`: The refresh token

**Response**:
- `access_token`: New access token (valid 15 minutes)
- `refresh_token`: New refresh token (valid 7 days)

**Notes**:
- The old refresh token is blacklisted after use
- This prevents token reuse attacks

---

### POST /api/auth/logout

**Purpose**: Invalidates the user's session.

**Request Body**:
- `refresh_token`: The refresh token to invalidate

**How it works**:
- Adds the refresh token to a blacklist in Redis
- The access token continues working until it expires (15 min)

---

### GET /api/auth/me

**Purpose**: Gets the current user's profile information.

**Requires**: Authentication

**Response**:
- `id`: User ID
- `email`: User's email
- `full_name`: Display name
- `tier`: Subscription tier (free, pro, enterprise)
- `credit_balance`: Current credit balance
- `email_verified`: Whether email is verified
- `oauth_provider`: Which OAuth provider they used
- `created_at`: Account creation date
- `dataset_count`: Number of datasets owned
- `workflow_count`: Number of workflows owned
- `model_count`: Number of trained models
- `storage_used_bytes`: Storage space used

---

### POST /api/auth/dev-login

**Purpose**: Development-only login that bypasses OAuth.

**Note**: Only works when `DEBUG=true` or `ENVIRONMENT=development`

**Request Body**:
- `email`: Email address
- `full_name`: Optional display name

**Response**:
- `access_token`: JWT access token
- `refresh_token`: JWT refresh token
- `user`: Basic user information

---

## Dataset Endpoints

Prefix: `/api/datasets`

These endpoints manage dataset uploads and metadata.

### POST /api/datasets/upload-url

**Purpose**: Generates a presigned URL for uploading a file directly to storage.

**Requires**: Authentication

**Request Body**:
- `filename`: Name of the file being uploaded
- `size_bytes`: Size of the file in bytes

**Response**:
- `upload_id`: Unique identifier for this upload
- `upload_url`: Presigned URL to upload the file to
- `expires_at`: When the URL expires
- `max_size_bytes`: Maximum allowed file size for user's tier

**How it works**:
1. Checks if file size is within user's tier limits
2. Checks if user has enough storage quota
3. Generates a presigned URL for direct upload to R2/MinIO
4. Frontend uploads file directly to storage (not through API)

**Size Limits by Tier**:
- Free: Configurable via environment
- Pro: Larger limit
- Enterprise: Largest limit

---

### POST /api/datasets/confirm

**Purpose**: Confirms a file upload and starts processing it.

**Requires**: Authentication

**Request Body**:
- `upload_id`: ID from the upload-url response
- `dataset_name`: Name for the dataset
- `description`: Optional description
- `problem_type`: Optional (classification, regression, clustering)
- `target_column`: Optional target column name
- `create_new_version`: Whether to add version to existing dataset
- `dataset_id`: Required if creating new version
- `version_label`: Optional label for the version

**Response**:
- `job_id`: ID to track the processing job
- `dataset_id`: ID of the created/updated dataset
- `dataset_version_id`: ID of the version
- `version_number`: Version number (1, 2, 3, etc.)
- `status`: "pending"
- `estimated_duration_seconds`: Estimated processing time

**How it works**:
1. Verifies the file exists in storage
2. Creates dataset record (or finds existing)
3. Creates version record
4. Creates ingestion job
5. Queues job for background processing
6. Worker processes file (profiling, conversion to Parquet)

---

### GET /api/datasets

**Purpose**: Lists the user's datasets with pagination.

**Requires**: Authentication

**Query Parameters**:
- `page`: Page number (default 1)
- `per_page`: Items per page (default 20, max 100)
- `problem_type`: Filter by problem type
- `search`: Search in dataset names
- `sort_by`: Field to sort by (created_at, updated_at, name)
- `sort_order`: asc or desc

**Response**:
- `datasets`: Array of dataset objects
- `total`: Total number of datasets
- `page`: Current page
- `per_page`: Items per page
- `total_pages`: Total number of pages

**Dataset Object**:
- `id`: Dataset ID
- `name`: Dataset name
- `description`: Description
- `problem_type`: Type of ML problem
- `target_column`: Target column name
- `current_version_id`: ID of current version
- `row_count`: Number of rows
- `column_count`: Number of columns
- `columns_metadata`: Detailed column information
- `file_size_bytes`: Size of processed file
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

### GET /api/datasets/{dataset_id}

**Purpose**: Gets detailed information about a specific dataset.

**Requires**: Authentication

**Response**: Same as dataset object in list response, with full column metadata.

---

### DELETE /api/datasets/{dataset_id}

**Purpose**: Deletes a dataset and all its versions.

**Requires**: Authentication

**Response**:
- `message`: "Dataset deleted successfully"

**Notes**: This is a hard delete (data is permanently removed).

---

### GET /api/datasets/jobs/{job_id}

**Purpose**: Gets the status of a dataset processing job.

**Requires**: Authentication

**Response**:
- `job_id`: Job ID
- `status`: pending, processing, completed, or failed
- `progress_percentage`: 0-100
- `error_message`: Error details if failed
- `dataset_id`: Associated dataset
- `dataset_version_id`: Associated version
- `created_at`: When job was created
- `started_at`: When processing started
- `completed_at`: When processing finished

---

## Job Endpoints

Prefix: `/api/jobs`

These endpoints manage ML training jobs.

### POST /api/jobs

**Purpose**: Creates a new ML training job.

**Requires**: Authentication

**Request Body**:
- `workflow_snapshot_id`: ID of the workflow snapshot to execute
- Other job-specific parameters

**Response**:
- `id`: Job ID
- `status`: Initial status (queued)
- `estimated_cost`: Credit cost estimate
- Other job details

**How it works**:
1. Validates the workflow snapshot exists and belongs to user
2. Calculates estimated credit cost
3. Checks if user has enough credits
4. Creates job record
5. Queues job for background execution

---

### GET /api/jobs

**Purpose**: Lists the user's jobs with pagination and filtering.

**Requires**: Authentication

**Query Parameters**:
- `status_filter`: Filter by job status
- `page`: Page number
- `page_size`: Items per page (max 100)

**Response**:
- `items`: Array of job objects
- `total`: Total count
- Pagination metadata

---

### GET /api/jobs/{job_id}

**Purpose**: Gets detailed information about a specific job.

**Requires**: Authentication

**Response**: Complete job object including:
- Status and progress
- Timing information
- Results (if completed)
- Error details (if failed)

---

### POST /api/jobs/{job_id}/cancel

**Purpose**: Cancels a running or queued job.

**Requires**: Authentication

**Conditions**:
- Job must be in pending, queued, or running status
- Cannot cancel completed or failed jobs

**Response**:
- Updated job object with cancelled status

---

### POST /api/jobs/{job_id}/retry

**Purpose**: Retries a failed job.

**Requires**: Authentication

**How it works**:
1. Verifies the original job failed
2. Checks if user has enough credits
3. Creates new job with same workflow
4. Charges credits again

---

### GET /api/jobs/{job_id}/logs

**Purpose**: Gets detailed execution logs for a job.

**Requires**: Authentication

**Response**:
- Node execution statuses
- Timing for each node
- Error details per node
- Output summaries

---

### GET /api/jobs/stats

**Purpose**: Gets statistics about the user's jobs.

**Requires**: Authentication

**Response**:
- Job counts by status
- Total credits spent
- Average job duration
- Success rate

---

## Workflow Endpoints

Prefix: `/api/workflows`

These endpoints handle workflow validation and execution.

### POST /api/workflows/validate

**Purpose**: Validates a workflow without executing it.

**Requires**: Authentication

**Request Body**:
- `nodes`: Array of workflow nodes
- `edges`: Array of connections between nodes

**Response**:
- `valid`: true or false
- `errors`: Array of validation errors (if any)

**Checks performed**:
- Valid graph structure (no disconnected nodes)
- Proper node connections (correct input/output types)
- Required configurations present
- No cycles in the graph

---

### POST /api/workflows/execute

**Purpose**: Queues a workflow for execution.

**Requires**: Authentication

**Request Body**:
- `nodes`: Array of workflow nodes
- `edges`: Array of connections
- `workflow_id`: Optional workflow ID to update

**Response**:
- `job_id`: ID to track execution
- `status`: "queued"
- Other job details

**How it works**:
1. Validates the workflow first
2. Creates a workflow snapshot (frozen copy)
3. Creates a job record
4. Queues for background execution
5. Returns job ID for tracking

---

### GET /api/workflows/{job_id}/status

**Purpose**: Gets the current status of a workflow execution.

**Requires**: Authentication

**Response**:
- Overall job status
- Individual node statuses
- Progress information
- Results (if completed)

---

### POST /api/workflows/{job_id}/cancel

**Purpose**: Cancels a running workflow.

**Requires**: Authentication

---

### WebSocket /api/workflows/{job_id}/stream

**Purpose**: Real-time updates for workflow execution.

**How it works**:
1. Client connects to WebSocket
2. Server subscribes to Redis pub/sub channel for job
3. Worker publishes status updates as nodes complete
4. Server forwards updates to client
5. Connection closes when job finishes

**Message Types**:
- Node status changes
- Progress updates
- Log messages
- Final results

---

## Credit Endpoints

Prefix: `/api/credits`

These endpoints manage the user's credit balance.

### GET /api/credits/balance

**Purpose**: Gets the user's current credit balance.

**Requires**: Authentication

**Response**:
- `balance`: Current credit balance
- `total_earned`: Total credits earned (purchases + refunds)
- `total_spent`: Total credits consumed
- `transaction_count`: Total number of transactions

---

### GET /api/credits/transactions

**Purpose**: Lists the user's credit transactions.

**Requires**: Authentication

**Query Parameters**:
- `page`: Page number
- `page_size`: Items per page (max 100)

**Response**:
- `items`: Array of transaction objects
- `total`: Total count
- `has_more`: Whether more pages exist

**Transaction Object**:
- `id`: Transaction ID
- `type`: purchase, consumption, or refund
- `amount`: Credit amount (positive or negative)
- `balance_after`: Balance after transaction
- `description`: Description of transaction
- `created_at`: Transaction timestamp

---

### POST /api/credits/mock-purchase

**Purpose**: Creates a mock credit purchase for testing.

**Note**: Only works when `ALLOW_MOCK_PURCHASES=true`

**Requires**: Authentication

**Request Body**:
- `amount`: Number of credits to purchase
- `description`: Optional description

**Response**:
- `transaction_id`: Created transaction ID
- `amount`: Credits purchased
- `balance_after`: New balance
- `message`: Success message

---

## Plugin Endpoints

Prefix: `/api/plugins`

These endpoints provide information about available ML algorithms and preprocessing methods.

### GET /api/plugins

**Purpose**: Lists all available plugins (models and preprocessing methods).

**Query Parameters**:
- `problem_type`: Filter models by problem type

**Response**:
- `models`: Array of model plugin summaries
- `preprocessing`: Array of preprocessing method summaries

---

### GET /api/plugins/models

**Purpose**: Lists all available ML model plugins.

**Query Parameters**:
- `problem_type`: Filter by classification, regression, or clustering

**Response**: Array of model summaries:
- `slug`: Unique identifier
- `name`: Display name
- `description`: What the model does
- `icon`: Icon identifier
- `problemTypes`: Supported problem types
- `category`: Model category
- `bestFor`: What scenarios it's best for

---

### GET /api/plugins/models/{slug}

**Purpose**: Gets detailed information about a specific model.

**Query Parameters**:
- `problem_type`: Problem type for capabilities filtering

**Response**:
- All summary fields plus:
- `hyperparameters`: Main and advanced parameter definitions
- `capabilities`: Supported metrics and plots

**Hyperparameter Definition**:
- `key`: Parameter name
- `name`: Display name
- `type`: select, number, boolean, etc.
- `default`: Default value
- `description`: Help text
- `min`, `max`, `step`: For numeric inputs
- `options`: For select inputs
- `required`: Whether required

---

### GET /api/plugins/preprocessing

**Purpose**: Lists all preprocessing methods.

**Query Parameters**:
- `category`: Filter by category

---

### GET /api/plugins/preprocessing/categories

**Purpose**: Lists preprocessing categories.

**Response**: Array of categories:
- `key`: Category identifier
- `name`: Display name
- `description`: What it's for
- `icon`: Icon identifier

---

### GET /api/plugins/preprocessing/{slug}

**Purpose**: Gets detailed information about a preprocessing method.

---

### GET /api/plugins/metrics

**Purpose**: Lists all evaluation metrics.

**Query Parameters**:
- `problem_type`: Filter by problem type

---

### GET /api/plugins/plots

**Purpose**: Lists all visualization plot types.

**Query Parameters**:
- `problem_type`: Filter by problem type

---

## Error Responses

All endpoints may return these error responses:

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 402 | Payment Required - Insufficient credits |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File too big |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```
