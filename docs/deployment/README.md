# Deployment Documentation

This folder contains guides for deploying the AutoML Platform to production.

## Quick Start

1. **[Architecture Overview](./architecture.md)** - Understand how components connect
2. **[Frontend (Vercel)](./frontend-vercel.md)** - Deploy the Next.js app
3. **[Backend (Render)](./backend-render.md)** - Deploy the FastAPI server
4. **[ML Worker (HF Space)](./worker-hf-space.md)** - Deploy the ML execution worker

## Deployment Order

Deploy in this order to ensure all components can communicate:

```
1. Database (Supabase/Neon) → Get DATABASE_URL
2. HF Space Worker         → Get HF_SPACE_URL
3. Backend (Render)        → Get API URL
4. Frontend (Vercel)       → Configure with API URL
```

## Architecture Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────>│   Backend    │────>│  HF Space    │
│   (Vercel)   │     │   (Render)   │     │  (Worker)    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │  (Supabase)  │
                     └──────────────┘
```

## Environment Variables Summary

| Component | Required Variables |
|-----------|-------------------|
| Frontend | `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID` |
| Backend | `DATABASE_URL`, `HF_SPACE_URL`, `FRONTEND_URL`, `JWT_SECRET`, Google OAuth vars |
| HF Space | None (uses defaults) |
