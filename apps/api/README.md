# AutoML Platform API

FastAPI backend for the AutoML Platform.

## Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL (or Neon serverless)
- Redis

## Setup

### 1. Install Dependencies

```bash
cd apps/api
poetry install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run Database Migrations

```bash
# Generate initial migration (if needed)
poetry run alembic revision --autogenerate -m "Initial schema"

# Apply migrations
poetry run alembic upgrade head
```

### 4. Start Development Server

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
apps/api/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   ├── env.py           # Alembic environment
│   └── script.py.mako   # Migration template
├── app/
│   ├── auth/            # Authentication module
│   ├── credits/         # Credits module
│   ├── datasets/        # Datasets module
│   ├── jobs/            # Jobs module
│   ├── models/          # Trained models module
│   ├── workflows/       # Workflows module
│   ├── core/            # Core utilities
│   │   ├── config.py    # Settings
│   │   ├── database.py  # DB session
│   │   └── routes.py    # Health checks
│   └── main.py          # App entry point
├── tests/               # Test suite
├── alembic.ini          # Alembic config
├── pyproject.toml       # Dependencies
└── .env.example         # Environment template
```

## API Documentation

When running in development mode:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_health.py -v
```

## Database Commands

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply all migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key | Required in production |
| `DEBUG` | Enable debug mode | `true` |
| `ENVIRONMENT` | Environment name | `development` |

See `.env.example` for all available options.
