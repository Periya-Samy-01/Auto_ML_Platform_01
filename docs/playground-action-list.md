# Playground Plugin System — Action List

> Detailed breakdown of what needs to be done/modified to implement the plugin-based playground system.

---

## Current State Summary

### Backend — What Exists

| Component | Location | Status |
|-----------|----------|--------|
| Trainers (11 models) | `apps/api/app/ml/trainers/` | ✅ Exist, need plugin wrapper |
| Evaluators (3 types) | `apps/api/app/ml/evaluators/` | ✅ Exist, need consolidation |
| Preprocessors (8 methods) | `apps/api/app/ml/preprocessors/` | ✅ Exist, need registry |
| Workflows module | `apps/api/app/workflows/` | ⚠️ Empty (only `__init__.py`) |
| Worker | `apps/api/app/worker.py` | ✅ Exists (ARQ-based) |

### Frontend — What Exists

| Component | Location | Status |
|-----------|----------|--------|
| Playground page | `apps/web/app/dashboard/playground/` | ✅ Exists |
| Node components | `apps/web/components/playground/nodes/` | ⚠️ Exist, need refactoring |
| Inspector components | `apps/web/components/playground/nodes/` | ⚠️ Exist, need refactoring |
| Algorithm configs | `apps/web/configs/algorithms/` | ⚠️ Only Logistic Regression defined |
| Workflow store | `apps/web/stores/` | ✅ Exists |

---

## Backend Actions

### 1. Create Plugin Registry System

**Location:** `apps/api/app/plugins/`

**What to create:**

| File | Purpose |
|------|---------|
| `__init__.py` | Exports registry and utilities |
| `registry.py` | Plugin discovery, registration, and retrieval |
| `base.py` | `BaseModelPlugin` abstract class defining the plugin interface |

**BaseModelPlugin interface should define:**
- `slug` — Unique identifier (e.g., "random_forest")
- `name` — Display name (e.g., "Random Forest")
- `description` — Short description
- `icon` — Emoji or icon identifier
- `problem_types` — List of supported types: classification, regression, clustering
- `category` — Algorithm category: tree, ensemble, linear, neural, clustering
- `get_hyperparameters()` — Returns schema for main + advanced hyperparameters
- `get_default_hyperparameters()` — Returns default values
- `get_supported_metrics()` — Returns list of metric keys
- `get_default_metrics()` — Returns default metric keys
- `get_supported_plots()` — Returns list of plot keys
- `get_default_plots()` — Returns default plot keys
- `train(X_train, y_train, hyperparameters)` — Train and return model
- `predict(model, X)` — Make predictions

**Registry should provide:**
- `discover_plugins()` — Scan plugins directory and register all plugins
- `get_plugin(slug)` — Get plugin by slug
- `get_all_plugins()` — Get list of all plugins
- `get_plugins_by_problem_type(problem_type)` — Filter by problem type

---

### 2. Convert Existing Trainers to Plugins

**Location:** `apps/api/app/plugins/models/`

**What to create:**

| File | Wraps |
|------|-------|
| `random_forest.py` | `ml/trainers/random_forest.py` |
| `xgboost.py` | `ml/trainers/xgboost.py` |
| `decision_tree.py` | `ml/trainers/decision_tree.py` |
| `logistic_regression.py` | `ml/trainers/logistic_regression.py` |
| `linear_regression.py` | `ml/trainers/linear_regression.py` |
| `knn.py` | `ml/trainers/knn.py` |
| `naive_bayes.py` | `ml/trainers/naive_bayes.py` |
| `neural_network.py` | `ml/trainers/neural_network.py` |
| `svm.py` | New (not currently in trainers) |

**Each plugin file should:**
- Extend `BaseModelPlugin`
- Define metadata (slug, name, description, icon, problem_types, category)
- Define hyperparameter schema with field types, defaults, ranges
- Declare supported metrics and plots from shared library
- Implement `train()` using existing trainer logic

---

### 3. Create Preprocessing Registry

**Location:** `apps/api/app/plugins/preprocessing/`

**What to create:**

| File | Purpose |
|------|---------|
| `__init__.py` | Exports |
| `registry.py` | Preprocessing method discovery and registration |
| `base.py` | `BasePreprocessor` abstract class |

**What to wrap from existing preprocessors:**

| Method | Source |
|--------|--------|
| Fill Missing (mean/median/mode/constant) | `ml/preprocessors/missing_value_imputation.py` |
| Standard Scaler | `ml/preprocessors/feature_scaling.py` |
| MinMax Scaler | `ml/preprocessors/feature_scaling.py` |
| Robust Scaler | `ml/preprocessors/feature_scaling.py` |
| OneHot Encoder | `ml/preprocessors/one_hot_encoding.py` |
| Label Encoder | `ml/preprocessors/ordinal_label_encoding.py` |
| Remove Outliers (IQR) | `ml/preprocessors/outlier_handling.py` |
| Remove Outliers (Z-score) | `ml/preprocessors/outlier_handling.py` |
| Remove Duplicates | `ml/preprocessors/duplicate_removal.py` |

**Registry should provide:**
- `get_all_methods()` — List all preprocessing methods
- `get_method(slug)` — Get method by slug
- `get_methods_by_category(category)` — Filter by category

---

### 4. Create Shared Evaluators Library

**Location:** `apps/api/app/plugins/shared/evaluators.py`

**What to consolidate:**

Extract metrics from existing evaluators and define in one place:

**Classification Metrics:**
| Key | Name | Formula | Higher is Better |
|-----|------|---------|------------------|
| `accuracy` | Accuracy | (TP+TN)/(TP+TN+FP+FN) | Yes |
| `precision` | Precision | TP/(TP+FP) | Yes |
| `recall` | Recall | TP/(TP+FN) | Yes |
| `f1_score` | F1 Score | 2×(P×R)/(P+R) | Yes |
| `roc_auc` | ROC AUC | Area under ROC curve | Yes |
| `confusion_matrix` | Confusion Matrix | Matrix of TP/TN/FP/FN | N/A |
| `classification_report` | Classification Report | Per-class metrics | N/A |

**Regression Metrics:**
| Key | Name | Formula | Higher is Better |
|-----|------|---------|------------------|
| `mse` | Mean Squared Error | Σ(y-ŷ)²/n | No |
| `rmse` | Root Mean Squared Error | √MSE | No |
| `mae` | Mean Absolute Error | Σ|y-ŷ|/n | No |
| `r2_score` | R² Score | 1 - SS_res/SS_tot | Yes |
| `mape` | Mean Absolute % Error | Σ|(y-ŷ)/y|/n | No |

**Each metric should have:**
- `key` — Unique identifier
- `name` — Display name
- `formula` — Formula string (optional)
- `tooltip` — Description
- `higher_is_better` — Boolean
- `compute(y_true, y_pred, **kwargs)` — Compute function

---

### 5. Create Shared Visualizers Library

**Location:** `apps/api/app/plugins/shared/visualizers.py`

**What to create:**

| Key | Name | Applies To | Cost |
|-----|------|------------|------|
| `confusion_matrix` | Confusion Matrix | Classification | 1 |
| `roc_curve` | ROC Curve | Binary Classification | 1 |
| `precision_recall_curve` | Precision-Recall Curve | Binary Classification | 1 |
| `learning_curve` | Learning Curve | All | 2 |
| `feature_importance` | Feature Importance | Tree-based, Linear | 1 |
| `coefficient_plot` | Coefficient Plot | Linear | 1 |
| `residual_plot` | Residual Plot | Regression | 1 |
| `prediction_vs_actual` | Prediction vs Actual | Regression | 1 |
| `shap_summary` | SHAP Summary | All | 3 |
| `shap_waterfall` | SHAP Waterfall | All | 2 |
| `partial_dependence` | Partial Dependence | All | 2 |

**Each visualizer should have:**
- `key` — Unique identifier
- `name` — Display name
- `description` — What it shows
- `applies_to` — List of model categories
- `cost` — Credit cost
- `generate(model, X, y, **kwargs)` — Returns image path or bytes

---

### 6. Create Plugin API Endpoints

**Location:** `apps/api/app/plugins/router.py`

**Endpoints to create:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/plugins` | List all plugins (models + preprocessing) |
| GET | `/api/v1/plugins/models` | List model plugins, filter by `?problem_type=` |
| GET | `/api/v1/plugins/models/{slug}` | Get model plugin details |
| GET | `/api/v1/plugins/preprocessing` | List preprocessing methods |
| GET | `/api/v1/plugins/preprocessing/{slug}` | Get preprocessing method details |
| GET | `/api/v1/plugins/metrics` | List all available metrics |
| GET | `/api/v1/plugins/plots` | List all available plots |

**Register router in `main.py`**

---

### 7. Create Workflow Execution System

**Location:** `apps/api/app/workflows/`

**What to create:**

| File | Purpose |
|------|---------|
| `schemas.py` | Pydantic models for workflow request/response |
| `router.py` | API endpoints for workflow execution |
| `validator.py` | Validate workflow graph and node configs |
| `executor.py` | Execute workflow nodes in order |
| `models.py` | SQLAlchemy models for workflow storage (optional) |

**Schemas to define:**
- `NodeConfig` — Base node configuration
- `DatasetNodeConfig`, `PreprocessingNodeConfig`, `SplitNodeConfig`, `ModelNodeConfig`, `EvaluateNodeConfig`, `VisualizeNodeConfig`
- `EdgeConfig` — Source and target node IDs
- `WorkflowExecuteRequest` — Nodes + edges
- `WorkflowExecuteResponse` — Job ID, status

**Endpoints to create:**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/workflows/validate` | Validate workflow without executing |
| POST | `/api/v1/workflows/execute` | Queue workflow for execution |
| GET | `/api/v1/workflows/{job_id}/status` | Get execution status |
| WS | `/api/v1/workflows/{job_id}/stream` | WebSocket for real-time updates |

**Executor should:**
- Parse workflow graph
- Topologically sort nodes
- Execute each node in order
- Pass data between nodes
- Publish status updates via Redis pub/sub
- Store results in database and object storage

---

### 8. Modify Worker for Workflow Execution

**Location:** `apps/api/app/worker.py`

**What to add:**
- `execute_workflow` task function
- Integration with workflow executor
- Status publishing to Redis for WebSocket streaming

---

## Frontend Actions

### 9. Create Algorithm Plugin Configs

**Location:** `apps/web/configs/algorithms/`

**What to create:**

| File | Model |
|------|-------|
| `randomForest.ts` | Random Forest |
| `xgboost.ts` | XGBoost |
| `decisionTree.ts` | Decision Tree |
| `knn.ts` | K-Nearest Neighbors |
| `naiveBayes.ts` | Naive Bayes |
| `svm.ts` | Support Vector Machine |
| `linearRegression.ts` | Linear Regression |
| `neuralNetwork.ts` | Neural Network |

**Each config file should define:**
- `metadata` — slug, name, icon, description, category, problemTypes, bestFor
- `hyperparameters.main` — Always visible parameters
- `hyperparameters.advanced` — Collapsible parameters
- `evaluate.supportedMetrics` — List of metric keys
- `evaluate.defaultMetrics` — Default selected metrics
- `evaluate.metricDefinitions` — Metadata for each metric
- `visualize.supportedPlots` — List of plot keys
- `visualize.defaultPlots` — Default selected plots
- `visualize.plotDefinitions` — Metadata for each plot

**Update `index.ts`:**
- Import all configs
- Export `algorithmRegistry` object
- Export utility functions: `getAlgorithmConfig`, `getDefaultHyperparameters`

---

### 10. Refactor Inspector Field Components

**Location:** `apps/web/components/playground/inspectors/fields/`

**What to create:**

| File | Purpose |
|------|---------|
| `index.ts` | Exports |
| `SliderField.tsx` | Number input with slider |
| `SelectField.tsx` | Dropdown selection |
| `CheckboxField.tsx` | Boolean toggle |
| `NumberField.tsx` | Number input |
| `ToggleField.tsx` | Switch toggle |
| `RangeField.tsx` | Min-max range slider |
| `DynamicField.tsx` | Renders field based on schema type |

**DynamicField should:**
- Accept field schema and value
- Determine field type from schema
- Render appropriate field component
- Handle onChange callback

---

### 11. Refactor Node Components

**Location:** `apps/web/components/playground/nodes/`

**What to standardize:**

All nodes should:
- Use consistent BaseNode wrapper
- Show status indicator (not-configured, configured, running, completed, error)
- Show input/output handles based on node type
- Support delete action
- Display summary of configuration

**Node-specific updates:**

| Node | Updates Needed |
|------|----------------|
| DatasetNode | Add status indicator, standardize styling |
| PreprocessingNode | Add status indicator, show operation count |
| SplitNode | Add status indicator, show split ratio |
| ModelNode | Add status indicator, show algorithm name |
| EvaluateNode | Add status indicator, show metric count |
| VisualizeNode | Add status indicator, show plot count |

---

### 12. Refactor Inspector Components

**Location:** `apps/web/components/playground/nodes/`

**What to standardize:**

All inspectors should:
- Use consistent collapsible section style
- Use shared field components from `fields/`
- Handle "no input connected" empty state
- Show validation warnings

**Inspector-specific updates:**

| Inspector | Updates Needed |
|-----------|----------------|
| DatasetInspector | Connect to API for user datasets |
| PreprocessingInspector | Fetch methods from API |
| SplitInspector | Good as-is, minor styling |
| ModelInspector | Fetch algorithms from API, use DynamicField |
| EvaluateInspector | Read capabilities from upstream, filter metrics |
| VisualizeInspector | Read capabilities from upstream, filter plots |

---

### 13. Implement Capabilities Propagation

**Location:** `apps/web/lib/workflow/capabilities.ts`

**What to create:**
- Function to build capabilities from Model node config
- Function to propagate capabilities through edges
- Hook to get capabilities at any node

**How it works:**
1. When Model node algorithm changes → rebuild capabilities
2. Store capabilities in node data
3. Downstream nodes (Evaluate, Visualize) read capabilities from upstream edge
4. Filter options based on capabilities

---

### 14. Create API Hooks

**Location:** `apps/web/hooks/`

**What to create:**

| File | Purpose |
|------|---------|
| `usePlugins.ts` | Fetch and cache plugins from API |
| `useWorkflowExecution.ts` | Submit workflow, track execution status |

**usePlugins should provide:**
- `models` — List of model plugins
- `preprocessing` — List of preprocessing methods
- `getModelDetails(slug)` — Fetch full model config
- `isLoading`, `error` — Loading state

**useWorkflowExecution should provide:**
- `execute(workflow)` — Submit workflow
- `status` — Current execution status
- `nodeStatuses` — Status per node
- `results` — Results after completion
- `isExecuting` — Boolean

---

### 15. Create Execution UI

**Location:** `apps/web/components/playground/execution/`

**What to create:**

| File | Purpose |
|------|---------|
| `ExecutionButton.tsx` | Run button in toolbar |
| `ExecutionProgress.tsx` | Modal or panel showing execution progress |
| `NodeStatusOverlay.tsx` | Status indicators on nodes during execution |
| `ResultsPanel.tsx` | Display results after execution |

**ExecutionProgress should show:**
- Current executing node
- Progress through workflow
- Elapsed time
- Cancel button

**ResultsPanel should show:**
- Metrics table
- Visualization images
- Download options

---

### 16. Add Validation UI

**Location:** `apps/web/lib/workflow/validation.ts`

**What to create:**
- `validateWorkflow(nodes, edges)` — Check for errors
- Return list of errors with node IDs

**Validation rules:**
- Dataset node must have dataset selected
- Dataset node must have target column (for supervised)
- Model node must have algorithm selected
- All nodes must be connected
- No circular dependencies
- Evaluate must be after Model
- Visualize must be after Evaluate or Model

**UI representation:**
- Show errors in toolbar before execution
- Highlight error nodes with red border
- Show error message on hover

---

### 17. Update Workflow Store

**Location:** `apps/web/stores/workflowStore.ts`

**What to add:**
- `executionStatus` — 'idle' | 'running' | 'completed' | 'error'
- `nodeStatuses` — Map of node ID to status
- `executionResults` — Results after completion
- `setNodeStatus(nodeId, status)` — Update node status
- `setExecutionResults(results)` — Store results
- `resetExecution()` — Reset to idle

---

## Integration Actions

### 18. Connect Frontend to Plugin API

**What to modify:**

| File | Change |
|------|--------|
| `ModelInspector.tsx` | Fetch algorithms from API instead of hardcoded |
| `PreprocessingInspector.tsx` | Fetch methods from API |
| `EvaluateInspector.tsx` | Use capabilities from upstream |
| `VisualizeInspector.tsx` | Use capabilities from upstream |

---

### 19. Connect Execution Flow

**What to wire up:**

1. **Toolbar Run button** → calls `useWorkflowExecution.execute()`
2. **API returns job_id** → open WebSocket connection
3. **WebSocket messages** → update `workflowStore.nodeStatuses`
4. **Execution complete** → store results, show ResultsPanel

---

### 20. Final Polish

**What to add:**
- Loading states during API calls
- Error toasts for failed requests
- Cost estimate calculation in toolbar
- Keyboard shortcuts (Ctrl+Enter to run)
- Workflow save/load (optional, future)

---

## Priority Order

| Phase | Items | Effort |
|-------|-------|--------|
| **Phase 1** | 1, 2, 3, 4, 5, 6 | Backend plugin foundation |
| **Phase 2** | 9, 10, 11, 12 | Frontend component refactoring |
| **Phase 3** | 7, 8, 13, 14 | Execution system |
| **Phase 4** | 15, 16, 17, 18, 19, 20 | Integration and polish |
