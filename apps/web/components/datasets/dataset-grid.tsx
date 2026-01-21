"use client";

/**
 * Dataset Grid
 * Grid view of dataset cards with infinite scroll
 */

import { useEffect, useRef } from "react";
import { Loader2 } from "lucide-react";
import { DatasetCard } from "./dataset-card";
import type { Dataset, JobStatusResponse } from "@/types";

interface DatasetGridProps {
  datasets: Dataset[];
  /** Job statuses keyed by dataset ID */
  jobStatuses: Record<string, JobStatusResponse | undefined>;
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
  onView: (id: string) => void;
  onDelete: (id: string) => void;
}

export function DatasetGrid({
  datasets,
  jobStatuses,
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  onView,
  onDelete,
}: DatasetGridProps) {
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

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {datasets.map((dataset) => (
          <DatasetCard
            key={dataset.id}
            dataset={dataset}
            jobStatus={jobStatuses[dataset.id]}
            onView={onView}
            onDelete={onDelete}
          />
        ))}
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
