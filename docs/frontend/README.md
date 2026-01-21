# Frontend Overview

> **Note**: This documentation reflects the current frontend structure. The architecture may evolve as the platform develops.

## What is the Frontend?

The frontend is a **Next.js 14 application** that provides the user interface for the AutoML Platform. It features:

- User authentication flow (OAuth login)
- Dashboard for managing datasets and jobs
- Visual workflow canvas for building ML pipelines
- Real-time job execution monitoring
- Responsive design for desktop and mobile

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| **Next.js 14** | React framework with App Router |
| **React 18** | UI component library |
| **TypeScript** | Type-safe JavaScript |
| **React Flow** | Visual node-based canvas |
| **Zustand** | Lightweight state management |
| **Shadcn/UI** | Component library (Radix-based) |
| **TailwindCSS** | Utility-first styling |
| **Axios** | HTTP client for API calls |

---

## Directory Structure

```
apps/web/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   ├── auth/              # Authentication pages
│   │   └── callback/      # OAuth callback handler
│   └── dashboard/         # Protected dashboard routes
│       ├── page.tsx       # Dashboard home
│       ├── datasets/      # Dataset management
│       ├── models/        # Model management
│       ├── playground/    # Workflow canvas
│       └── learn/         # Tutorials
├── components/            # React components
│   ├── ui/               # Base UI components (Shadcn)
│   ├── layout/           # Navigation, sidebar, navbar
│   ├── playground/       # Canvas and node components
│   ├── datasets/         # Dataset-related components
│   ├── jobs/             # Job monitoring components
│   ├── auth/             # Auth-related components
│   └── providers/        # React context providers
├── stores/               # Zustand state stores
│   ├── auth-store.ts     # Authentication state
│   ├── workflow-store.ts # Workflow canvas state
│   └── ...
├── lib/                  # Utilities and helpers
│   ├── api.ts           # API client
│   ├── workflowUtils.ts # Workflow utilities
│   └── ...
├── configs/              # Configuration files
│   └── algorithms/       # ML algorithm definitions
├── types/                # TypeScript type definitions
│   ├── auth.ts          # Auth types
│   ├── dataset.ts       # Dataset types
│   ├── workflow.ts      # Workflow types
│   └── ...
├── hooks/                # Custom React hooks
├── styles/               # Global styles
└── public/               # Static assets
```

---

## Key Features

### 1. Authentication

- OAuth login with Google and GitHub
- JWT token storage in localStorage
- Automatic token refresh
- Protected routes via middleware

### 2. Dashboard

- Overview of datasets, models, and jobs
- Quick actions for common tasks
- Credit balance display
- Recent activity feed

### 3. Dataset Management

- Upload datasets (CSV, Excel, JSON)
- View dataset previews and statistics
- Manage dataset versions
- Delete datasets

### 4. Workflow Playground

- Visual canvas for building ML pipelines
- Drag-and-drop node placement
- Node configuration via inspector panel
- Real-time validation
- Undo/redo support
- Workflow execution with live updates

### 5. Job Monitoring

- View running and past jobs
- Real-time progress updates
- Detailed logs and metrics
- Cancel or retry jobs

---

## Application Flow

### 1. User lands on app

```
/ (Landing Page)
├── Not authenticated → Show marketing page
├── Click "Login" → Redirect to /api/auth/google
└── OAuth callback → /auth/callback → Set tokens → /dashboard
```

### 2. User builds workflow

```
/dashboard/playground
├── Add nodes (Dataset, Preprocessing, Model, etc.)
├── Connect nodes with edges
├── Configure each node via inspector
├── Click Execute → Submit to API
└── WebSocket receives real-time updates
```

### 3. User views results

```
Job completes
├── Results panel shows metrics
├── Visualizations display
└── Model saved for future use
```

---

## Pages Overview

### Public Pages

| Route | Description |
|-------|-------------|
| `/` | Landing/marketing page |
| `/auth/callback` | OAuth callback handler |

### Protected Pages (Require Auth)

| Route | Description |
|-------|-------------|
| `/dashboard` | Main dashboard |
| `/dashboard/datasets` | Dataset management |
| `/dashboard/models` | Model management |
| `/dashboard/playground` | Workflow canvas |
| `/dashboard/learn` | Tutorials |

---

## How Routing Works

Next.js 14 uses the App Router with file-based routing:

- `app/page.tsx` → `/`
- `app/dashboard/page.tsx` → `/dashboard`
- `app/dashboard/datasets/page.tsx` → `/dashboard/datasets`

### Layouts

Layouts wrap pages and persist across navigation:

- `app/layout.tsx` - Root layout (providers, global styles)
- `app/dashboard/layout.tsx` - Dashboard layout (sidebar, navbar)

### Protection

Dashboard routes are protected by checking auth state on mount. Unauthenticated users are redirected to the login page.

---

## Development

### Running Locally

```bash
cd apps/web
npm install
npm run dev
```

Access: http://localhost:3000

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL |

### Build for Production

```bash
npm run build
npm start
```

---

## Documentation Index

| Document | Description |
|----------|-------------|
| [Components](./components.md) | Component hierarchy and organization |
| [Playground Canvas](./playground-canvas.md) | React Flow canvas system |
| [Stores](./stores.md) | Zustand state management |
| [Types](./types.md) | TypeScript type definitions |
