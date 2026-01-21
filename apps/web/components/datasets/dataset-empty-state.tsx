"use client";

/**
 * Dataset Empty State
 * Shown when user has no datasets
 */

import { Database, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DatasetEmptyStateProps {
  onUpload: () => void;
}

export function DatasetEmptyState({ onUpload }: DatasetEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
        <Database className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-lg font-semibold">No datasets yet</h3>
      <p className="mt-2 max-w-sm text-center text-sm text-muted-foreground">
        Upload your first dataset to start building machine learning models.
        We support CSV, JSON, Excel, and Parquet files.
      </p>
      <Button onClick={onUpload} className="mt-6">
        <Upload className="mr-2 h-4 w-4" />
        Upload Dataset
      </Button>
    </div>
  );
}
