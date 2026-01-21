"use client";

/**
 * Dataset Table
 * Table view of datasets with inline progress and infinite scroll
 */

import { useEffect, useRef } from "react";
import { formatDistanceToNow } from "date-fns";
import {
  Database,
  MoreVertical,
  Trash2,
  ExternalLink,
  Loader2,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { Dataset, JobStatusResponse, DatasetListParams } from "@/types";

interface DatasetTableProps {
  datasets: Dataset[];
  /** Job statuses keyed by dataset ID */
  jobStatuses: Record<string, JobStatusResponse | undefined>;
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
  sortBy?: DatasetListParams["sort_by"];
  sortOrder?: DatasetListParams["sort_order"];
  onSort: (column: DatasetListParams["sort_by"]) => void;
  onView: (id: string) => void;
  onDelete: (id: string) => void;
}

export function DatasetTable({
  datasets,
  jobStatuses,
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  sortBy = "created_at",
  sortOrder = "desc",
  onSort,
  onView,
  onDelete,
}: DatasetTableProps) {
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    const el = loadMoreRef.current;
    if (el) {
      observer.observe(el);
    }

    return () => {
      if (el) {
        observer.unobserve(el);
      }
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const SortIcon = ({ column }: { column: DatasetListParams["sort_by"] }) => {
    if (sortBy !== column) return null;
    return sortOrder === "asc" ? (
      <ChevronUp className="ml-1 inline h-4 w-4" />
    ) : (
      <ChevronDown className="ml-1 inline h-4 w-4" />
    );
  };

  const problemTypeColors: Record<string, string> = {
    classification: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
    regression: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    clustering: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
    other: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
  };

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[300px]">
                <button
                  className="flex items-center font-medium hover:text-foreground"
                  onClick={() => onSort("name")}
                >
                  Name
                  <SortIcon column="name" />
                </button>
              </TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="text-right">Rows</TableHead>
              <TableHead className="text-right">Columns</TableHead>
              <TableHead>
                <button
                  className="flex items-center font-medium hover:text-foreground"
                  onClick={() => onSort("created_at")}
                >
                  Created
                  <SortIcon column="created_at" />
                </button>
              </TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[50px]" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {datasets.map((dataset) => {
              // Look up job status by dataset ID
              const jobStatus = jobStatuses[dataset.id];
              const isProcessing =
                jobStatus &&
                (jobStatus.status === "pending" || jobStatus.status === "processing");
              const isFailed = jobStatus?.status === "failed";

              return (
                <TableRow
                  key={dataset.id}
                  className={cn(
                    "cursor-pointer transition-colors hover:bg-muted/50",
                    isProcessing && "bg-muted/30"
                  )}
                  onClick={() => !isProcessing && onView(dataset.id)}
                >
                  {/* Name */}
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                        {isProcessing ? (
                          <Loader2 className="h-4 w-4 animate-spin text-primary" />
                        ) : (
                          <Database className="h-4 w-4 text-primary" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-medium">{dataset.name}</p>
                        {dataset.description && (
                          <p className="truncate text-xs text-muted-foreground">
                            {dataset.description}
                          </p>
                        )}
                      </div>
                    </div>
                  </TableCell>

                  {/* Problem Type */}
                  <TableCell>
                    {dataset.problem_type ? (
                      <Badge
                        variant="secondary"
                        className={problemTypeColors[dataset.problem_type]}
                      >
                        {dataset.problem_type}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>

                  {/* Rows */}
                  <TableCell className="text-right font-mono">
                    {isProcessing ? (
                      "..."
                    ) : dataset.row_count !== null ? (
                      dataset.row_count.toLocaleString()
                    ) : (
                      "—"
                    )}
                  </TableCell>

                  {/* Columns */}
                  <TableCell className="text-right font-mono">
                    {isProcessing ? (
                      "..."
                    ) : dataset.column_count !== null ? (
                      dataset.column_count.toLocaleString()
                    ) : (
                      "—"
                    )}
                  </TableCell>

                  {/* Created */}
                  <TableCell className="text-muted-foreground">
                    {formatDistanceToNow(new Date(dataset.created_at), {
                      addSuffix: true,
                    })}
                  </TableCell>

                  {/* Status */}
                  <TableCell>
                    {isProcessing ? (
                      <div className="w-32 space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span>Processing</span>
                          <span>{jobStatus.progress_percentage}%</span>
                        </div>
                        <Progress
                          value={jobStatus.progress_percentage}
                          className="h-1.5"
                        />
                      </div>
                    ) : isFailed ? (
                      <Badge variant="destructive">Failed</Badge>
                    ) : (
                      <Badge
                        variant="outline"
                        className="bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400"
                      >
                        Ready
                      </Badge>
                    )}
                  </TableCell>

                  {/* Actions */}
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onView(dataset.id);
                          }}
                        >
                          <ExternalLink className="mr-2 h-4 w-4" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(dataset.id);
                          }}
                          className="text-destructive"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Infinite scroll trigger */}
      <div ref={loadMoreRef} className="flex justify-center py-4">
        {isFetchingNextPage && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading more...
          </div>
        )}
      </div>
    </div>
  );
}
