"use client";

import { useWorkflowStore } from "@/stores";

export function CanvasStatusBar() {
  const { nodes, edges } = useWorkflowStore();

  return (
    <div className="absolute bottom-4 left-4 z-10">
      <div className="px-4 py-2 rounded-lg bg-card/90 backdrop-blur-sm border border-border">
        <span className="text-sm text-muted-foreground">
          Nodes: <span className="text-foreground font-medium">{nodes.length}</span>
          <span className="mx-2 text-border">|</span>
          Connections: <span className="text-foreground font-medium">{edges.length}</span>
        </span>
      </div>
    </div>
  );
}
