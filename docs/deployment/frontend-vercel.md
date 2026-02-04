# Frontend Deployment (Vercel)

## Prerequisites

- GitHub repository with the project
- Vercel account (free tier works)
- Google OAuth credentials

## Step-by-Step Deployment

### 1. Connect to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Select the repository containing your AutoML Platform

### 2. Configure Build Settings

| Setting | Value |
|---------|-------|
| **Framework Preset** | Next.js |
| **Root Directory** | `apps/web` |
| **Build Command** | `npm run build` (or leave default) |
| **Output Directory** | `.next` (default) |

### 3. Set Environment Variables

Add the following environment variables in Vercel dashboard:

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

### 4. Deploy

Click **"Deploy"** - Vercel will automatically:
- Install dependencies
- Build the Next.js application
- Deploy to their CDN

### 5. Configure Domain (Optional)

1. Go to **Settings → Domains**
2. Add your custom domain
3. Follow DNS configuration instructions

## Auto-Deployment

Once connected, Vercel automatically deploys on every push to `main` branch.

## Troubleshooting

### Build Fails

- Check that `apps/web` is set as root directory
- Ensure all dependencies are in `package.json`
- Check build logs for specific errors

### API Calls Fail

- Verify `NEXT_PUBLIC_API_URL` is correct
- Ensure backend is running and accessible
- Check browser console for CORS errors

### OAuth Redirect Fails

- Add Vercel domain to Google OAuth authorized origins
- Add callback URL: `https://your-app.vercel.app/auth/callback`
