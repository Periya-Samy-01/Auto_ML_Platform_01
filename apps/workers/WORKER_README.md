# 🚀 Celery Worker - Dataset Ingestion

## ✅ Implementation Complete!

The Celery worker task for dataset ingestion is now fully implemented with:

### Features Implemented:
1. **Complete Processing Pipeline**
   - Download temp files from R2
   - Load with Polars (CSV, JSON, Excel, Parquet)
   - Validate data integrity
   - Extract schema information
   - Compute statistical profiles
   - Convert to Parquet format
   - Calculate SHA-256 checksums
   - Upload to permanent R2 storage
   - Update database records
   - Cache results in Redis

2. **Robust Error Handling**
   - Automatic retry (3 attempts)
   - Exponential backoff
   - Comprehensive logging
   - Graceful failure handling

3. **Performance Optimizations**
   - Streaming for large files (>100MB)
   - Efficient Parquet compression
   - Worker memory management
   - Temp file cleanup

4. **Scheduled Tasks**
   - Daily cleanup of soft-deleted datasets
   - Stuck job detection every 30 minutes

## 📦 Setup Instructions

### 1. Install Dependencies
```bash
cd apps/workers
pip install -r requirements.txt
# or if using poetry:
poetry install
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add:
DATABASE_URL=your-postgres-url
REDIS_URL=redis://localhost:6379/0
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-key
R2_SECRET_ACCESS_KEY=your-secret
R2_BUCKET_NAME=automl-datasets-production
```

### 3. Run the Worker

#### Basic Worker:
```bash
celery -A worker.celery_app worker --loglevel=info
```

#### With Concurrency:
```bash
celery -A worker.celery_app worker --loglevel=info --concurrency=2
```

#### With Beat Scheduler (for cleanup tasks):
```bash
# Terminal 1: Worker
celery -A worker.celery_app worker --loglevel=info

# Terminal 2: Beat Scheduler
celery -A worker.celery_app beat --loglevel=info
```

## 🧪 Testing the Complete Flow

### 1. Start All Services:
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: API
cd apps/api
poetry run uvicorn app.main:app --reload

# Terminal 3: Worker
cd apps/workers
celery -A worker.celery_app worker --loglevel=info

# Terminal 4: Beat (optional)
cd apps/workers
celery -A worker.celery_app beat --loglevel=info
```

### 2. Test Upload Flow:

#### Step 1: Generate Upload URL
```bash
curl -X POST http://localhost:8000/api/datasets/upload-url \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_data.csv",
    "size_bytes": 1024
  }'
```

#### Step 2: Upload File to R2
```bash
# Use the presigned URL from step 1
curl -X PUT "PRESIGNED_URL_FROM_STEP_1" \
  --data-binary @your_file.csv
```

#### Step 3: Confirm Upload
```bash
curl -X POST http://localhost:8000/api/datasets/confirm \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "UUID_FROM_STEP_1",
    "dataset_name": "My Test Dataset",
    "description": "Testing the upload flow"
  }'
```

#### Step 4: Check Job Status
```bash
curl http://localhost:8000/api/datasets/jobs/JOB_ID_FROM_STEP_3 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 What Happens During Processing

1. **Job Starts** → Status: `processing`, Progress: 10%
2. **File Downloaded** → Progress: 20%
3. **Data Loaded** → Progress: 40%
4. **Validation & Profiling** → Progress: 60%
5. **Parquet Conversion** → Progress: 80%
6. **Upload & Finalize** → Status: `completed`, Progress: 100%

## 🔍 Monitoring

### Check Worker Logs:
```bash
tail -f celery.log
```

### Monitor Redis:
```bash
redis-cli monitor
```

### Check Job Status in Redis:
```bash
redis-cli
> GET job:YOUR_JOB_ID:status
```

## 🐛 Troubleshooting

### Common Issues:

1. **"File not found in R2"**
   - Ensure R2 credentials are correct
   - Check that upload completed successfully

2. **"Job stuck in processing"**
   - Check worker logs for errors
   - Ensure worker is running
   - Wait for stuck job checker (runs every 30 min)

3. **"Out of memory"**
   - Large files use streaming mode automatically
   - Adjust `WORKER_MAX_TASKS_PER_CHILD` in .env

4. **"Connection refused"**
   - Ensure Redis is running
   - Check DATABASE_URL is correct

## ⚡ Performance Notes

- Files >100MB use Polars lazy loading
- Parquet files are ~70% smaller than CSV
- Worker restarts after 10 tasks (prevent memory leaks)
- Concurrent processing: Set `--concurrency=N`
- Max task time: 30 minutes (configurable)

## 🎉 Ready for Production!

The dataset ingestion pipeline is now complete and ready for use!
