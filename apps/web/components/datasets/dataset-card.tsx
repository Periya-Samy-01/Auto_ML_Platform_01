"use client";

/**
 * Dataset Card
 * Card view for a single dataset
 */

import { formatDistanceToNow } from "date-fns";
import { Database, MoreVertical, Trash2, ExternalLink, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Dataset, JobStatusResponse } from "@/types";

interface DatasetCardProps {
  dataset: Dataset;
  jobStatus?: JobStatusResponse;
  onView: (id: string) => void;
  onDelete: (id: string) => void;
}

export function DatasetCard({ dataset, jobStatus, onView, onDelete }: DatasetCardProps) {
  const isProcessing = jobStatus && 
    (jobStatus.status === "pending" || jobStatus.status === "processing");
  const isFailed = jobStatus?.status === "failed";

  const problemTypeColors: Record<string, string> = {
    classification: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
    regression: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    clustering: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
    other: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
  };

  return (
    <Card className="group relative transition-shadow hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              {isProcessing ? (
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
              ) : (
                <Database className="h-5 w-5 text-primary" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="truncate font-semibold">{dataset.name}</h3>
              <p className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(dataset.created_at), { addSuffix: true })}
              </p>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onView(dataset.id)}>
                <ExternalLink className="mr-2 h-4 w-4" />
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete(dataset.id)}
                className="text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Processing Progress */}
        {isProcessing && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Processing...</span>
              <span className="font-medium">{jobStatus.progress_percentage}%</span>
            </div>
            <Progress value={jobStatus.progress_percentage} className="h-1.5" />
          </div>
        )}

        {/* Error State */}
        {isFailed && (
          <div className="rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">
            {jobStatus.error_message || "Processing failed"}
          </div>
        )}

        {/* Stats */}
        {!isProcessing && !isFailed && (
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-muted-foreground">Rows</p>
              <p className="font-medium">
                {dataset.row_count?.toLocaleString() ?? "—"}
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">Columns</p>
              <p className="font-medium">
                {dataset.column_count?.toLocaleString() ?? "—"}
              </p>
            </div>
          </div>
        )}

        {/* Problem Type Badge */}
        {dataset.problem_type && (
          <Badge
            variant="secondary"
            className={problemTypeColors[dataset.problem_type]}
          >
            {dataset.problem_type}
          </Badge>
        )}

        {/* Description */}
        {dataset.description && (
          <p className="line-clamp-2 text-xs text-muted-foreground">
            {dataset.description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
