"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import {
  Database,
  FolderOpen,
  Sparkles,
  Plus,
  Search,
  LayoutGrid,
  List,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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

import {
  useDatasets,
  useDeleteDataset,
  useJobStatus,
  flattenDatasetPages,
  getDatasetTotal,
} from "@/hooks/use-datasets";
import { DatasetListParams, JobStatusResponse } from "@/types/dataset";
import { ViewToggle } from "@/components/datasets/view-toggle";
import { DatasetGrid } from "@/components/datasets/dataset-grid";
import { DatasetTable } from "@/components/datasets/dataset-table";
import { DatasetEmptyState } from "@/components/datasets/dataset-empty-state";
import { UploadModal } from "@/components/datasets/upload-modal";
import { SampleDatasetGrid } from "@/components/datasets/sample-dataset-grid";

type ViewMode = "grid" | "table";
type DatasetSection = "overview" | "my-datasets" | "sample-datasets";

// Component to poll job status
function JobStatusPoller({
  jobId,
  datasetId,
  onStatusUpdate,
  onComplete,
}: {
  jobId: string;
  datasetId: string;
  onStatusUpdate: (datasetId: string, status: JobStatusResponse) => void;
  onComplete: (datasetId: string) => void;
}) {
  useJobStatus(jobId, {
    onStatusUpdate: (status) => onStatusUpdate(datasetId, status),
    onComplete: () => onComplete(datasetId),
  });
  return null;
}

export default function DatasetsPage() {
  const [section, setSection] = useState<DatasetSection>("overview");
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [datasetToDelete, setDatasetToDelete] = useState<string | null>(null);

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [problemTypeFilter, setProblemTypeFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<DatasetListParams["sort_by"]>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Track processing jobs: Map<datasetId, jobId>
  const [processingJobs, setProcessingJobs] = useState<Map<string, string>>(
    new Map()
  );
  // Track job statuses for UI updates
  const [jobStatuses, setJobStatuses] = useState<
    Record<string, JobStatusResponse>
  >({});

  // Build query params - only for my-datasets section
  const queryParams: DatasetListParams = {
    search: searchQuery || undefined,
    problem_type:
      problemTypeFilter !== "all"
        ? (problemTypeFilter as DatasetListParams["problem_type"])
        : undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    is_sample: false,  // Always false since sample datasets use static catalog
  };

  const {
    data,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useDatasets(queryParams);

  const deleteDatasetMutation = useDeleteDataset();

  // Flatten pages for display
  const datasets = data ? flattenDatasetPages(data) : [];
  const totalCount = data ? getDatasetTotal(data) : 0;

  // Infinite scroll observer
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (isFetchingNextPage) return;
      if (observerRef.current) observerRef.current.disconnect();

      observerRef.current = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && hasNextPage) {
            fetchNextPage();
          }
        },
        { threshold: 0.1 }
      );

      if (node) observerRef.current.observe(node);
    },
    [isFetchingNextPage, hasNextPage, fetchNextPage]
  );

  // Handle job status updates
  const handleJobStatusUpdate = useCallback(
    (datasetId: string, status: JobStatusResponse) => {
      setJobStatuses((prev) => ({ ...prev, [datasetId]: status }));
    },
    []
  );

  // Handle job completion
  const handleJobComplete = useCallback((datasetId: string) => {
    setProcessingJobs((prev) => {
      const next = new Map(prev);
      next.delete(datasetId);
      return next;
    });
    // Clear status after a delay
    setTimeout(() => {
      setJobStatuses((prev) => {
        const next = { ...prev };
        delete next[datasetId];
        return next;
      });
    }, 2000);
  }, []);

  // Handle upload success
  const handleUploadSuccess = useCallback(
    (datasetId: string, jobId: string) => {
      setProcessingJobs((prev) => new Map(prev).set(datasetId, jobId));
    },
    []
  );

  // Handle delete
  const handleDelete = (id: string) => {
    setDatasetToDelete(id);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!datasetToDelete) return;
    try {
      await deleteDatasetMutation.mutateAsync(datasetToDelete);
    } finally {
      setDeleteDialogOpen(false);
      setDatasetToDelete(null);
    }
  };

  // Overview section with cards
  if (section === "overview") {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Datasets</h2>
            <p className="text-muted-foreground mt-1">
              Manage your data for machine learning
            </p>
          </div>
          <Button onClick={() => setUploadModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add New
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* My Datasets Card */}
          <Card
            className="hover:border-primary/50 transition-colors cursor-pointer group"
            onClick={() => setSection("my-datasets")}
          >
            <CardHeader className="pb-3">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <FolderOpen className="w-6 h-6 text-blue-400" />
              </div>
              <CardTitle className="text-lg">My Datasets</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                View and manage your uploaded datasets
              </p>
            </CardContent>
          </Card>

          {/* Sample Datasets Card */}
          <Card
            className="hover:border-primary/50 transition-colors cursor-pointer group"
            onClick={() => setSection("sample-datasets")}
          >
            <CardHeader className="pb-3">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-purple-400" />
              </div>
              <CardTitle className="text-lg">Sample Datasets</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Explore pre-loaded datasets to learn with
              </p>
            </CardContent>
          </Card>
        </div>

        <UploadModal
          open={uploadModalOpen}
          onOpenChange={setUploadModalOpen}
          onSuccess={handleUploadSuccess}
        />
      </div>
    );
  }

  // Dataset list section (My Datasets or Sample Datasets)
  return (
    <div className="space-y-6">
      {/* Job status pollers */}
      {Array.from(processingJobs.entries()).map(([datasetId, jobId]) => (
        <JobStatusPoller
          key={datasetId}
          jobId={jobId}
          datasetId={datasetId}
          onStatusUpdate={handleJobStatusUpdate}
          onComplete={handleJobComplete}
        />
      ))}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => setSection("overview")}
            className="text-sm text-muted-foreground hover:text-foreground mb-1 flex items-center gap-1"
          >
            ← Back to Datasets
          </button>
          <h2 className="text-2xl font-semibold">
            {section === "my-datasets" ? "My Datasets" : "Sample Datasets"}
          </h2>
          <p className="text-muted-foreground mt-1">
            {section === "my-datasets"
              ? "Your uploaded datasets"
              : "Pre-loaded datasets to help you learn and experiment"}
          </p>
        </div>
        {section === "my-datasets" && (
          <Button onClick={() => setUploadModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Upload Dataset
          </Button>
        )}
      </div>

      {/* Sample Datasets Section - uses static catalog */}
      {section === "sample-datasets" && (
        <SampleDatasetGrid />
      )}

      {/* My Datasets Section - uses API */}
      {section === "my-datasets" && (
        <>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search datasets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            <Select value={problemTypeFilter} onValueChange={setProblemTypeFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Problem Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="classification">Classification</SelectItem>
                <SelectItem value="regression">Regression</SelectItem>
                <SelectItem value="clustering">Clustering</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={`${sortBy}-${sortOrder}`}
              onValueChange={(value) => {
                const [field, order] = value.split("-");
                setSortBy(field as DatasetListParams["sort_by"]);
                setSortOrder(order as "asc" | "desc");
              }}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at-desc">Newest First</SelectItem>
                <SelectItem value="created_at-asc">Oldest First</SelectItem>
                <SelectItem value="name-asc">Name (A-Z)</SelectItem>
                <SelectItem value="name-desc">Name (Z-A)</SelectItem>
                <SelectItem value="row_count-desc">Most Rows</SelectItem>
                <SelectItem value="row_count-asc">Least Rows</SelectItem>
              </SelectContent>
            </Select>

            <ViewToggle value={viewMode} onChange={setViewMode} />
          </div>

          {/* Content */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : datasets.length === 0 ? (
            <DatasetEmptyState onUpload={() => setUploadModalOpen(true)} />
          ) : viewMode === "grid" ? (
            <DatasetGrid
              datasets={datasets}
              jobStatuses={jobStatuses}
              onDelete={handleDelete}
              onView={(id) => window.location.href = `/dashboard/datasets/${id}`}
              hasNextPage={hasNextPage ?? false}
              fetchNextPage={fetchNextPage}
              isFetchingNextPage={isFetchingNextPage}
            />
          ) : (
            <DatasetTable
              datasets={datasets}
              jobStatuses={jobStatuses}
              onDelete={handleDelete}
              onView={(id) => window.location.href = `/dashboard/datasets/${id}`}
              sortBy={sortBy}
              sortOrder={sortOrder}
              onSort={(column) => {
                if (column === sortBy) {
                  setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                } else {
                  setSortBy(column);
                  setSortOrder("desc");
                }
              }}
              hasNextPage={hasNextPage ?? false}
              fetchNextPage={fetchNextPage}
              isFetchingNextPage={isFetchingNextPage}
            />
          )}
        </>
      )}

      {/* Upload Modal */}
      <UploadModal
        open={uploadModalOpen}
        onOpenChange={setUploadModalOpen}
        onSuccess={handleUploadSuccess}
      />

      {/* Delete Confirmation */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Dataset</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this dataset? This action cannot
              be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteDatasetMutation.isPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
