# Docker Configuration

> **Note**: This documentation reflects the current Docker setup. The configuration may evolve as the platform develops.

## Overview

Docker is used for local development to run the infrastructure services that the AutoML Platform depends on:

- **PostgreSQL** - Primary database
- **Redis** - Caching, sessions, and job queue
- **MinIO** - S3-compatible object storage

The application code (FastAPI, Next.js) runs natively on the host machine, connecting to these containerized services.

---

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Terminal access

### Start All Services

```bash
cd docker
docker-compose up -d
```

### Verify Services

```bash
docker-compose ps
```

Expected output:
```
NAME              STATUS    PORTS
automl_postgres   Up        0.0.0.0:5432->5432/tcp
automl_redis      Up        0.0.0.0:6379->6379/tcp
automl_minio      Up        0.0.0.0:9000->9000/tcp, 0.0.0.0:9001->9001/tcp
```

### Stop Services

```bash
# Stop but keep data
docker-compose down

# Stop and delete all data
docker-compose down -v
```

---

## Services

### PostgreSQL

The primary database for storing all application data.

| Property | Value |
|----------|-------|
| **Image** | postgres:16-alpine |
| **Container Name** | automl_postgres |
| **Port** | 5432 |
| **Volume** | postgres_data |

**Default Credentials**:
- Username: `automl_user`
- Password: `automl_password`
- Database: `automl_dev`

**Connection URL**:
```
postgresql://automl_user:automl_password@localhost:5432/automl_dev
```

**Health Check**: `pg_isready` command every 10 seconds

---

### Redis

Used for caching, session storage, and background job queue (ARQ).

| Property | Value |
|----------|-------|
| **Image** | redis:7-alpine |
| **Container Name** | automl_redis |
| **Port** | 6379 |
| **Volume** | redis_data |

**Connection URL**:
```
redis://localhost:6379/0
```

**Configuration**:
- Persistence enabled (`appendonly yes`)
- No authentication (local dev only)

**Health Check**: `redis-cli ping` every 10 seconds

---

### MinIO

S3-compatible object storage for datasets and models.

| Property | Value |
|----------|-------|
| **Image** | minio/minio:latest |
| **Container Name** | automl_minio |
| **S3 Port** | 9000 |
| **Console Port** | 9001 |
| **Volume** | minio_data |

**Default Credentials**:
- Username: `minioadmin`
- Password: `minioadmin`

**S3 Endpoint**:
```
http://localhost:9000
```

**Web Console**:
```
http://localhost:9001
```

---

### MinIO Initialization

A helper container that sets up MinIO on first run.

| Property | Value |
|----------|-------|
| **Image** | minio/mc:latest |
| **Container Name** | automl_minio_init |
| **Depends On** | minio (healthy) |

**What It Does**:
1. Waits for MinIO to be healthy
2. Creates `automl-datasets` bucket
3. Sets bucket policy to public
4. Configures CORS for browser uploads
5. Exits after setup

---

## Docker Compose File

The complete `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: automl_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-automl_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-automl_password}
      POSTGRES_DB: ${POSTGRES_DB:-automl_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-automl_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: automl_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: automl_minio
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin}
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio-init:
    image: minio/mc:latest
    container_name: automl_minio_init
    depends_on:
      minio:
        condition: service_healthy
    volumes:
      - ./minio-cors.json:/tmp/cors.json:ro
    entrypoint: >
      /bin/sh -c "
      mc alias set myminio http://minio:9000 minioadmin minioadmin;
      mc mb myminio/automl-datasets --ignore-existing;
      mc anonymous set public myminio/automl-datasets;
      echo 'MinIO bucket created and configured!';
      "

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## Environment Variables

### Docker Environment (docker/.env)

```env
POSTGRES_USER=automl_user
POSTGRES_PASSWORD=automl_password
POSTGRES_DB=automl_dev
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

### Application Environment (apps/api/.env)

Update these to connect to Docker services:

```env
# Database
DATABASE_URL=postgresql://automl_user:automl_password@localhost:5432/automl_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage (MinIO)
R2_ENDPOINT=http://localhost:9000
R2_ACCESS_KEY_ID=minioadmin
R2_SECRET_ACCESS_KEY=minioadmin
R2_BUCKET_NAME=automl-datasets
```

---

## Common Commands

### Service Management

| Action | Command |
|--------|---------|
| Start all services | `docker-compose up -d` |
| Stop all services | `docker-compose down` |
| Stop and delete data | `docker-compose down -v` |
| Restart a service | `docker-compose restart postgres` |
| View all logs | `docker-compose logs -f` |
| View specific logs | `docker-compose logs -f postgres` |

### Database Operations

```bash
# Connect to PostgreSQL
docker exec -it automl_postgres psql -U automl_user -d automl_dev

# Run SQL file
docker exec -i automl_postgres psql -U automl_user -d automl_dev < script.sql

# Create database backup
docker exec automl_postgres pg_dump -U automl_user automl_dev > backup.sql

# Restore from backup
docker exec -i automl_postgres psql -U automl_user -d automl_dev < backup.sql
```

### Redis Operations

```bash
# Connect to Redis CLI
docker exec -it automl_redis redis-cli

# View all keys
docker exec -it automl_redis redis-cli KEYS '*'

# Flush all data
docker exec -it automl_redis redis-cli FLUSHALL
```

### MinIO Operations

```bash
# List bucket contents
docker exec automl_minio mc ls myminio/automl-datasets

# Check MinIO status
docker exec automl_minio curl http://localhost:9000/minio/health/live
```

---

## Volume Management

Data persists in Docker volumes:

| Volume | Contains |
|--------|----------|
| `postgres_data` | PostgreSQL database files |
| `redis_data` | Redis persistence files |
| `minio_data` | MinIO uploaded files |

### Viewing Volumes

```bash
docker volume ls
```

### Removing Volumes (Deletes All Data!)

```bash
# Remove specific volume
docker volume rm docker_postgres_data

# Remove all unused volumes
docker volume prune
```

---

## Troubleshooting

### Port Already in Use

If a port is already taken:

```bash
# Find what's using port 5432
netstat -ano | findstr :5432

# Or change the port in docker-compose.yml
ports:
  - "5433:5432"  # Map to different host port
```

### Container Won't Start

Check logs for errors:

```bash
docker-compose logs postgres
```

Common issues:
- Previous container not stopped cleanly
- Corrupted volume data
- Port conflict

Fix: Try removing and recreating:

```bash
docker-compose down -v
docker-compose up -d
```

### Database Connection Refused

1. Verify container is running: `docker-compose ps`
2. Check container health: `docker-compose ps` shows "healthy"
3. Test connection: `docker exec automl_postgres pg_isready`
4. Verify host connection: Use `localhost`, not `127.0.0.1` sometimes

### MinIO Bucket Not Created

If the init container failed:

```bash
# Check init logs
docker-compose logs minio-init

# Manually create bucket
docker exec automl_minio mc mb myminio/automl-datasets
```

---

## Development Workflow

### Typical Workflow

1. **Start Docker services**:
   ```bash
   cd docker && docker-compose up -d
   ```

2. **Run database migrations**:
   ```bash
   cd apps/api && alembic upgrade head
   ```

3. **Start backend**:
   ```bash
   cd apps/api && poetry run uvicorn app.main:app --reload
   ```

4. **Start worker**:
   ```bash
   cd apps/api && poetry run arq app.worker.WorkerSettings
   ```

5. **Start frontend**:
   ```bash
   cd apps/web && npm run dev
   ```

### Switching Environments

To switch between local Docker and cloud services, update `apps/api/.env`:

| Service | Local Docker | Cloud |
|---------|--------------|-------|
| **Database** | localhost:5432 | Neon/Supabase URL |
| **Redis** | localhost:6379 | Upstash URL |
| **Storage** | localhost:9000 | R2 endpoint |

---

## Files Summary

| File | Purpose |
|------|---------|
| `docker/docker-compose.yml` | Service definitions |
| `docker/.env` | Docker environment variables |
| `docker/.env.example` | Example environment file |
| `docker/minio-cors.json` | MinIO CORS configuration |
| `docker/guide.md` | Original setup guide |
