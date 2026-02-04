# AutoML Platform - Deployment Architecture

This document describes how the AutoML Platform components are connected and deployed in production.

## Overview

The AutoML Platform uses a **three-tier architecture** deployed across multiple cloud services:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                                     │
│                        Next.js Application                                   │
│                        https://your-app.vercel.app                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼ REST API calls
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (Render)                                     │
│                         FastAPI Application                                  │
│                         https://your-api.onrender.com                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                  ▼
┌──────────────────────────────┐    ┌────────────────────────────────────────┐
│   PostgreSQL Database        │    │       HF SPACE (ML Worker)              │
│   (Supabase/Neon)           │    │       Gradio Application                │
│                              │    │       https://user-worker.hf.space     │
└──────────────────────────────┘    └────────────────────────────────────────┘
```

## Components

### 1. Frontend (Vercel)

- **Technology**: Next.js 14+ with App Router
- **Purpose**: User interface for the AutoML platform
- **Key Features**:
  - React Flow canvas for workflow building
  - Dataset upload and management
  - Model training interface
  - Results visualization

### 2. Backend API (Render)

- **Technology**: FastAPI (Python)
- **Purpose**: REST API server handling authentication, data, and workflow orchestration
- **Key Responsibilities**:
  - User authentication (OAuth with Google)
  - Dataset management
  - Workflow validation
  - Orchestrating ML execution via HF Space
  - Storing model results in database

### 3. ML Worker (Hugging Face Space)

- **Technology**: Gradio + scikit-learn
- **Purpose**: Execute ML training workloads
- **Why HF Space?**: 
  - Render free tier has 60-second request timeout
  - HF Spaces allow longer execution times (5+ minutes)
  - Free GPU access available if needed

### 4. Database (PostgreSQL)

- **Options**: Supabase, Neon, or any PostgreSQL provider
- **Stores**: Users, datasets, trained models, metrics

## Request Flow

### Workflow Execution Flow

```
Frontend                 Backend                  HF Space
   │                        │                        │
   │ POST /workflows/execute│                        │
   │───────────────────────>│                        │
   │                        │                        │
   │                        │ Validate workflow      │
   │                        │◄───────────────────────│
   │                        │                        │
   │                        │ POST /call/predict     │
   │                        │───────────────────────>│
   │                        │                        │
   │                        │     Train model        │
   │                        │     (up to 60s+)       │
   │                        │                        │
   │                        │    Return results      │
   │                        │<───────────────────────│
   │                        │                        │
   │                        │ Save model to DB       │
   │                        │◄───────────────────────│
   │                        │                        │
   │  Return workflow results                        │
   │<───────────────────────│                        │
   │                        │                        │
```

## Environment Variables

### Frontend (Vercel)

```env
NEXT_PUBLIC_API_URL=https://your-api.onrender.com/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### Backend (Render)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# HF Space Worker
HF_SPACE_URL=https://username-automl-worker.hf.space

# Frontend URL (for CORS)
FRONTEND_URL=https://your-app.vercel.app

# JWT Secret
JWT_SECRET=your-secure-random-string
```

### HF Space

No environment variables required - uses Gradio defaults.

## Key Integration Points

### 1. Frontend ↔ Backend

- **Protocol**: HTTPS REST API
- **Authentication**: JWT tokens (stored in cookies)
- **CORS**: Backend must allow frontend origin

### 2. Backend ↔ HF Space

- **Protocol**: Gradio 4.x API (`/call/predict` endpoint)
- **Flow**:
  1. Backend POSTs workflow JSON to `/call/predict`
  2. HF Space returns `event_id`
  3. Backend polls `/call/predict/{event_id}` for results
  4. Results returned via Server-Sent Events (SSE)

### 3. Backend ↔ Database

- **Protocol**: PostgreSQL via SQLAlchemy
- **Connection**: Direct connection string

## Scaling Considerations

### Current Limitations (Free Tier)

| Component | Limitation |
|-----------|------------|
| Render | 512MB RAM, sleeps after 15min inactivity |
| HF Space | 2GB RAM, 2 CPU cores |
| Vercel | 100GB bandwidth/month |

### Scaling Options

1. **Paid Render**: Remove timeout, add more RAM
2. **Paid HF Space**: GPU access, persistent storage
3. **Self-hosted**: Deploy to AWS/GCP for full control

## Security Notes

1. **CORS**: Backend only accepts requests from frontend origin
2. **JWT**: Tokens have 7-day expiry, stored as httpOnly cookies
3. **OAuth**: Google OAuth handles authentication
4. **HTTPS**: All communication encrypted in transit
