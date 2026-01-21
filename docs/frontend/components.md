# Components

> **Note**: This documentation reflects the current component structure. The components may evolve as the platform develops.

## Overview

The frontend uses a modular component architecture organized by feature area. Components are primarily built using React with TypeScript, styled with TailwindCSS, and leverage Shadcn/UI for base components.

---

## Component Organization

```
components/
├── ui/              # Base UI components (Shadcn)
├── layout/          # Navigation and layout components
├── playground/      # Workflow canvas components
├── datasets/        # Dataset management components
├── jobs/            # Job monitoring components
├── auth/            # Authentication components
└── providers/       # React context providers
```

---

## UI Components (Shadcn)

Base components from Shadcn/UI that provide consistent styling and accessibility.

| Component | Purpose |
|-----------|---------|
| **Button** | Clickable buttons with variants |
| **Card** | Container with header, content, footer |
| **Input** | Text input fields |
| **Select** | Dropdown selection |
| **Dialog** | Modal dialogs |
| **DropdownMenu** | Contextual dropdown menus |
| **Tabs** | Tabbed content navigation |
| **Table** | Data table display |
| **Slider** | Numeric range slider |
| **Switch** | Toggle switch |
| **Badge** | Status badges and labels |
| **Tooltip** | Hover tooltips |
| **Skeleton** | Loading placeholders |
| **ScrollArea** | Custom scrollable areas |
| **Separator** | Visual dividers |
| **Sheet** | Slide-out panels |
| **Popover** | Floating content panels |
| **AlertDialog** | Confirmation dialogs |
| **Avatar** | User profile images |
| **Progress** | Progress indicators |

These components are customized via `components/ui/*.tsx` files.

---

## Layout Components

Handle the overall application structure and navigation.

### app-sidebar.tsx

The main sidebar navigation for the dashboard.

**Features**:
- Collapsible sidebar
- Navigation links to dashboard sections
- User profile section
- Credit balance display
- Theme toggle

**Menu Structure**:
- Dashboard (home)
- Datasets
- Playground
- Models
- Learn
- Settings

### dashboard-layout.tsx

Wrapper layout for all dashboard pages.

**Includes**:
- Sidebar (collapsible)
- Main content area
- Mobile navigation

### dashboard-navbar.tsx

Top navigation bar in the dashboard.

**Features**:
- Page title
- Search (optional)
- Notifications
- User menu
- Mobile menu toggle

### mobile-sidebar.tsx

Slide-out sidebar for mobile devices.

**Features**:
- Triggered by hamburger menu
- Same navigation as desktop sidebar
- Dismissible overlay

### navbar.tsx

Public navbar for non-authenticated pages.

**Features**:
- Logo
- Navigation links
- Login/Signup buttons

---

## Playground Components

The visual workflow canvas and its supporting components.

### Canvas Components

| Component | File | Purpose |
|-----------|------|---------|
| **PlaygroundCanvas** | `canvas/playground-canvas.tsx` | Main React Flow canvas wrapper |
| **CanvasToolbar** | `canvas/canvas-toolbar.tsx` | Toolbar with add node, zoom, export |
| **CanvasBackground** | `canvas/canvas-background.tsx` | Grid/dot background for canvas |
| **ExecutionPanel** | `canvas/execution-panel.tsx` | Results and execution status |
| **ProgressModal** | `canvas/progress-modal.tsx` | Execution progress overlay |
| **MiniMap** | `canvas/minimap.tsx` | Mini navigation map |

### Node Components

Each node type has a visual component and an inspector:

| Node Type | Node Component | Inspector Component |
|-----------|----------------|---------------------|
| **Dataset** | `dataset-node.tsx` | `dataset-inspector.tsx` |
| **Preprocessing** | `preprocessing-node.tsx` | `preprocessing-inspector.tsx` |
| **Feature Engineering** | `feature-engineering-node.tsx` | `feature-engineering-inspector.tsx` |
| **Train/Test Split** | `train-test-split-node.tsx` | `train-test-split-inspector.tsx` |
| **Model** | `model-node.tsx` | `model-inspector.tsx` |
| **Evaluate** | `evaluate-node.tsx` | `evaluate-inspector.tsx` |
| **Visualize** | `visualize-node.tsx` | `visualize-inspector.tsx` |

### base-node.tsx

A wrapper component that provides consistent styling for all node types.

**Features**:
- Common node structure (header, body)
- Status indicators (idle, selected, running, completed, failed)
- Input/output handles
- Selection highlighting

### Inspector Components

Inspector panels appear when a node is selected and provide configuration UI.

**Common Features**:
- Node configuration form
- Validation feedback
- Help tooltips
- Dynamic fields based on node type

**Dataset Inspector**:
- Dataset selection dropdown
- Target column selection
- Problem type selection (classification/regression)

**Preprocessing Inspector**:
- Method selection
- Column selection
- Method-specific parameters

**Model Inspector**:
- Algorithm selection
- Hyperparameter configuration
- Main and advanced parameters
- Training options

**Evaluate Inspector**:
- Metric selection based on problem type
- Metrics from upstream model capabilities

**Visualize Inspector**:
- Plot type selection
- Plot-specific configuration

---

## Dataset Components

Components for dataset management in the dashboard.

| Component | Purpose |
|-----------|---------|
| **DatasetList** | Paginated table of user datasets |
| **DatasetCard** | Card view of a dataset |
| **DatasetUploader** | File upload component |
| **DatasetPreview** | Data preview table |
| **DatasetStats** | Column statistics display |
| **UploadProgress** | Upload and processing progress |
| **DeleteConfirmModal** | Confirmation before deletion |

---

## Job Components

Components for job monitoring and history.

| Component | Purpose |
|-----------|---------|
| **JobList** | List of user's jobs |
| **JobCard** | Summary card for a job |
| **JobDetail** | Detailed job view |
| **JobLogs** | Execution logs display |
| **JobProgress** | Real-time progress bar |
| **JobActions** | Cancel, retry buttons |

---

## Auth Components

Components for authentication flows.

| Component | Purpose |
|-----------|---------|
| **LoginButton** | OAuth login buttons (Google, GitHub) |
| **AuthCallback** | Handles OAuth redirect |
| **ProtectedRoute** | Wrapper to check authentication |

---

## Provider Components

React context providers that wrap the application.

| Provider | Purpose |
|----------|---------|
| **ThemeProvider** | Dark/light theme support |
| **ToastProvider** | Toast notification system |
| **QueryProvider** | React Query client |

---

## Component Patterns

### How Nodes Work

Each node follows this pattern:

1. **Node Component** (`*-node.tsx`):
   - Renders the visual representation on the canvas
   - Shows summary of configuration
   - Displays status indicator
   - Uses `BaseNode` as wrapper

2. **Inspector Component** (`*-inspector.tsx`):
   - Renders configuration form
   - Reads current config from node data
   - Updates node data on changes
   - Shows validation errors

3. **Registration** (`index.ts`):
   - Exported from nodes index
   - Registered with React Flow

### Example Node Flow

```
User clicks "Add Model Node"
    ↓
Model node added to canvas (default state)
    ↓
User selects Model node
    ↓
Inspector panel opens with ModelInspector
    ↓
User selects algorithm
    ↓
Inspector shows hyperparameter form
    ↓
User configures parameters
    ↓
Node data updated, node shows summary
    ↓
Node connected to upstream/downstream nodes
```

### Data Flow Between Components

1. **Canvas** manages nodes/edges via workflow store
2. **Nodes** read their config from `node.data`
3. **Inspectors** update `node.data` via store actions
4. **Store** persists changes and handles undo/redo

---

## Styling Approach

### TailwindCSS

All components use TailwindCSS utility classes:

```tsx
<div className="flex items-center gap-2 p-4 bg-background rounded-lg">
  <Button variant="primary">Click Me</Button>
</div>
```

### CSS Variables

Theme colors are defined as CSS variables:

- `--background`, `--foreground`
- `--primary`, `--primary-foreground`
- `--accent`, `--accent-foreground`
- `--muted`, `--muted-foreground`
- `--border`, `--ring`

### Dark Mode

Supported via TailwindCSS's `dark:` variant:

```tsx
<div className="bg-white dark:bg-slate-900">
```

---

## Component Best Practices

1. **Single Responsibility**: Each component does one thing well
2. **Props Over State**: Prefer props for configuration, use store for shared state
3. **TypeScript**: All components are typed
4. **Colocation**: Related files stay together (node + inspector)
5. **Reusability**: Extract common patterns to shared components
