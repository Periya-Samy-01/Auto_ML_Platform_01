"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Plus,
  Inbox,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useDatasets, flattenDatasetPages } from "@/hooks/use-datasets";
import {
  SAMPLE_DATASETS,
  formatFileSize,
  formatRowCount,
  type SampleDataset,
} from "./sample-datasets";
import type { DatasetConfig } from "./dataset-node";
import type { Dataset } from "@/types";

interface DatasetInspectorProps {
  nodeId: string;
  config: DatasetConfig;
  onConfigChange: (config: Partial<DatasetConfig>) => void;
}

interface CollapsibleSectionProps {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

function CollapsibleSection({
  title,
  defaultOpen = false,
  children,
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-white/5 last:border-b-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 w-full px-4 py-3 text-left hover:bg-white/5 transition-colors"
      >
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-zinc-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-zinc-400" />
        )}
        <span className="text-[11px] uppercase tracking-wider text-zinc-400 font-medium">
          {title}
        </span>
      </button>
      <div
        className={cn(
          "overflow-hidden transition-all duration-200",
          isOpen ? "max-h-[600px] opacity-100" : "max-h-0 opacity-0"
        )}
      >
        <div className="px-4 pb-4">{children}</div>
      </div>
    </div>
  );
}

export function DatasetInspector({
  nodeId,
  config,
  onConfigChange,
}: DatasetInspectorProps) {
  const router = useRouter();
  const [selectedTab, setSelectedTab] = useState<"my-datasets" | "sample-data">(
    "sample-data"
  );
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch user datasets from API
  const {
    data: userDatasetsData,
    isLoading: isLoadingUserDatasets,
    error: userDatasetsError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useDatasets({ search: searchQuery || undefined });

  // Flatten paginated user datasets
  const userDatasets = useMemo(
    () => flattenDatasetPages(userDatasetsData),
    [userDatasetsData]
  );

  // All available problem types for user datasets
  const ALL_PROBLEM_TYPES = [
    { value: "classification" as const, label: "Classification", autoDetected: false },
    { value: "regression" as const, label: "Regression", autoDetected: false },
    { value: "clustering" as const, label: "Clustering", autoDetected: false },
  ];

  // Get selected dataset details (from either source)
  const selectedDataset = useMemo(() => {
    if (!config.datasetId) return null;

    // Check sample datasets first
    const sampleDataset = SAMPLE_DATASETS.find((d) => d.id === config.datasetId);
    if (sampleDataset) return sampleDataset;

    // Check user datasets
    const userDataset = userDatasets.find((d) => d.id === config.datasetId);
    if (userDataset) {
      // Convert columns_metadata to columnInfo format
      const columnInfo = (userDataset.columns_metadata || []).map((col) => ({
        name: col.name,
        type: mapDtypeToSimpleType(col.dtype),
        missingPercent: col.null_percentage || 0,
      }));

      // Mark the detected problem type as auto-detected
      const availableProblemTypes = ALL_PROBLEM_TYPES.map((pt) => ({
        ...pt,
        autoDetected: pt.value === userDataset.problem_type,
      }));

      return {
        id: userDataset.id,
        name: userDataset.name,
        rows: userDataset.row_count || 0,
        columns: userDataset.column_count || 0,
        size: userDataset.file_size_bytes || 0,
        isSample: false,
        defaultTarget: userDataset.target_column || null,
        availableProblemTypes,
        columnInfo,
        description: userDataset.description || "",
      } as SampleDataset;
    }

    return null;
  }, [config.datasetId, userDatasets]);

  // Helper function to map polars dtype to simple type
  function mapDtypeToSimpleType(dtype: string): "int" | "float" | "string" | "boolean" | "datetime" {
    const lowerDtype = dtype.toLowerCase();
    if (lowerDtype.includes("int") || lowerDtype.includes("uint")) return "int";
    if (lowerDtype.includes("float") || lowerDtype.includes("decimal")) return "float";
    if (lowerDtype.includes("bool")) return "boolean";
    if (lowerDtype.includes("date") || lowerDtype.includes("time")) return "datetime";
    return "string";
  }

  // Filter datasets based on search and tab
  const filteredDatasets = useMemo(() => {
    if (selectedTab === "sample-data") {
      if (!searchQuery) return SAMPLE_DATASETS;
      return SAMPLE_DATASETS.filter((d) =>
        d.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    // For "my-datasets", filtering is done server-side via the hook
    return [];
  }, [selectedTab, searchQuery]);

  // Handle user dataset selection
  const handleUserDatasetSelect = (dataset: Dataset) => {
    onConfigChange({
      datasetId: dataset.id,
      datasetName: dataset.name,
      isSample: false,
      targetColumn: dataset.target_column || null,
      problemType: dataset.problem_type || null,
      rows: dataset.row_count || 0,
      columns: dataset.column_count || 0,
      error: undefined,
    });
  };

  const handleDatasetSelect = (dataset: SampleDataset) => {
    onConfigChange({
      datasetId: dataset.id,
      datasetName: dataset.name,
      isSample: dataset.isSample,
      targetColumn: dataset.defaultTarget,
      problemType: dataset.availableProblemTypes[0]?.value || null,
      rows: dataset.rows,
      columns: dataset.columns,
      error: undefined,
    });
  };

  const handleTargetChange = (columnName: string) => {
    const newTarget = columnName === "none" ? null : columnName;
    onConfigChange({ targetColumn: newTarget });
  };

  const handleProblemTypeChange = (type: string) => {
    onConfigChange({
      problemType: type as "classification" | "regression" | "clustering",
    });
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto custom-scrollbar">
        {/* Section 1: Dataset Selection */}
        <CollapsibleSection title="Dataset Selection" defaultOpen={true}>
          {/* Tabs */}
          <div className="flex border-b border-white/10 mb-3">
            <button
              onClick={() => {
                setSelectedTab("my-datasets");
                setSearchQuery("");
              }}
              className={cn(
                "flex-1 py-2 text-sm font-medium transition-colors",
                selectedTab === "my-datasets"
                  ? "text-white border-b-2 border-blue-500"
                  : "text-zinc-500 hover:text-zinc-300"
              )}
            >
              My Datasets
            </button>
            <button
              onClick={() => {
                setSelectedTab("sample-data");
                setSearchQuery("");
              }}
              className={cn(
                "flex-1 py-2 text-sm font-medium transition-colors",
                selectedTab === "sample-data"
                  ? "text-white border-b-2 border-blue-500"
                  : "text-zinc-500 hover:text-zinc-300"
              )}
            >
              Sample Data
            </button>
          </div>

          {/* Upload Button (only for My Datasets tab) */}
          {selectedTab === "my-datasets" && (
            <button
              onClick={() => router.push("/dashboard/datasets")}
              className="w-full flex items-center gap-2 px-3 py-2 mb-3 text-sm text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Upload New Dataset
            </button>
          )}

          {/* Search Input */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              type="text"
              placeholder="Search datasets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-10 bg-zinc-800/50 border-zinc-700 text-white placeholder:text-zinc-500"
            />
          </div>

          {/* Dataset List */}
          <div className="max-h-[200px] overflow-y-auto custom-scrollbar space-y-1">
            {selectedTab === "sample-data" ? (
              // Sample datasets
              filteredDatasets.length > 0 ? (
                filteredDatasets.map((dataset) => (
                  <button
                    key={dataset.id}
                    onClick={() => handleDatasetSelect(dataset)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left",
                      config.datasetId === dataset.id
                        ? "bg-blue-500/10 border-l-2 border-blue-500"
                        : "hover:bg-white/5"
                    )}
                  >
                    {/* Radio circle */}
                    <div
                      className={cn(
                        "w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0",
                        config.datasetId === dataset.id
                          ? "border-blue-500"
                          : "border-zinc-600"
                      )}
                    >
                      {config.datasetId === dataset.id && (
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                      )}
                    </div>

                    {/* Dataset name */}
                    <span className="flex-1 text-sm text-white truncate">
                      {dataset.name}
                    </span>

                    {/* Row count */}
                    <span className="text-xs text-zinc-500">
                      {formatRowCount(dataset.rows)} rows
                    </span>
                  </button>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <Inbox className="w-12 h-12 text-zinc-600 mb-3" />
                  <p className="text-sm text-zinc-400">No datasets found</p>
                </div>
              )
            ) : (
              // User datasets from API
              isLoadingUserDatasets ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-3" />
                  <p className="text-sm text-zinc-400">Loading datasets...</p>
                </div>
              ) : userDatasetsError ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <AlertCircle className="w-12 h-12 text-red-500 mb-3" />
                  <p className="text-sm text-red-400">Failed to load datasets</p>
                  <p className="text-xs text-zinc-500 mt-1">
                    {userDatasetsError instanceof Error ? userDatasetsError.message : "Unknown error"}
                  </p>
                </div>
              ) : userDatasets.length > 0 ? (
                <>
                  {userDatasets.map((dataset) => (
                    <button
                      key={dataset.id}
                      onClick={() => handleUserDatasetSelect(dataset)}
                      className={cn(
                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left",
                        config.datasetId === dataset.id
                          ? "bg-blue-500/10 border-l-2 border-blue-500"
                          : "hover:bg-white/5"
                      )}
                    >
                      {/* Radio circle */}
                      <div
                        className={cn(
                          "w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0",
                          config.datasetId === dataset.id
                            ? "border-blue-500"
                            : "border-zinc-600"
                        )}
                      >
                        {config.datasetId === dataset.id && (
                          <div className="w-2 h-2 rounded-full bg-blue-500" />
                        )}
                      </div>

                      {/* Dataset info */}
                      <div className="flex-1 min-w-0">
                        <span className="text-sm text-white truncate block">
                          {dataset.name}
                        </span>
                        {dataset.problem_type && (
                          <span className="text-xs text-zinc-500 capitalize">
                            {dataset.problem_type}
                          </span>
                        )}
                      </div>

                      {/* Row count */}
                      <span className="text-xs text-zinc-500">
                        {dataset.row_count ? formatRowCount(dataset.row_count) : "—"} rows
                      </span>
                    </button>
                  ))}
                  {/* Load more button */}
                  {hasNextPage && (
                    <button
                      onClick={() => fetchNextPage()}
                      disabled={isFetchingNextPage}
                      className="w-full py-2 text-sm text-blue-400 hover:text-blue-300 disabled:opacity-50"
                    >
                      {isFetchingNextPage ? "Loading..." : "Load more"}
                    </button>
                  )}
                </>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <Inbox className="w-12 h-12 text-zinc-600 mb-3" />
                  <p className="text-sm text-zinc-400">No datasets found</p>
                  <p className="text-xs text-zinc-500 mt-1">
                    Upload your first dataset to get started.
                  </p>
                </div>
              )
            )}
          </div>
        </CollapsibleSection>

        {/* Section 2: Dataset Preview (only when dataset selected) */}
        {selectedDataset && (
          <CollapsibleSection title="Dataset Preview" defaultOpen={true}>
            <div className="space-y-4">
              {/* Shape */}
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">📊</span>
                  <span className="text-[11px] uppercase tracking-wider text-zinc-500">
                    Shape
                  </span>
                </div>
                <p className="text-[15px] text-white font-semibold">
                  {selectedDataset.rows.toLocaleString()} rows ×{" "}
                  {selectedDataset.columns} columns
                </p>
              </div>

              {/* Size */}
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">📦</span>
                  <span className="text-[11px] uppercase tracking-wider text-zinc-500">
                    Size
                  </span>
                </div>
                <p className="text-[15px] text-white">
                  {formatFileSize(selectedDataset.size)}
                </p>
              </div>

              {/* Target Column */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm">🎯</span>
                  <span className="text-[11px] uppercase tracking-wider text-zinc-500">
                    Target Column
                  </span>
                </div>
                <Select
                  value={config.targetColumn || "none"}
                  onValueChange={handleTargetChange}
                >
                  <SelectTrigger className="h-10 bg-zinc-800/50 border-zinc-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-zinc-700">
                    <SelectItem value="none" className="text-zinc-400">
                      — None (Unsupervised) —
                    </SelectItem>
                    {selectedDataset.columnInfo.map((col) => (
                      <SelectItem key={col.name} value={col.name}>
                        {col.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Problem Type */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm">🔖</span>
                  <span className="text-[11px] uppercase tracking-wider text-zinc-500">
                    Problem Type
                  </span>
                </div>
                <Select
                  value={config.problemType || ""}
                  onValueChange={handleProblemTypeChange}
                >
                  <SelectTrigger className="h-10 bg-zinc-800/50 border-zinc-700 text-white">
                    <SelectValue placeholder="Select problem type" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-zinc-700">
                    {selectedDataset.availableProblemTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                        {type.autoDetected && " ✓"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CollapsibleSection>
        )}

        {/* Section 3: Status */}
        <CollapsibleSection title="Status" defaultOpen={false}>
          {config.error ? (
            <div className="flex items-start gap-3">
              <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-400">Error</p>
                <p className="text-xs text-zinc-400 mt-1">
                  {config.error.message}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                  onClick={() =>
                    onConfigChange({
                      datasetId: null,
                      datasetName: null,
                      error: undefined,
                    })
                  }
                >
                  Reselect Dataset
                </Button>
              </div>
            </div>
          ) : !config.datasetId ? (
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-400">
                  Not Configured
                </p>
                <p className="text-xs text-zinc-400 mt-1">
                  Please select a dataset to continue.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-emerald-400">
                  Ready to Use
                </p>
                <p className="text-xs text-zinc-400 mt-1">
                  This dataset is configured and ready to be used in your
                  workflow.
                </p>
              </div>
            </div>
          )}
        </CollapsibleSection>
    </div>
  );
}
