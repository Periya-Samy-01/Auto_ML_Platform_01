# Playground Canvas

> **Note**: This documentation reflects the current canvas implementation. The system may evolve as the platform develops.

## Overview

The Playground Canvas is a visual interface for building machine learning workflows. Built on **React Flow**, it allows users to drag, connect, and configure nodes to create ML pipelines without writing code.

---

## How the Canvas Works

### Core Concept

The canvas represents an ML pipeline as a **directed acyclic graph (DAG)**:

- **Nodes** = Processing steps (dataset, preprocessing, model, etc.)
- **Edges** = Data flow connections between nodes
- **Execution** = Nodes run in topological order

### User Workflow

1. User opens the playground
2. Adds nodes from the toolbar
3. Connects nodes by dragging handles
4. Configures each node via the inspector
5. Clicks Execute to run the pipeline
6. Views real-time progress and results

---

## React Flow Integration

### What is React Flow?

React Flow is a library for building node-based interfaces. It provides:

- Drag-and-drop node positioning
- Edge connections between nodes
- Zoom and pan controls
- Selection and multi-select
- Minimap navigation

### How We Use It

The `PlaygroundCanvas` component wraps React Flow with:

1. Custom node types (our ML nodes)
2. Custom styling (dark theme, animations)
3. Integration with Zustand store
4. Custom connection validation
5. Toolbar and inspector overlays

---

## Node Types

The canvas supports these node types:

| Type | Purpose | Icon |
|------|---------|------|
| **dataset** | Load a dataset | Database |
| **preprocessing** | Apply preprocessing | Filter |
| **featureEngineering** | Feature transformations | Wand |
| **trainTestSplit** | Split data | SplitSquare |
| **model** | Train ML model | Brain |
| **evaluate** | Calculate metrics | ChartBar |
| **visualize** | Generate plots | PieChart |

Each node type has:
- A visual component (how it looks on canvas)
- An inspector component (configuration panel)
- A data schema (what it stores)

---

## Node Structure

### Visual Structure

```
┌─────────────────────────────────────┐
│  [Icon] Node Title        [Status]  │  ← Header
├─────────────────────────────────────┤
│                                     │
│  Summary of current configuration   │  ← Body
│                                     │
├─────────────────────────────────────┤
│  ○─────────────────────────────○    │  ← Handles
└─────────────────────────────────────┘
```

### Node Data Structure

Each node stores its configuration in `node.data`:

```typescript
{
  id: "node-1",
  type: "model",
  position: { x: 300, y: 200 },
  data: {
    label: "Random Forest",
    config: {
      algorithm: "randomForest",
      hyperparameters: {
        n_estimators: 100,
        max_depth: 10,
      },
    },
    capabilities: { /* from algorithm config */ },
    status: "idle",
  }
}
```

### Node Statuses

| Status | Color | Meaning |
|--------|-------|---------|
| **idle** | Gray | Not configured or not run |
| **configured** | Blue | Configured, ready to run |
| **running** | Yellow/Animated | Currently executing |
| **completed** | Green | Finished successfully |
| **failed** | Red | Encountered error |
| **skipped** | Gray | Skipped due to upstream failure |

---

## Edges (Connections)

### Connection Rules

Not all nodes can connect to all other nodes. Valid connections:

| Source Node | Valid Targets |
|-------------|---------------|
| Dataset | Preprocessing, Feature Engineering, Split, Model |
| Preprocessing | Preprocessing, Feature Engineering, Split, Model |
| Feature Engineering | Preprocessing, Split, Model |
| Train/Test Split | Model |
| Model | Evaluate, Visualize |
| Evaluate | (terminal) |
| Visualize | (terminal) |

### Connection Validation

When a user tries to connect nodes:

1. Check if source can connect to target type
2. Check if target already has an input (single input allowed)
3. Check for cycles (would create loop)
4. If valid, create edge; otherwise, reject

### Edge Styling

Edges use animated styling:
- Default: Blue animated line
- During execution: Highlight active paths
- Invalid: Red temporary line

---

## Inspector Panel

The inspector panel is a side panel that shows configuration for the selected node.

### How It Works

1. User clicks a node
2. Workflow store sets `selectedNodeId`
3. Inspector panel renders appropriate inspector component
4. User makes changes
5. Inspector calls `updateNodeData()` on store
6. Node re-renders with new data

### Inspector Position

The inspector can be:
- Docked to the right (default)
- Draggable/floating
- Minimized to just header
- Hidden completely

### Switching Inspectors

The inspector component is chosen based on node type:

```typescript
switch (node.type) {
  case "dataset":
    return <DatasetInspector />;
  case "model":
    return <ModelInspector />;
  // etc.
}
```

---

## Toolbar

The canvas toolbar provides quick actions:

| Action | Icon | Description |
|--------|------|-------------|
| **Add Node** | Plus | Dropdown to add node types |
| **Undo** | Undo | Undo last change |
| **Redo** | Redo | Redo undone change |
| **Zoom In** | Plus | Increase zoom |
| **Zoom Out** | Minus | Decrease zoom |
| **Fit View** | Maximize | Fit all nodes in view |
| **Execute** | Play | Run the workflow |
| **Save** | Save | Save workflow |
| **Export** | Download | Export as image/JSON |
| **Settings** | Gear | Canvas settings |

---

## Execution Flow

### Starting Execution

1. User clicks Execute button
2. Frontend validates workflow locally
3. Frontend sends workflow to `/api/workflows/execute`
4. API validates and creates job
5. API returns job ID
6. Frontend opens WebSocket to `/api/workflows/{job_id}/stream`

### During Execution

1. Worker executes nodes in order
2. Worker publishes status updates via Redis
3. API forwards updates via WebSocket
4. Frontend updates node statuses in real-time
5. Progress modal shows current state

### After Execution

1. Worker sends completion/failure message
2. Frontend updates final node statuses
3. Results panel displays metrics and plots
4. User can view details or start new execution

---

## Data Propagation

Data flows between nodes based on connections:

### Upstream Data Access

Nodes can read data from upstream nodes:

**Dataset Info**: Model node reads target column and problem type from upstream dataset.

**Model Capabilities**: Evaluate node reads supported metrics from upstream model.

### Utility Functions

`lib/workflowUtils.ts` provides helpers:

| Function | Purpose |
|----------|---------|
| `findUpstreamModelNode()` | Find connected model node |
| `getUpstreamCapabilities()` | Get model capabilities |
| `getUpstreamDatasetInfo()` | Get dataset configuration |
| `validateWorkflowUpstream()` | Validate required connections |
| `findDownstreamNodes()` | Find all nodes that receive data |

### Example: Evaluate Node

When an Evaluate node is selected:

1. Inspector calls `getUpstreamCapabilities()`
2. Gets supported metrics from upstream model
3. Displays only valid metrics for that model
4. User selects which metrics to calculate

---

## State Management

The canvas state is managed by the **Workflow Store** (Zustand).

### What's Stored

**Persistent State** (saved, undo/redo tracked):
- `nodes` - All nodes on canvas
- `edges` - All connections
- `workflowName` - Name of workflow

**Transient State** (not saved):
- `selectedNodeId` - Currently selected node
- `inspectorVisible` - Is inspector open
- `executionStatus` - Current execution state
- `nodeExecutionStatuses` - Status per node
- `executionResults` - Results after completion

### Undo/Redo

Powered by Zundo middleware:
- Every node/edge change is tracked
- User can undo with Ctrl+Z
- User can redo with Ctrl+Y
- History is limited to prevent memory issues

### Persistence

Workflow state is saved to localStorage:
- Automatically saved on changes
- Loaded on page refresh
- Prevents losing work

---

## Algorithm Configuration

### Where Algorithms Are Defined

Algorithm configurations live in `configs/algorithms/`:

```
configs/algorithms/
├── index.ts           # Registry and exports
├── types.ts           # Type definitions
├── logisticRegression.ts
├── randomForest.ts
├── xgboost.ts
├── kmeans.ts
└── ...
```

### Algorithm Config Structure

Each algorithm defines:

```typescript
{
  id: "randomForest",
  name: "Random Forest",
  description: "Ensemble of decision trees",
  icon: "tree",
  category: "ensemble",
  problemTypes: ["classification", "regression"],
  
  hyperparameters: {
    main: [
      {
        key: "n_estimators",
        name: "Number of Trees",
        type: "number",
        default: 100,
        min: 1,
        max: 1000,
        description: "Number of trees in the forest"
      },
      // ...
    ],
    advanced: [
      // Less common parameters
    ]
  },
  
  capabilities: {
    supportsMulticlass: true,
    supportsProbabilities: true,
    supportsFeatureImportance: true,
    supportedMetrics: ["accuracy", "precision", "recall", "f1", "roc_auc"],
    supportedPlots: ["confusion_matrix", "feature_importance", "roc_curve"]
  }
}
```

### How Configs Are Used

1. **Model Inspector**: Shows algorithm dropdown with all algorithms
2. **When selected**: Loads hyperparameter definitions
3. **Inspector renders**: Input fields for each hyperparameter
4. **Capabilities**: Passed to downstream nodes (Evaluate, Visualize)

---

## Files Summary

| File/Directory | Purpose |
|----------------|---------|
| `components/playground/canvas/` | Canvas wrapper and toolbar |
| `components/playground/nodes/` | Node and inspector components |
| `stores/workflow-store.ts` | Canvas state management |
| `lib/workflowUtils.ts` | Workflow graph utilities |
| `configs/algorithms/` | Algorithm definitions |
| `types/workflow.ts` | Workflow type definitions |
