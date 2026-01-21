# Storage Integration

> **Note**: This documentation reflects the current storage implementation. The configuration may evolve as the platform develops.

## Overview

The AutoML Platform uses **S3-compatible object storage** for storing datasets and trained models. In production, this is **Cloudflare R2**. For local development, we use **MinIO** as an S3-compatible alternative.

---

## Why Object Storage?

Object storage is used for:

- **Dataset files** - Large CSV/Parquet files that shouldn't live in the database
- **Trained models** - Serialized model files (joblib format)
- **Visualizations** - Generated plot images
- **Temporary uploads** - Files during the upload process

Benefits:
- Scalable to any file size
- Cost-effective for large files
- Direct browser uploads (presigned URLs)
- No server memory constraints

---

## Storage Architecture

### Production (Cloudflare R2)

Cloudflare R2 is S3-compatible storage with:
- No egress fees
- Global distribution
- S3 API compatibility

### Development (MinIO)

MinIO is a self-hosted S3-compatible server:
- Runs in Docker locally
- Same API as R2/S3
- Web console for debugging

---

## Bucket Structure

The storage bucket is organized as follows:

```
automl-datasets/
├── uploads/
│   └── temp/
│       └── {upload_id}.csv       # Temporary uploads
├── datasets/
│   └── {user_id}/
│       └── {dataset_id}/
│           └── {version_id}.parquet   # Processed datasets
├── models/
│   └── {user_id}/
│       └── {job_id}/
│           ├── model.joblib     # Trained model
│           └── metadata.json    # Model metadata
├── plots/
│   └── {job_id}/
│       └── {plot_name}.png      # Generated visualizations
└── deleted/
    └── ...                      # Soft-deleted files
```

---

## R2Service

The `R2Service` class (`app/services/r2.py`) handles all storage operations.

### Configuration

| Environment Variable | Purpose |
|---------------------|---------|
| `R2_ENDPOINT` | Storage endpoint URL |
| `R2_ACCESS_KEY_ID` | Access key |
| `R2_SECRET_ACCESS_KEY` | Secret key |
| `R2_BUCKET_NAME` | Bucket name |

### Production Configuration (Cloudflare R2)

```env
R2_ENDPOINT=https://{account_id}.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=automl-datasets
```

### Development Configuration (MinIO)

```env
R2_ENDPOINT=http://localhost:9000
R2_ACCESS_KEY_ID=minioadmin
R2_SECRET_ACCESS_KEY=minioadmin
R2_BUCKET_NAME=automl-datasets
```

---

## Key Operations

### Presigned Upload URLs

For large file uploads, we use presigned URLs:

1. **Frontend requests URL** from `/api/datasets/upload-url`
2. **Backend generates presigned URL** with temporary credentials
3. **Frontend uploads directly to storage** (bypasses API server)
4. **Frontend confirms upload** via `/api/datasets/confirm`

This approach:
- Reduces server load
- Handles large files efficiently
- Avoids memory issues
- Provides progress tracking

### Generating Presigned URLs

The service creates URLs that:
- Expire after 1 hour (configurable)
- Include temporary credentials in the URL
- Work directly from the browser
- Support PUT method for uploads

### Downloading Files

For workers processing data:
1. Worker calls `download_file_from_r2()`
2. File downloaded to local temp directory
3. Worker processes the file
4. Processed file uploaded back to storage
5. Temp file deleted

### File Existence Checks

Before operations, the service can:
- Check if a file exists
- Get file size
- Verify upload completion

---

## Upload Flow

### Step-by-Step Upload Process

```
1. User selects file in browser
        ↓
2. Frontend calls POST /api/datasets/upload-url
   - Sends: filename, size_bytes
        ↓
3. Backend validates:
   - File size within tier limit
   - Storage quota not exceeded
   - Generates upload_id
   - Creates presigned URL
        ↓
4. Backend returns:
   - upload_id, upload_url, expires_at
        ↓
5. Frontend uploads directly to storage
   - PUT request to presigned URL
   - Content-Type: application/octet-stream
        ↓
6. Frontend calls POST /api/datasets/confirm
   - Sends: upload_id, dataset_name, etc.
        ↓
7. Backend:
   - Verifies file exists in temp location
   - Creates dataset and version records
   - Queues ingestion job
        ↓
8. Worker:
   - Downloads file from temp location
   - Processes (profile, convert to Parquet)
   - Uploads to final location
   - Deletes temp file
```

---

## CORS Configuration

For browser-based uploads, CORS must be configured:

### MinIO CORS (minio-cors.json)

```json
{
  "CORSRules": [
    {
      "AllowedOrigin": ["http://localhost:3000", "*"],
      "AllowedMethod": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeader": ["*"],
      "ExposeHeader": ["ETag", "Content-Length"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

### Cloudflare R2 CORS

Configure via Cloudflare dashboard or API:
- Allow origins: your frontend domains
- Allow methods: GET, PUT, HEAD
- Allow headers: Content-Type, etc.

---

## MinIO Setup for Development

### Starting MinIO

MinIO is included in docker-compose:

```bash
cd docker
docker-compose up -d minio
```

### Ports

| Port | Purpose |
|------|---------|
| **9000** | S3 API endpoint |
| **9001** | Web console |

### Web Console

Access: http://localhost:9001

Credentials (default):
- Username: `minioadmin`
- Password: `minioadmin`

### Automatic Setup

The `minio-init` container automatically:
1. Creates the `automl-datasets` bucket
2. Sets public read policy
3. Configures CORS rules

---

## Security Considerations

### Presigned URL Security

- URLs expire after a short time (1 hour)
- Each URL is unique and single-use
- URLs include signature that validates request

### Access Control

- Files organized by user ID
- Backend validates user ownership before generating URLs
- No direct public access to user data

### Production Recommendations

1. Use private bucket with presigned-only access
2. Set short expiration times
3. Validate file types on upload
4. Scan uploaded files for malware
5. Use separate buckets for different data types

---

## Troubleshooting

### Common Issues

**Upload fails with 403 Forbidden**:
- Check CORS configuration
- Verify presigned URL hasn't expired
- Check Content-Type matches what was signed

**File not found after upload**:
- Verify upload completed successfully
- Check the temp key path is correct
- Verify bucket name matches

**MinIO not accessible**:
- Ensure Docker container is running
- Check port 9000 is not blocked
- Verify credentials are correct

### Debugging Commands

```bash
# Check MinIO logs
docker-compose logs -f minio

# List bucket contents
docker exec automl_minio mc ls myminio/automl-datasets

# Check if file exists
docker exec automl_minio mc stat myminio/automl-datasets/uploads/temp/{upload_id}.csv
```

---

## Files Summary

| File | Purpose |
|------|---------|
| `app/services/r2.py` | R2Service - storage operations |
| `docker/docker-compose.yml` | MinIO container definition |
| `docker/minio-cors.json` | CORS configuration for MinIO |
