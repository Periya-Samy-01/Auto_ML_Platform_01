# Backend Overview

> **Note**: This documentation reflects the current structure of the backend. The architecture may evolve as the platform develops.

## What is the Backend?

The backend is a **FastAPI application** that powers all server-side functionality of the AutoML Platform. It handles:

- User authentication (OAuth login, JWT tokens)
- Dataset uploads and storage
- ML workflow execution
- Background job processing
- Real-time updates via WebSocket

---

## How the Backend is Organized

The backend lives in `apps/api/` and follows a modular structure where each feature has its own directory.

```
apps/api/
├── app/                    # Main application code
│   ├── main.py            # Application entry point
│   ├── worker.py          # Background worker entry point
│   ├── auth/              # Authentication system
│   ├── core/              # Core configuration and utilities
│   ├── services/          # Business logic services
│   ├── ml/                # Machine learning components
│   ├── datasets/          # Dataset management
│   ├── jobs/              # Job management
│   ├── workflows/         # Workflow execution
│   ├── workflows/         # Workflow execution
│   └── plugins/           # Plugin system for algorithms
├── alembic/               # Database migrations
├── tests/                 # Test files
├── pyproject.toml         # Python dependencies (Poetry)
└── .env                   # Environment variables
```

---

## Entry Points

The backend has two main entry points:

### 1. API Server (`main.py`)

This is the FastAPI application that handles HTTP requests and WebSocket connections.

**What it does on startup:**
- Connects to Redis for caching and pub/sub
- Creates an ARQ connection pool for background jobs
- Sets up middleware (CORS, rate limiting)
- Registers all API routers

**How to run:**
```bash
cd apps/api
poetry run uvicorn app.main:app --reload
```

### 2. Background Worker (`worker.py`)

This is an ARQ worker that processes background jobs (like ML training).

**What it does:**
- Listens for jobs in the Redis queue
- Executes ML workflows in the background
- Publishes real-time updates via Redis pub/sub

**How to run:**
```bash
cd apps/api
poetry run arq app.worker.WorkerSettings
```

---

## Module Descriptions

### auth/

Handles everything related to user authentication and authorization.

| File | Purpose |
|------|---------|
| `router.py` | OAuth endpoints (Google, GitHub), token management |
| `jwt.py` | JWT token creation and validation |
| `oauth.py` | OAuth provider integrations |
| `redis.py` | Redis client for session storage |
| `dependencies.py` | FastAPI dependencies for auth |
| `schemas.py` | Request/response models |
| `service.py` | Authentication business logic |

### core/

Core functionality shared across the application.

| File | Purpose |
|------|---------|
| `config.py` | Environment configuration (settings) |
| `database.py` | Database session management |
| `middleware.py` | Custom middleware (rate limiting) |
| `routes.py` | Health check endpoints |
| `security.py` | Security utilities |

### services/

Business logic layer that coordinates between routes and data.

| File | Purpose |
|------|---------|
| `cache.py` | Redis caching service |
| `datasets.py` | Dataset CRUD operations |
| `ingestion.py` | Dataset upload processing |
| `ingestion_processor.py` | Dataset profiling and analysis |
| `r2.py` | Object storage operations (R2/MinIO) |

### ml/

Machine learning components for training and evaluation.

| Directory | Purpose |
|-----------|---------|
| `trainers/` | ML algorithm implementations |
| `evaluators/` | Model evaluation metrics |
| `preprocessors/` | Data preprocessing methods |
| `utils/` | ML utility functions |

### datasets/

Dataset management endpoints.

| File | Purpose |
|------|---------|
| `router.py` | API endpoints for datasets |

### jobs/

Job creation and monitoring.

| File | Purpose |
|------|---------|
| `router.py` | API endpoints for jobs |
| `schemas.py` | Job request/response models |
| `service.py` | Job business logic |

### workflows/

Workflow validation and execution.

| File | Purpose |
|------|---------|
| `router.py` | API endpoints including WebSocket |
| `schemas.py` | Workflow request/response models |
| `executor.py` | Workflow execution logic |
| `validator.py` | Workflow validation logic |

### credits/

Credit system for tracking usage.

| File | Purpose |
|------|---------|
| `router.py` | API endpoints for credits |
| `schemas.py` | Credit request/response models |
| `service.py` | Credit business logic |

### plugins/

Dynamic plugin system for algorithms and preprocessing.

| File | Purpose |
|------|---------|
| `router.py` | API endpoints for plugin info |
| `registry.py` | Plugin registration and lookup |
| `models.py` | Model plugin definitions |
| `preprocessing.py` | Preprocessing plugin definitions |
| `metrics.py` | Metric definitions |

---

## Middleware Stack

When a request comes in, it passes through these middleware layers in order:

1. **CORS Middleware** - Allows cross-origin requests from the frontend
2. **Rate Limit Middleware** - Prevents abuse by limiting request frequency
3. **Authentication** - Validates JWT tokens (via FastAPI dependencies)

---

## How Routes are Organized

All API routes are registered in `main.py` using FastAPI's router system:

| Router | Prefix | Purpose |
|--------|--------|---------|
| Core | `/` | Health checks, root endpoint |
| Auth | `/api/auth` | Login, logout, token management |
| Datasets | `/api/datasets` | Dataset CRUD operations |
| Jobs | `/api/jobs` | Job CRUD and monitoring |
| Workflows | `/api/workflows` | Workflow validation and execution |
| Plugins | `/api/plugins` | Plugin information |

---

## Database Connection

The backend uses SQLAlchemy to connect to PostgreSQL. The database session is managed via FastAPI's dependency injection:

- Sessions are created per-request
- Sessions are automatically closed after the request
- Connection pooling is used for efficiency

Database models are defined in the shared `packages/database/` package.

---

## Background Job Processing

The backend uses **ARQ** (Async Redis Queue) for background job processing. This allows long-running tasks like ML training to run without blocking HTTP requests.

**How it works:**

1. User submits a workflow execution request
2. API creates a job record in the database
3. API enqueues the job in Redis
4. Background worker picks up the job
5. Worker executes the workflow
6. Worker publishes status updates via Redis pub/sub
7. Frontend receives updates via WebSocket

---

## Environment Configuration

The backend reads configuration from environment variables. Key settings include:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `R2_ENDPOINT` | Object storage endpoint |
| `GOOGLE_CLIENT_ID` | OAuth client ID for Google |
| `GITHUB_CLIENT_ID` | OAuth client ID for GitHub |
| `JWT_SECRET` | Secret key for JWT signing |
| `FRONTEND_URL` | Frontend URL for redirects |

See `.env.example` for all available configuration options.
