# Service Layer

> **Note**: This documentation reflects the current service implementations. The architecture may evolve as the platform develops.

## Overview

The service layer sits between API endpoints and data access, containing the core business logic of the platform. Services are designed as singletons that can be imported and used throughout the application.

---

## CacheService

**File**: `app/services/cache.py`

**Purpose**: Provides Redis-based caching to reduce database load and improve response times.

### What It Does

The CacheService stores frequently accessed data in Redis with automatic expiration. If Redis is unavailable, the service gracefully degrades - the application continues working, just without caching.

### Cached Data Types

| Data | Key Pattern | TTL | Use Case |
|------|-------------|-----|----------|
| **Dataset Schema** | `schema:{dataset_id}:{version_id}` | 24 hours | Column types, structure |
| **Dataset Preview** | `preview:{dataset_id}:{version_id}` | 1 hour | Sample rows for display |
| **Dataset Profile** | `profile:{dataset_id}:{version_id}` | 6 hours | Statistical summaries |
| **Job Status** | `job:{job_id}` | 1 hour | Processing progress |
| **User Datasets** | `user:{user_id}:datasets:{page}` | 5 minutes | Paginated list cache |

### Key Operations

**Storing Data**:
- Data is serialized to JSON before storing
- Each cache entry has a time-to-live (TTL)
- When TTL expires, Redis automatically deletes the entry

**Retrieving Data**:
- Returns cached value if exists and not expired
- Returns `None` if not found or expired
- Caller should fetch from database if cache miss

**Cache Invalidation**:
- When a dataset is updated, its cache entries are deleted
- User dataset list cache is cleared when datasets change
- This ensures users always see fresh data after changes

### Graceful Degradation

If Redis is unavailable:
- Application continues working
- All cache operations return `None` or succeed silently
- Performance is slower but functionality is preserved

---

## DatasetService

**File**: `app/services/datasets.py`

**Purpose**: Handles all dataset-related business logic including CRUD operations and version management.

### What It Does

The DatasetService manages the lifecycle of datasets from creation through deletion, including version control and storage quota management.

### Key Operations

**Creating Datasets**:
1. Validates the dataset name is unique for the user
2. Creates the dataset record in the database
3. Updates user's dataset count
4. Returns the created dataset

**Getting Datasets**:
1. Looks up dataset by ID
2. Verifies the requesting user owns it
3. Optionally includes version information
4. Returns dataset with current version metadata

**Listing Datasets**:
1. Queries user's datasets with filters
2. Supports search by name
3. Supports sorting by various fields
4. Returns paginated results with total count

**Deleting Datasets**:
1. Verifies ownership
2. Deletes dataset (CASCADE handles versions)
3. Updates user's dataset count and storage
4. Invalidates cache entries

**Creating Versions**:
1. Gets next version number for dataset
2. Creates version record in "pending" status
3. Sets up relationship to parent dataset
4. Returns version ready for processing

**Updating Versions**:
1. Updates status after processing
2. Stores file path, size, row/column counts
3. Updates parent dataset's current version
4. Link to schema and profile data

### Storage Quota

The service enforces storage limits based on user tier:

- Checks if adding new file would exceed quota
- Quota limits configurable via environment
- Returns boolean indicating if upload allowed

---

## R2Service

**File**: `app/services/r2.py`

**Purpose**: Manages all interactions with Cloudflare R2 (or MinIO for local development) object storage.

### What It Does

The R2Service handles file storage operations using the S3-compatible API. It's used for storing uploaded datasets and processed files.

### Key Operations

**Generating Upload URLs**:
1. Creates a presigned URL for direct browser upload
2. URL expires after a configurable time (default: 1 hour)
3. Includes proper CORS headers for browser access
4. Returns URL and expiration time

How presigned URLs work:
- URL contains temporary credentials embedded in it
- Browser uploads directly to R2, bypassing the API server
- More efficient for large files
- Reduces server bandwidth and memory usage

**Uploading Files** (Server-side):
1. Takes a local file path
2. Uploads to specified R2 key
3. Returns the file size
4. Used by workers after processing

**Downloading Files**:
1. Downloads from R2 to local filesystem
2. Creates parent directories if needed
3. Returns the local path
4. Used by workers for processing

**Checking Files**:
- `check_file_exists`: Verifies a key exists in R2
- `get_file_size`: Returns file size in bytes

**Generating Download URLs**:
1. Creates presigned URL for downloading
2. Expires after configurable time
3. Can be given to users for file access

**Deleting Files**:
- Can hard delete a file
- Or move to a "deleted" folder (soft delete)
- Soft delete allows recovery if needed

### Bucket Structure

```
{bucket}/
├── uploads/
│   └── temp/              # Temporary uploads before processing
│       └── {upload_id}.csv
├── datasets/
│   └── {user_id}/
│       └── {dataset_id}/
│           └── {version_id}.parquet
├── models/
│   └── {user_id}/
│       └── {model_id}/
└── deleted/               # Soft-deleted files
```

### Auto-Initialization

On startup, the service:
1. Creates the bucket if it doesn't exist
2. Configures CORS rules for browser uploads
3. Logs any configuration issues

---

## IngestionService

**File**: `app/services/ingestion.py`

**Purpose**: Processes uploaded datasets including parsing, validation, profiling, and format conversion.

### What It Does

When a user uploads a dataset, the IngestionService processes it through a pipeline that validates, analyzes, and converts the data into an efficient format.

### Key Operations

**Creating Ingestion Jobs**:
1. Creates a job record to track processing
2. Stores upload metadata (filename, size)
3. Sets initial status to "pending"
4. Returns job for queuing to workers

**Updating Job Status**:
1. Updates status as processing progresses
2. Records timing (started_at, completed_at)
3. Stores errors if processing fails
4. Updates cache with current progress

**Detecting File Format**:
- Examines file extension
- Supports CSV, Excel (XLS, XLSX), JSON, Parquet
- Returns appropriate enum value

**Loading DataFrames**:
1. Reads file into Polars DataFrame
2. Handles format-specific parsing
3. Supports streaming for large files
4. Raises errors for unsupported formats

**Extracting Schema**:
From a loaded DataFrame, extracts:
- Column names
- Data types
- Null counts per column
- Unique value counts (for categorical)

**Computing Profiles**:
For each column, calculates:
- Basic stats (count, null count)
- Numeric stats (mean, min, max, std)
- Categorical stats (unique values, top values)
- Data quality metrics

**Validating DataFrames**:
Checks for common issues:
- Row count validation
- Column count validation
- Data type consistency
- Missing value thresholds
- Returns list of warnings/errors

**Storing Profiles**:
1. Creates DatasetProfile record
2. Stores computed statistics as JSON
3. Links to dataset version
4. Makes profile available via cache

### Processing Pipeline

When a worker processes an ingestion job:

1. **Download**: Get file from R2 temp storage
2. **Load**: Parse into Polars DataFrame
3. **Validate**: Check for data issues
4. **Profile**: Compute statistics
5. **Convert**: Save as Parquet format
6. **Upload**: Put processed file in R2
7. **Store**: Save schema and profile to database
8. **Clean**: Remove temp file from R2
9. **Update**: Mark job as completed

### Why Parquet?

Original CSV files are converted to Parquet format because:
- Much faster to read (columnar format)
- Smaller file size (compression)
- Type information preserved
- Efficient for partial reads (only needed columns)

---

## How Services Work Together

Example: Dataset Upload Flow

```
1. User requests upload URL
   └─> R2Service.generate_presigned_upload_url()

2. User uploads file directly to R2

3. User confirms upload
   └─> IngestionService.create_ingestion_job()
   └─> DatasetService.create_dataset()
   └─> DatasetService.create_dataset_version()
   └─> Job queued to worker

4. Worker processes job
   └─> R2Service.download_file_from_r2()
   └─> IngestionService.load_dataframe()
   └─> IngestionService.validate_dataframe()
   └─> IngestionService.extract_schema()
   └─> IngestionService.compute_standard_profile()
   └─> R2Service.upload_file_to_r2() (Parquet)
   └─> DatasetService.update_dataset_version_status()
   └─> CacheService.cache_schema()
   └─> CacheService.cache_profile()

5. User views dataset
   └─> CacheService.get_cached_schema() // Try cache first
   └─> DatasetService.get_dataset() // If cache miss
```

---

## Singleton Pattern

All services use the singleton pattern:

- One instance is created when the module is imported
- The same instance is used throughout the application
- Exported at the bottom of each module

This ensures:
- Consistent state across requests
- Efficient resource usage (one Redis connection, etc.)
- Easy to import and use

**Importing Services**:
```python
from app.services import (
    r2_service,
    dataset_service,
    ingestion_service,
    cache_service
)
```

---

## Files Summary

| File | Service | Purpose |
|------|---------|---------|
| `cache.py` | CacheService | Redis caching for performance |
| `datasets.py` | DatasetService | Dataset CRUD and version management |
| `r2.py` | R2Service | Object storage operations |
| `ingestion.py` | IngestionService | Dataset processing and profiling |
| `ingestion_processor.py` | (Worker) | Actual processing logic for workers |
