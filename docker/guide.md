# Docker Setup Guide for AutoML Platform

Complete guide to set up PostgreSQL, Redis, and Celery using Docker Desktop.

---

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `docker/docker-compose.yml` | Defines PostgreSQL (port 5432) and Redis (port 6379) containers |
| `docker/.env` | Docker credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) |
| `apps/api/.env` | Application credentials (DATABASE_URL, REDIS_URL, CELERY settings) |

---

## 🚀 Quick Start

### Step 1: Start Docker Desktop
Open Docker Desktop and wait for the engine to start (green icon in system tray).

### Step 2: Start the Services
```bash
cd "c:\Folders\AutoML Platform 2.0\docker"
docker-compose up -d
```

### Step 3: Verify Services are Running
```bash
docker-compose ps
```
Expected output:
```
NAME              STATUS    PORTS
automl_postgres   Up        0.0.0.0:5432->5432/tcp
automl_redis      Up        0.0.0.0:6379->6379/tcp
```

### Step 4: Update API Environment for Local Docker
Edit `apps/api/.env` and update these lines:

```env
# Database (Local Docker PostgreSQL) 
DATABASE_URL=postgresql://automl_user:automl_dev_2024@localhost:5432/automl_dev

# Redis (Local Docker Redis)
REDIS_URL=redis://localhost:6379/0

# Celery Task Queue (add these lines)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 5: Run Database Migrations
```bash
cd "c:\Folders\AutoML Platform 2.0\apps\api"
alembic upgrade head
```

### Step 6: Start Celery Worker
```bash
cd "c:\Folders\AutoML Platform 2.0\apps\workers"
poetry run celery -A worker.celery_app worker --loglevel=info --pool=solo
```

> **Note:** On Windows, `--pool=solo` is required.

---

## 🔧 Common Commands

| Action | Command |
|--------|---------|
| Start services | `docker-compose up -d` |
| Stop services | `docker-compose down` |
| Stop & delete data | `docker-compose down -v` |
| View logs | `docker-compose logs -f` |
| PostgreSQL logs | `docker-compose logs -f postgres` |
| Redis logs | `docker-compose logs -f redis` |

### Connect to Databases Directly
```bash
# PostgreSQL
docker exec -it automl_postgres psql -U automl_user -d automl_dev

# Redis
docker exec -it automl_redis redis-cli
```

---

## 🔐 Credentials

### Docker Credentials (`docker/.env`)
```env
POSTGRES_USER=automl_user
POSTGRES_PASSWORD=automl_dev_2024
POSTGRES_DB=automl_dev
```

### Connection URLs for Application
```env
DATABASE_URL=postgresql://automl_user:automl_dev_2024@localhost:5432/automl_dev
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Docker Desktop                     │
│  ┌─────────────┐      ┌─────────────┐               │
│  │  PostgreSQL │      │    Redis    │               │
│  │   :5432     │      │   :6379     │               │
│  └──────┬──────┘      └─────┬───────┘               │
└─────────┼───────────────────┼───────────────────────┘
          │                   │
          ▼                   ▼
    ┌─────────────┐     ┌─────────────┐
    │  FastAPI    │────▶│   Celery    │
    │  (apps/api) │     │  (workers)  │
    └─────────────┘     └─────────────┘
```

---

## ⚠️ Switching Between Local and Cloud

Your current `apps/api/.env` has **cloud credentials** (Neon PostgreSQL + Upstash Redis).

| Environment | DATABASE_URL | REDIS_URL |
|-------------|--------------|-----------|
| **Local Docker** | `postgresql://automl_user:automl_dev_2024@localhost:5432/automl_dev` | `redis://localhost:6379/0` |
| **Cloud (Current)** | `postgresql://neondb_owner:...@...neon.tech/neondb` | `rediss://default:...@upstash.io:6379` |

To switch between environments, update the `DATABASE_URL` and `REDIS_URL` in `apps/api/.env`.
