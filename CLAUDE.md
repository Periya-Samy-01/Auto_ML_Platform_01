## Project Overview
You are working inside the "AutoML Platform 2.0" backend.
This project contains:
- FastAPI backend (apps/api)
- Celery worker system (apps/workers)
- SQLAlchemy database models (packages/database)
- ML training pipelines (apps/workers/worker/ml)

Goal:
Implement job execution using Celery + add job API endpoints.

## High-Level Architecture
- FastAPI handles authentication, datasets, jobs API.
- Celery workers run ML training jobs asynchronously.
- Redis is used as broker + backend.
- R2 (S3-compatible) is used for dataset & model storage.
- Each job:
  - Loads dataset → preprocess → train model → evaluate → save model → update DB.

## Coding Rules
- Use Python 3.11+
- Follow project folder structure strictly
- DO NOT rename directories or move modules
- Keep worker code idempotent and retry-safe
- Do not modify database schemas
- Use Pydantic v2 models

## What You Should Modify
- apps/workers/worker/celery_app.py
- apps/workers/worker/tasks/*
- apps/api/app/jobs/*
- tests under apps/api/tests

## What You Should NOT Modify
- packages/database/models/*
- auth system
- dataset upload logic
- .env files
- infra scripts

## Tools & Plugins
- Follow official anthropics/claude-code marketplace
- Use "Apply diff" for all file modifications
- Never remove imports unless asked

## Development Style
- Always propose changes as small diffs
- Keep functions small and modular
- Log every major step in workers

