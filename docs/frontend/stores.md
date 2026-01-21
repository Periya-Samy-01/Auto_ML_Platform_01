# State Management (Stores)

> **Note**: This documentation reflects the current state management implementation. The stores may evolve as the platform develops.

## Overview

The frontend uses **Zustand** for state management. Zustand is a lightweight state management library that provides:

- Simple API (no boilerplate)
- React hooks integration
- Middleware support (persist, devtools, undo)
- TypeScript friendly

---

## Store Files

```
stores/
├── auth-store.ts      # Authentication state
├── workflow-store.ts  # Workflow canvas state
└── (other stores)     # Additional as needed
```

---

## Auth Store

**File**: `stores/auth-store.ts`

Manages user authentication state across the application.

### State

| Field | Type | Description |
|-------|------|-------------|
| **user** | User \| null | Current user profile |
| **accessToken** | string \| null | JWT access token |
| **refreshToken** | string \| null | JWT refresh token |
| **isAuthenticated** | boolean | Whether user is logged in |
| **isLoading** | boolean | Auth operation in progress |
| **isInitialized** | boolean | Whether auth state has been loaded |

### Actions

| Action | Description |
|--------|-------------|
| **setTokens(access, refresh)** | Store tokens after login |
| **setUser(user)** | Store user profile |
| **setLoading(loading)** | Set loading state |
| **setInitialized(init)** | Mark auth as initialized |
| **logout()** | Clear auth state and tokens |
| **reset()** | Reset to initial state |
| **getAccessToken()** | Get token from state or localStorage |
| **getRefreshToken()** | Get refresh token |

### Persistence

The auth store persists to localStorage:
- Tokens stored separately for axios interceptor access
- User profile stored with Zustand persist middleware
- Rehydrated automatically on page load

### Token Storage

Tokens are stored in two places:
1. **Zustand state** - For React component access
2. **localStorage** - For axios interceptor access

This dual storage ensures the API client can always access tokens, even outside React components.

### Usage Example

```typescript
import { useAuthStore } from "@/stores/auth-store";

function Profile() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  return (
    <div>
      <p>Hello, {user?.full_name}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Utility Functions

For use outside React components:

```typescript
import { getStoredTokens, clearStoredTokens } from "@/stores/auth-store";

// In axios interceptor
const { accessToken } = getStoredTokens();
```

---

## Workflow Store

**File**: `stores/workflow-store.ts`

Manages the workflow canvas state including nodes, edges, and execution.

### State Types

**Persistent State** (saved to localStorage, tracked for undo):

| Field | Type | Description |
|-------|------|-------------|
| **nodes** | Node[] | All nodes on the canvas |
| **edges** | Edge[] | All connections between nodes |
| **workflowName** | string | Name of the workflow |

**Transient State** (not persisted):

| Field | Type | Description |
|-------|------|-------------|
| **selectedNodeId** | string \| null | Currently selected node |
| **inspectorVisible** | boolean | Is inspector panel open |
| **inspectorMinimized** | boolean | Is inspector minimized |
| **inspectorPosition** | {x, y} | Inspector panel position |
| **executionStatus** | ExecutionStatus | idle, running, completed, failed |
| **executionJobId** | string \| null | Current job ID |
| **nodeExecutionStatuses** | Record | Status per node during execution |
| **executionResults** | WorkflowResults \| null | Results after completion |
| **executionError** | string \| null | Error if execution failed |
| **showResultsPanel** | boolean | Is results panel visible |
| **showProgressModal** | boolean | Is progress modal visible |

### Actions

**React Flow Handlers**:

| Action | Description |
|--------|-------------|
| **onNodesChange(changes)** | Handle node changes (position, etc.) |
| **onEdgesChange(changes)** | Handle edge changes |
| **onConnect(connection)** | Handle new connection between nodes |

**Node Actions**:

| Action | Description |
|--------|-------------|
| **setNodes(nodes)** | Replace all nodes |
| **addNode(node)** | Add a new node |
| **deleteNode(id)** | Delete a node by ID |
| **updateNode(id, data)** | Update node properties |
| **updateNodeData(id, data)** | Update node.data specifically |

**Edge Actions**:

| Action | Description |
|--------|-------------|
| **setEdges(edges)** | Replace all edges |
| **addEdge(edge)** | Add a new edge |
| **deleteEdge(id)** | Delete an edge by ID |

**Selection Actions**:

| Action | Description |
|--------|-------------|
| **selectNode(id)** | Select a node (opens inspector) |
| **deselectNode()** | Clear selection (closes inspector) |

**Inspector Actions**:

| Action | Description |
|--------|-------------|
| **toggleInspector()** | Toggle inspector visibility |
| **setInspectorVisible(visible)** | Set inspector visibility |
| **setInspectorMinimized(min)** | Set minimized state |
| **setInspectorPosition(pos)** | Set inspector position |

**Workflow Actions**:

| Action | Description |
|--------|-------------|
| **setWorkflowName(name)** | Set workflow name |
| **clearWorkflow()** | Remove all nodes and edges |
| **loadWorkflow(nodes, edges, name)** | Load a saved workflow |

**Execution Actions**:

| Action | Description |
|--------|-------------|
| **updateNodeExecutionStatus(id, status)** | Update single node status |
| **resetExecution()** | Reset all execution state |
| **startExecution(jobId)** | Begin execution tracking |
| **completeExecution(results)** | Handle successful completion |
| **failExecution(error)** | Handle execution failure |

**Computed/Getters**:

| Getter | Description |
|--------|-------------|
| **getSelectedNode()** | Get currently selected node object |
| **isExecuting()** | Check if workflow is running |

### Middleware

**Persist Middleware**:
- Saves persistent state to localStorage
- Key: "automl-workflow"
- Rehydrates on page load

**Zundo Temporal Middleware**:
- Enables undo/redo functionality
- Tracks changes to persistent state only
- Configurable history limit

### Connection Validation

When `onConnect` is called, the store validates:

1. **Type compatibility**: Can source type connect to target type?
2. **Single input**: Does target already have an input?
3. **No cycles**: Would this create a loop?

If validation fails, the connection is rejected.

### Usage Example

```typescript
import { useWorkflowStore } from "@/stores/workflow-store";

function AddNodeButton() {
  const addNode = useWorkflowStore((state) => state.addNode);

  const handleClick = () => {
    addNode({
      id: `node-${Date.now()}`,
      type: "model",
      position: { x: 100, y: 100 },
      data: { label: "New Model" },
    });
  };

  return <button onClick={handleClick}>Add Model</button>;
}
```

### Using Selectors

For performance, use selectors to access specific state:

```typescript
// Good - only re-renders when nodes change
const nodes = useWorkflowStore((state) => state.nodes);

// Avoid - re-renders on any store change
const store = useWorkflowStore();
```

---

## Store Patterns

### Creating a Store

```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface MyState {
  count: number;
  increment: () => void;
}

export const useMyStore = create<MyState>()(
  persist(
    (set) => ({
      count: 0,
      increment: () => set((state) => ({ count: state.count + 1 })),
    }),
    { name: "my-store" }
  )
);
```

### Accessing State in Components

```typescript
// Single value
const count = useMyStore((state) => state.count);

// Multiple values
const { count, increment } = useMyStore((state) => ({
  count: state.count,
  increment: state.increment,
}));

// With shallow comparison for objects
import { shallow } from "zustand/shallow";
const { count, total } = useMyStore(
  (state) => ({ count: state.count, total: state.total }),
  shallow
);
```

### Accessing State Outside React

```typescript
// Get current state
const currentState = useMyStore.getState();

// Subscribe to changes
const unsubscribe = useMyStore.subscribe(
  (state) => console.log("State changed:", state)
);
```

---

## Benefits of Zustand

1. **Minimal Boilerplate**: No actions, reducers, or providers
2. **TypeScript Support**: Full type inference
3. **Performance**: Fine-grained subscriptions prevent unnecessary renders
4. **Flexibility**: Works inside and outside React
5. **Middleware**: Persistence, devtools, undo built-in
6. **Bundle Size**: Very small (~1KB)
