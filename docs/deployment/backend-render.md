# Backend Deployment (Render)

## Prerequisites

- GitHub repository with the project
- Render account (free tier works)
- PostgreSQL database (Supabase, Neon, or Render's PostgreSQL)
- Google OAuth credentials
- HF Space URL (see [worker deployment](./worker-hf-space.md))

## Step-by-Step Deployment

### 1. Create Web Service on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `automl-api` (or your choice) |
| **Root Directory** | `apps/api` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

### 2. Set Environment Variables

In Render dashboard → **Environment** tab, add:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend (for CORS)
FRONTEND_URL=https://your-frontend.vercel.app

# HF Space Worker
HF_SPACE_URL=https://username-automl-worker.hf.space

# JWT Secret (generate a secure random string)
JWT_SECRET=your-secure-random-string-at-least-32-chars

# Python path (required for shared packages)
PYTHONPATH=/opt/render/project/src
```

### 3. Deploy

Click **"Create Web Service"** - Render will:
- Clone your repository
- Install Python dependencies
- Start the FastAPI server

### 4. Verify Deployment

1. Check Render logs for startup messages
2. Visit `https://your-api.onrender.com/docs` for Swagger UI
3. Test health endpoint: `GET /api/health`

## Database Migrations

### Using Alembic

```bash
# SSH into Render (paid tier) or run locally with DATABASE_URL set
alembic upgrade head
```

### Manual Setup

If migrations haven't run, the tables won't exist. Check Render logs for database errors.

## Auto-Deployment

Render automatically deploys on every push to `main` branch.

## Known Limitations (Free Tier)

| Limitation | Impact |
|------------|--------|
| **15-min sleep** | First request after sleep takes ~30s |
| **512MB RAM** | Large datasets may fail |
| **60s timeout** | ML training handled by HF Space |

## Troubleshooting

### "Connection closed by server" (Redis)

- Redis is optional - app works without it
- Workflow status uses fallback to direct response

### Database Connection Errors

- Verify `DATABASE_URL` is correct
- Check database is accessible from Render
- Ensure SSL is enabled if required

### CORS Errors

- Add frontend URL to `FRONTEND_URL` env var
- Ensure URL has no trailing slash

### OAuth Redirect Fails

- Add Render URL to Google OAuth authorized origins
- Add callback: `https://your-api.onrender.com/api/auth/callback/google`
