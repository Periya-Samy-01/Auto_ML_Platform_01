# Playground Plugin System — Implementation Plan

> A comprehensive guide to the plugin-based architecture for the AutoML Playground workflow execution system.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Plugin System Architecture](#plugin-system-architecture)
4. [Node Types & Inspector Behavior](#node-types--inspector-behavior)
5. [Data Flow Through Nodes](#data-flow-through-nodes)
6. [Folder Structure](#folder-structure)
7. [API Contracts](#api-contracts)
8. [Workflow Execution Flow](#workflow-execution-flow)
9. [Implementation Phases](#implementation-phases)

---

## Overview

The Playground is a visual workflow builder where users construct ML pipelines by connecting nodes. Each node represents a step in the ML workflow:

```
Dataset → Preprocessing → Train/Test Split → Model → Evaluate → Visualize
```

The **Plugin System** enables:
- Backend-driven configuration (frontend displays what backend exposes)
- Model-specific evaluation metrics and visualizations
- Easy addition of new algorithms without frontend changes
- Separation of concerns between UI and ML logic

---

## Core Concepts

### 1. Nodes
Visual blocks on the canvas representing workflow steps. Each node has:
- **Type**: dataset, preprocessing, split, model, evaluate, visualize
- **Config**: User-selected options stored in node data
- **Status**: not-configured, configured, running, completed, error

### 2. Edges
Connections between nodes defining data flow. Each edge:
- Connects a source node's output to a target node's input
- Carries metadata about what data passes through
- Validates compatibility between connected nodes

### 3. Plugins
Self-contained modules that define an ML algorithm's complete behavior:
- Hyperparameter schema
- Training logic
- Supported evaluation metrics
- Supported visualizations

### 4. Capabilities
Metadata that flows downstream from Model node to Evaluate/Visualize nodes:
- Which metrics the selected algorithm supports
- Which visualizations are available
- Default selections for each

---

## Plugin System Architecture

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Backend Authority** | Backend plugins define all available options; frontend renders them dynamically |
| **Model-Centric** | Each model plugin declares its compatible metrics and visualizations |
| **Shared Utilities** | Common evaluation and visualization functions live in shared libraries |
| **Hot-Pluggable** | New plugins can be added without modifying core code |

### Plugin Responsibilities

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MODEL PLUGIN                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. METADATA                                                        │
│     ├── Name, slug, description, icon                               │
│     ├── Problem types: [classification, regression]                 │
│     └── Category: tree, linear, ensemble, neural                    │
│                                                                     │
│  2. HYPERPARAMETERS                                                 │
│     ├── Main parameters (always visible)                            │
│     ├── Advanced parameters (collapsible)                           │
│     └── Field types: int, float, select, bool, range                │
│                                                                     │
│  3. TRAINING                                                        │
│     ├── Model instantiation with hyperparameters                    │
│     ├── Fit on training data                                        │
│     └── Return trained model artifact                               │
│                                                                     │
│  4. EVALUATION (declares supported metrics)                         │
│     ├── Default metrics to select                                   │
│     ├── All supported metrics                                       │
│     └── References shared evaluator functions                       │
│                                                                     │
│  5. VISUALIZATION (declares supported plots)                        │
│     ├── Default plots to select                                     │
│     ├── All supported plots                                         │
│     └── References shared visualizer functions                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Shared Libraries

Plugins reference shared utilities rather than implementing their own:

**Evaluators (shared/evaluators.py)**
- `accuracy()`, `f1_score()`, `precision()`, `recall()`
- `roc_auc()`, `confusion_matrix()`, `classification_report()`
- `mse()`, `rmse()`, `mae()`, `r2_score()`

**Visualizers (shared/visualizers.py)**
- `plot_confusion_matrix()`, `plot_roc_curve()`
- `plot_feature_importance()`, `plot_learning_curve()`
- `plot_shap_summary()`, `plot_partial_dependence()`
- `plot_residuals()`, `plot_prediction_vs_actual()`

Each plugin declares WHICH of these it supports, and the shared library handles execution.

---

## Node Types & Inspector Behavior

### Dataset Node

**Purpose**: Select a dataset for the workflow

**Inspector Sections**:
| Section | Behavior |
|---------|----------|
| Dataset Selection | Tabs for "My Datasets" and "Sample Data". Search filter. Radio selection. Upload redirect button. |
| Dataset Preview | Overview: shape, size. Target column selector. Problem type selector. Columns tab: list with types and missing %. |
| Status | Shows configuration state with appropriate icon and message |

**Outputs**:
- Dataset ID
- Problem type (classification/regression/clustering)
- Target column
- Column metadata (names, types, missing percentages)

---

### Preprocessing Node

**Purpose**: Transform and clean data before training

**Inspector Sections**:
| Section | Behavior |
|---------|----------|
| Input Dataset | Shows connected upstream dataset info |
| Operations Pipeline | Orderable list of operations. Add via dropdown grouped by category. Each operation expands to show configuration. |
| Preview | Lists transformations in execution order |
| Warnings | Smart warnings for potential issues |

**Operation Categories**:
- **Missing Values**: Fill (mean, median, mode, constant), Drop rows/columns
- **Scaling**: StandardScaler, MinMaxScaler, RobustScaler
- **Encoding**: OneHotEncoder, LabelEncoder, TargetEncoder
- **Outliers**: IQR removal, Z-score removal, Clipping
- **Other**: Remove duplicates, Drop columns

**Outputs**:
- Ordered list of operations with their configurations
- Column transformations applied

---

### Train/Test Split Node

**Purpose**: Split data into training and testing sets

**Inspector Sections**:
| Section | Behavior |
|---------|----------|
| Input Dataset | Shows connected upstream info |
| Split Configuration | Slider (10-50%), preset buttons (80/20, 70/30, 90/10) |
| Options | Stratify (classification only), Shuffle, Random seed with regenerate |
| Preview | Visual bar, row counts, class distribution if stratified |
| Warnings | Small test set, imbalanced classes, shuffle disabled |

**Outputs**:
- Test size percentage
- Stratify flag
- Shuffle flag
- Random seed

---

### Model Node

**Purpose**: Select and configure an ML algorithm

**Inspector Sections**:
| Section | Behavior |
|---------|----------|
| Algorithm Selection | Radio list of available algorithms filtered by problem type. Shows icon, name, description, "best for" info. |
| Hyperparameters | Dynamic fields from plugin schema. Main + Advanced toggle. Validation warnings. |
| Training Settings | Cross-validation toggle with fold count. Optuna HPO toggle with trials and metric. |
| Cost Estimate | Estimated credits based on configuration |

**Key Behavior**:
- Algorithm list filtered by upstream problem type
- Hyperparameter fields rendered dynamically from plugin schema
- Generates `capabilities` object passed to downstream Evaluate/Visualize nodes

**Outputs**:
- Algorithm ID
- Hyperparameters
- Training settings (CV, Optuna)
- Capabilities (supported metrics + visualizations)

---

### Evaluate Node

**Purpose**: Select metrics to evaluate model performance

**Inspector Sections**:
| Section | Behavior |
|---------|----------|
| Connected Model | Shows upstream model info |
| Evaluation Metrics | Checkbox list from capabilities. Grouped: Recommended + Additional. Quick actions: Select Defaults/All/Clear. |
| Options | Confidence intervals toggle, Compare with baseline toggle |

**Key Behavior**:
- Only shows metrics declared by upstream Model plugin
- Groups metrics into "Recommended" (defaults) and "Additional"
- Each metric shows direction indicator (higher/lower is better)

**Outputs**:
- Selected metric keys
- Option flags

---

### Visualize Node

**Purpose**: Select visualizations to generate

**Inspector Sections**:
| Section | Behavior |
|---------|----------|
| Connected Model | Shows upstream model info |
| Visualizations | Checkbox list from capabilities. Grouped: Recommended / Performance / Explainability. Shows cost per plot. Quick actions. |
| Cost Summary | Total credits for selected visualizations |

**Key Behavior**:
- Only shows plots declared by upstream Model plugin
- Auto-populates defaults when Evaluate node selections change
- Each plot shows credit cost

**Outputs**:
- Selected plot keys
- Total visualization cost

---

## Data Flow Through Nodes

### Canvas-Time Data Flow (Configuration)

During canvas editing, data flows downstream to configure inspector options:

```
┌──────────┐     problemType      ┌──────────┐
│ Dataset  │ ──────────────────▶  │  Model   │  (filters available algorithms)
└──────────┘     targetColumn     └──────────┘
                                        │
                                        │ capabilities
                                        ▼
                              ┌──────────────────┐
                              │    Evaluate      │  (shows model-specific metrics)
                              └──────────────────┘
                                        │
                                        │ capabilities + selectedMetrics
                                        ▼
                              ┌──────────────────┐
                              │   Visualize      │  (shows model-specific plots)
                              └──────────────────┘
```

**Implementation**: When edges connect nodes, upstream config propagates to downstream nodes via:
1. Zustand store updates
2. React context or prop drilling
3. Edge metadata carrying capability info

### Execution-Time Data Flow (Runtime)

During workflow execution, actual data flows through the pipeline:

```
┌──────────┐     DataFrame        ┌──────────────┐     DataFrame
│ Dataset  │ ──────────────────▶  │ Preprocessing │ ──────────────▶
└──────────┘                      └──────────────┘
                                                          │
     ┌────────────────────────────────────────────────────┘
     │
     ▼
┌──────────┐   X_train, X_test    ┌──────────┐   trained_model
│  Split   │ ──────────────────▶  │  Model   │ ──────────────▶
└──────────┘   y_train, y_test    └──────────┘
                                        │
                                        │ model + test data
                                        ▼
                              ┌──────────────────┐   metrics_dict
                              │    Evaluate      │ ──────────────▶
                              └──────────────────┘
                                        │
                                        │ model + data + metrics
                                        ▼
                              ┌──────────────────┐   plot_artifacts
                              │   Visualize      │ ──────────────▶
                              └──────────────────┘
```

---

## Folder Structure

### Backend (apps/api)

```
apps/api/app/
├── plugins/
│   ├── __init__.py
│   ├── registry.py              # Plugin discovery and registration
│   ├── base.py                  # BaseModelPlugin abstract class
│   │
│   ├── models/                  # Model plugins
│   │   ├── __init__.py
│   │   ├── random_forest.py
│   │   ├── xgboost.py
│   │   ├── logistic_regression.py
│   │   ├── gradient_boosting.py
│   │   ├── decision_tree.py
│   │   ├── svm.py
│   │   ├── knn.py
│   │   └── linear_regression.py
│   │
│   └── shared/
│       ├── __init__.py
│       ├── evaluators.py        # All evaluation metric functions
│       ├── visualizers.py       # All visualization functions
│       └── constants.py         # Metric/plot definitions
│
├── preprocessing/
│   ├── __init__.py
│   ├── registry.py              # Preprocessing method registry
│   ├── base.py                  # BasePreprocessor abstract class
│   │
│   ├── methods/
│   │   ├── __init__.py
│   │   ├── missing.py           # FillMissing, DropMissing
│   │   ├── scaling.py           # StandardScaler, MinMaxScaler, RobustScaler
│   │   ├── encoding.py          # OneHotEncoder, LabelEncoder
│   │   ├── outliers.py          # IQROutlier, ZScoreOutlier
│   │   └── cleaning.py          # RemoveDuplicates, DropColumns
│   │
│   └── pipeline.py              # PreprocessingPipeline executor
│
├── workflows/
│   ├── __init__.py
│   ├── router.py                # Workflow API endpoints
│   ├── schemas.py               # Pydantic models for workflow config
│   ├── executor.py              # Workflow execution orchestrator
│   ├── validator.py             # Workflow validation logic
│   └── models.py                # SQLAlchemy models for workflow storage
│
└── ml/
    ├── __init__.py
    ├── trainers/                # Training logic (uses plugins)
    ├── evaluators/              # Evaluation execution
    └── visualizers/             # Visualization generation
```

### Frontend (apps/web)

```
apps/web/
├── app/
│   └── dashboard/
│       └── playground/
│           ├── layout.tsx
│           └── page.tsx         # Main playground canvas
│
├── components/
│   └── playground/
│       ├── index.ts             # Exports
│       │
│       ├── canvas/
│       │   ├── Canvas.tsx           # ReactFlow wrapper
│       │   ├── CanvasToolbar.tsx    # Top toolbar with node menu
│       │   ├── CanvasStatusBar.tsx  # Bottom status bar
│       │   └── CanvasMinimap.tsx    # Minimap component
│       │
│       ├── nodes/
│       │   ├── index.ts
│       │   ├── BaseNode.tsx         # Shared node wrapper
│       │   ├── DatasetNode.tsx
│       │   ├── PreprocessingNode.tsx
│       │   ├── SplitNode.tsx
│       │   ├── ModelNode.tsx
│       │   ├── EvaluateNode.tsx
│       │   └── VisualizeNode.tsx
│       │
│       ├── inspectors/
│       │   ├── index.ts
│       │   ├── InspectorPanel.tsx   # Right-side inspector container
│       │   ├── DatasetInspector.tsx
│       │   ├── PreprocessingInspector.tsx
│       │   ├── SplitInspector.tsx
│       │   ├── ModelInspector.tsx
│       │   ├── EvaluateInspector.tsx
│       │   ├── VisualizeInspector.tsx
│       │   │
│       │   └── fields/              # Reusable form field components
│       │       ├── index.ts
│       │       ├── SliderField.tsx
│       │       ├── SelectField.tsx
│       │       ├── CheckboxField.tsx
│       │       ├── NumberField.tsx
│       │       └── DynamicField.tsx # Renders field based on schema
│       │
│       └── execution/
│           ├── ExecutionPanel.tsx   # Execution progress UI
│           ├── ResultsPanel.tsx     # Display results after execution
│           └── NodeStatusOverlay.tsx # Status indicators on nodes
│
├── configs/
│   └── plugins/
│       ├── index.ts             # Plugin type definitions
│       └── types.ts             # TypeScript interfaces
│
├── hooks/
│   ├── useWorkflow.ts           # Workflow state management
│   ├── useNodeConfig.ts         # Node configuration helpers
│   ├── usePlugins.ts            # Fetch plugins from API
│   └── useExecution.ts          # Workflow execution hooks
│
├── stores/
│   └── workflowStore.ts         # Zustand store for workflow state
│
├── lib/
│   ├── api/
│   │   ├── plugins.ts           # Plugin API calls
│   │   └── workflows.ts         # Workflow API calls
│   │
│   └── workflow/
│       ├── validation.ts        # Client-side workflow validation
│       ├── serialization.ts     # Workflow to/from JSON
│       └── capabilities.ts      # Capabilities propagation logic
│
└── types/
    ├── workflow.ts              # Workflow, Node, Edge types
    ├── plugin.ts                # Plugin schema types
    └── execution.ts             # Execution status types
```

---

## API Contracts

### Get Available Plugins

```
GET /api/v1/plugins?problem_type=classification
```

Response:
```
{
  "models": [
    {
      "slug": "random_forest",
      "name": "Random Forest",
      "icon": "🌲",
      "description": "Ensemble of decision trees",
      "problem_types": ["classification", "regression"],
      "category": "ensemble"
    }
  ],
  "preprocessing": [
    {
      "slug": "fill_missing_mean",
      "name": "Fill Missing (Mean)",
      "category": "missing_values",
      "applies_to": ["numeric"]
    }
  ]
}
```

### Get Plugin Details

```
GET /api/v1/plugins/models/random_forest
```

Response:
```
{
  "slug": "random_forest",
  "name": "Random Forest",
  "hyperparameters": {
    "main": [
      { "key": "n_estimators", "type": "int", "default": 100, "min": 10, "max": 500 },
      { "key": "max_depth", "type": "int", "default": null, "min": 1, "max": 50, "nullable": true }
    ],
    "advanced": [
      { "key": "min_samples_split", "type": "int", "default": 2, "min": 2, "max": 20 }
    ]
  },
  "supported_metrics": ["accuracy", "f1_score", "precision", "recall", "roc_auc", "confusion_matrix"],
  "default_metrics": ["accuracy", "f1_score", "confusion_matrix"],
  "supported_plots": ["feature_importance", "confusion_matrix", "roc_curve", "learning_curve", "shap_summary"],
  "default_plots": ["feature_importance", "confusion_matrix"]
}
```

### Execute Workflow

```
POST /api/v1/workflows/execute
```

Request:
```
{
  "workflow_id": "uuid",
  "nodes": [
    { "id": "node-1", "type": "dataset", "config": { "dataset_id": "abc", "target_column": "label", "problem_type": "classification" } },
    { "id": "node-2", "type": "preprocessing", "config": { "operations": [...] } },
    { "id": "node-3", "type": "split", "config": { "test_size": 0.2, "stratify": true, "shuffle": true, "random_seed": 42 } },
    { "id": "node-4", "type": "model", "config": { "algorithm": "random_forest", "hyperparameters": {...}, "use_cv": true, "cv_folds": 5 } },
    { "id": "node-5", "type": "evaluate", "config": { "metrics": ["accuracy", "f1_score"] } },
    { "id": "node-6", "type": "visualize", "config": { "plots": ["confusion_matrix", "feature_importance"] } }
  ],
  "edges": [
    { "source": "node-1", "target": "node-2" },
    { "source": "node-2", "target": "node-3" },
    { "source": "node-3", "target": "node-4" },
    { "source": "node-4", "target": "node-5" },
    { "source": "node-5", "target": "node-6" }
  ]
}
```

Response:
```
{
  "job_id": "uuid",
  "status": "queued",
  "estimated_time": 120
}
```

### Get Execution Status (WebSocket)

```
WS /api/v1/workflows/execute/{job_id}/stream
```

Messages:
```
{ "node_id": "node-1", "status": "running" }
{ "node_id": "node-1", "status": "completed", "duration": 1.2 }
{ "node_id": "node-2", "status": "running" }
...
{ "type": "complete", "results": { "metrics": {...}, "artifacts": [...] } }
```

---

## Workflow Execution Flow

### Sequence Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Frontend │     │   API    │     │  Redis   │     │  Worker  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Execute        │                │                │
     │───────────────▶│                │                │
     │                │ Validate       │                │
     │                │ workflow       │                │
     │                │                │                │
     │                │ Queue job      │                │
     │                │───────────────▶│                │
     │                │                │                │
     │◀───────────────│                │                │
     │ job_id         │                │                │
     │                │                │ Pop job        │
     │                │                │◀───────────────│
     │                │                │                │
     │ Connect WS     │                │ Execute        │
     │───────────────▶│                │ Dataset        │
     │                │                │───────────────▶│
     │                │                │                │
     │◀───────────────│◀───────────────│◀───────────────│
     │ node-1 running │ Publish status │                │
     │                │                │                │
     │◀───────────────│◀───────────────│◀───────────────│
     │ node-1 done    │                │ Execute        │
     │                │                │ Preprocess     │
     │                │                │───────────────▶│
     │                │                │                │
     │    ...continues for each node...                │
     │                │                │                │
     │◀───────────────│◀───────────────│◀───────────────│
     │ complete       │                │ Store results  │
     │ + results      │                │ in DB + R2     │
     │                │                │                │
```

### Worker Execution Steps

1. **Load Dataset**: Fetch from storage, load into DataFrame
2. **Preprocess**: Apply operations in order using preprocessing registry
3. **Split**: Train/test split with configured options
4. **Train Model**: 
   - Instantiate plugin with hyperparameters
   - If CV: Run cross-validation
   - If Optuna: Run hyperparameter search
   - Train final model
5. **Evaluate**: Execute selected metrics from plugin's supported list
6. **Visualize**: Generate selected plots from plugin's supported list
7. **Store Results**: Save model artifact, metrics, and plot images to storage

---

## Implementation Phases

### Phase 1: Backend Plugin Foundation
- Create plugin base class and registry
- Implement 3-4 initial model plugins (Random Forest, Logistic Regression, XGBoost, Decision Tree)
- Create shared evaluators and visualizers
- Implement preprocessing registry and methods
- Create workflow execution endpoint

### Phase 2: Frontend Inspector Optimization
- Refactor node components to use consistent patterns
- Create reusable inspector field components
- Implement dynamic field rendering from plugin schemas
- Add capabilities propagation between nodes
- Implement workflow serialization/deserialization

### Phase 3: Execution Integration
- Connect frontend to execution API
- Implement WebSocket status updates
- Add execution progress UI on canvas
- Create results display panel

### Phase 4: Polish & Testing
- Add validation warnings and error handling
- Implement cost calculation
- Add execution history
- Write integration tests

---

## Summary

The plugin system provides a scalable, maintainable architecture where:

1. **Backend plugins** define complete algorithm behavior (hyperparameters, training, evaluation, visualization)
2. **Shared libraries** provide common evaluation and visualization functions
3. **Frontend** dynamically renders inspector panels based on plugin schemas
4. **Capabilities** flow downstream from Model to Evaluate/Visualize nodes
5. **Execution** happens asynchronously via workers with real-time status updates

This design allows adding new algorithms by simply creating a new plugin file—no changes needed to frontend code, evaluation logic, or visualization code.
