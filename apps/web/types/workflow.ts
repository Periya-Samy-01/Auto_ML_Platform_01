/**
 * Workflow Types
 * Matches backend workflow schemas
 */

export interface WorkflowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  graph_json: WorkflowGraph | null;
  thumbnail_url: string | null;
  last_modified: string | null;
  created_at: string;
}

export interface WorkflowSnapshot {
  id: string;
  workflow_id: string;
  user_id: string;
  graph_json: WorkflowGraph;
  snapshot_name: string | null;
  created_at: string;
}

export interface WorkflowCreateRequest {
  name: string;
  description?: string;
  graph_json?: WorkflowGraph;
}

export interface WorkflowUpdateRequest {
  name?: string;
  description?: string;
  graph_json?: WorkflowGraph;
}

export interface WorkflowListResponse {
  items: Workflow[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
