# AutoML Platform 2.0 - Overview

> **Note**: This documentation reflects the current structure of the project. The architecture may evolve as the platform develops.

## What is AutoML Platform?

AutoML Platform 2.0 is a **no-code machine learning training platform** that allows users to build, train, and evaluate ML models without writing code. Users create visual workflows by connecting nodes on a canvas, similar to how you might connect blocks in a flowchart.

### Who is it for?

- Data scientists who want to prototype quickly
- Business analysts who need ML capabilities without coding
- Developers who want a visual interface for ML workflows
- Students learning machine learning concepts

### What can you do with it?

- Upload datasets (CSV files)
- Preprocess data (handle missing values, scale features, encode categories)
- Train machine learning models (classification, regression, clustering)
- Evaluate model performance with various metrics
- Visualize results with plots and charts

---

## Technology Stack

### Backend (Python)

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework for building the REST API |
| **SQLAlchemy** | Database ORM for PostgreSQL |
| **ARQ** | Background job queue (Redis-based) |
| **Pydantic** | Data validation and serialization |
| **scikit-learn** | Machine learning algorithms |
| **XGBoost** | Gradient boosting models |

### Frontend (TypeScript)

| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework with App Router |
| **React Flow** | Visual canvas for building workflows |
| **Zustand** | State management |
| **Shadcn/UI** | Component library |
| **TailwindCSS** | Styling |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **PostgreSQL** | Primary database |
| **Redis** | Caching, sessions, job queue |
| **Cloudflare R2** / MinIO | Object storage for datasets and models |
| **Docker** | Containerization for local development |

---

## Repository Structure

```
AutoML Platform 2.0/
├── apps/
│   ├── api/              # Backend - FastAPI application
│   ├── web/              # Frontend - Next.js application
│   └── cli/              # Command-line interface tool
├── packages/
│   └── database/         # Shared database models and configuration
├── docker/               # Docker compose and configuration
├── docs/                 # This documentation
├── Design/               # Original architecture design documents
└── scripts/              # Utility scripts
```

### apps/api (Backend)

The backend is a FastAPI application that provides:
- REST API endpoints for all platform features
- WebSocket support for real-time job updates
- Background workers for ML training jobs
- Authentication via OAuth (Google, GitHub) and JWT tokens

**Key directories:**
- `app/auth/` - Authentication and authorization
- `app/core/` - Configuration, database, middleware
- `app/services/` - Business logic (datasets, caching, storage)
- `app/ml/` - Machine learning trainers, evaluators, preprocessors
- `app/jobs/` - Job creation and management
- `app/workflows/` - Workflow validation and execution
- `app/workflows/` - Workflow validation and execution
- `app/plugins/` - Plugin system for ML algorithms and preprocessing

### apps/web (Frontend)

The frontend is a Next.js application that provides:
- User authentication flow
- Dashboard for managing datasets and jobs
- Visual playground canvas for building workflows
- Real-time job status updates

**Key directories:**
- `app/` - Next.js pages and routes
- `components/` - React components
- `stores/` - Zustand state stores
- `lib/` - Utilities and API clients
- `configs/` - Algorithm configurations

### packages/database

Shared database package containing:
- SQLAlchemy models for all database tables
- Database connection configuration
- Common type definitions

---

## Key Concepts

### Workflows

A **workflow** is a collection of connected nodes that define an ML pipeline. Think of it like a recipe - each node is a step, and the connections define the order of operations.

Example workflow:
```
Dataset → Train/Test Split → Model Training → Evaluation
```

### Nodes

Nodes are the building blocks of workflows. Each node has a specific purpose:

| Node Type | Purpose |
|-----------|---------|
| **Dataset** | Select a dataset to use |
| **Train/Test Split** | Split data into training and testing sets |
| **Preprocessing** | Clean and transform data |
| **Model** | Select and configure an ML algorithm |
| **Evaluation** | Calculate performance metrics |
| **Visualization** | Generate plots and charts |

### Jobs

When a workflow is executed, it becomes a **job**. Jobs run in the background and have a lifecycle:

1. **Pending** - Job is created, waiting to start
2. **Queued** - Job is in the queue, waiting for a worker
3. **Running** - Job is being executed
4. **Completed** - Job finished successfully
5. **Failed** - Job encountered an error

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- Redis (or use Docker)

### Quick Start

1. **Start infrastructure** (PostgreSQL, Redis, MinIO):
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Start the backend**:
   ```bash
   cd apps/api
   poetry install
   poetry run uvicorn app.main:app --reload
   ```

3. **Start the frontend**:
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Documentation Index

### Backend Documentation

| Document | Description |
|----------|-------------|
| [Backend Overview](./backend/README.md) | Backend architecture and structure |
| [API Routes](./backend/api-routes.md) | All API endpoints documented |
| [Authentication](./backend/auth.md) | OAuth, JWT, and session management |
| [Services](./backend/services.md) | Service layer documentation |
| [ML Pipeline](./backend/ml-pipeline.md) | Trainers, evaluators, preprocessors |
| [Jobs & Workflows](./backend/jobs-workflows.md) | Job execution and workflow system |
| [Database Models](./backend/database-models.md) | Database schema and relationships |

### Frontend Documentation

| Document | Description |
|----------|-------------|
| [Frontend Overview](./frontend/README.md) | Frontend architecture and structure |
| [Components](./frontend/components.md) | Component hierarchy and purpose |
| [Playground Canvas](./frontend/playground-canvas.md) | React Flow canvas system |
| [Stores](./frontend/stores.md) | Zustand state management |
| [Types](./frontend/types.md) | TypeScript type definitions |

### Integration Documentation

| Document | Description |
|----------|-------------|
| [Storage](./integrations/storage.md) | R2/MinIO integration |
| [Docker](./integrations/docker.md) | Docker configuration |
