"use client";

import { useEffect, useState } from "react";
import { useReactTable, getCoreRowModel, ColumnDef } from "@tanstack/react-table";
import { api } from "@/lib/axios";
import { format } from "date-fns";
import { Inbox, Loader2, Trash2 } from "lucide-react";
import { DataGrid, DataGridContainer } from "@/components/ui/data-grid";
import { DataGridTable } from "@/components/ui/data-grid-table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

// Types for the API response
interface ModelBrief {
  id: string;
  name: string | null;
  modelType: string | null;
  datasetId: string | null;
  datasetName: string | null;
  jobId: string | null;
  metricsJson: Record<string, number> | null;
  createdAt: string;
}

interface ModelsResponse {
  items: ModelBrief[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Table row type with serial number
interface WorkflowRow extends ModelBrief {
  sno: number;
}

// Delete button cell component
function DeleteCell({ 
  row, 
  onDeleteClick 
}: { 
  row: WorkflowRow; 
  onDeleteClick: (row: WorkflowRow) => void;
}) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
      onClick={(e) => {
        e.stopPropagation();
        onDeleteClick(row);
      }}
    >
      <Trash2 className="h-4 w-4" />
    </Button>
  );
}

export function WorkflowsTable() {
  const [data, setData] = useState<WorkflowRow[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workflowToDelete, setWorkflowToDelete] = useState<WorkflowRow | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchModels = async () => {
    try {
      setIsLoading(true);
      const response = await api.get<ModelsResponse>("/models", {
        params: { page: 1, page_size: 50 },
      });

      // Add serial numbers
      const rowsWithSno = response.data.items.map((item, index) => ({
        ...item,
        sno: index + 1,
      }));

      setData(rowsWithSno);
      setTotal(response.data.total);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch models:", err);
      setError("Failed to load workflows");
      setData([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleDeleteClick = (row: WorkflowRow) => {
    setWorkflowToDelete(row);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!workflowToDelete) return;

    try {
      setIsDeleting(true);
      await api.delete(`/models/${workflowToDelete.id}`);
      toast.success("Workflow deleted successfully");
      setDeleteDialogOpen(false);
      setWorkflowToDelete(null);
      // Refresh the table
      await fetchModels();
    } catch (err) {
      console.error("Failed to delete workflow:", err);
      toast.error("Failed to delete workflow");
    } finally {
      setIsDeleting(false);
    }
  };

  // Column definitions - need to be created inside the component to access handleDeleteClick
  const columns: ColumnDef<WorkflowRow>[] = [
    {
      accessorKey: "sno",
      header: "S.No",
      size: 70,
      cell: ({ row }) => (
        <span className="text-muted-foreground">{row.original.sno}</span>
      ),
    },
    {
      accessorKey: "name",
      header: "Workflow",
      size: 200,
      cell: ({ row }) => (
        <span className="font-medium text-foreground">
          {row.original.name || "Untitled Workflow"}
        </span>
      ),
    },
    {
      accessorKey: "modelType",
      header: "Model",
      size: 150,
      cell: ({ row }) => {
        const modelType = row.original.modelType;
        if (!modelType) return <span className="text-muted-foreground">—</span>;
        // Format model type (e.g., "decision_tree" -> "Decision Tree")
        const formatted = modelType
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");
        return <span className="text-foreground">{formatted}</span>;
      },
    },
    {
      accessorKey: "datasetName",
      header: "Dataset",
      size: 150,
      cell: ({ row }) => (
        <span className="text-foreground">
          {row.original.datasetName || "—"}
        </span>
      ),
    },
    {
      accessorKey: "createdAt",
      header: "Time Created",
      size: 180,
      cell: ({ row }) => (
        <span className="text-muted-foreground">
          {format(new Date(row.original.createdAt), "MMM dd, yyyy HH:mm")}
        </span>
      ),
    },
    {
      accessorKey: "accuracy",
      header: "Accuracy",
      size: 100,
      cell: ({ row }) => {
        const metrics = row.original.metricsJson;
        if (!metrics || metrics.accuracy === undefined) {
          return <span className="text-muted-foreground">—</span>;
        }
        const accuracy = (metrics.accuracy * 100).toFixed(2);
        return (
          <span className="font-medium text-primary">{accuracy}%</span>
        );
      },
    },
    {
      id: "actions",
      header: "",
      size: 60,
      cell: ({ row }) => (
        <DeleteCell row={row.original} onDeleteClick={handleDeleteClick} />
      ),
    },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // Empty state
  if (!isLoading && data.length === 0 && !error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <Inbox className="w-8 h-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">
          No Workflows Yet
        </h3>
        <p className="text-muted-foreground max-w-sm">
          You haven&apos;t run any workflows yet. Head to the Playground to create and
          run your first machine learning workflow.
        </p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <>
      <DataGrid
        table={table}
        recordCount={total}
        isLoading={isLoading}
        tableClassNames={{
          headerRow: "bg-cyan-900/30",
        }}
      >
        <DataGridContainer>
          <DataGridTable />
        </DataGridContainer>
      </DataGrid>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Workflow</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{workflowToDelete?.name || "Untitled Workflow"}&quot;? 
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
