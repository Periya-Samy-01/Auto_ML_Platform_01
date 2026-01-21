"use client";

/**
 * Sample Dataset Grid
 * Displays sample datasets in a read-only grid format.
 * Users can only view and use samples - no delete/edit options.
 */

import { useMemo, useState } from "react";
import { Database, Search, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    SAMPLE_DATASETS,
    formatFileSize,
    formatRowCount,
    type SampleDataset,
} from "@/components/playground/nodes/sample-datasets";

interface SampleDatasetGridProps {
    onUseDataset?: (dataset: SampleDataset) => void;
}

export function SampleDatasetGrid({ onUseDataset }: SampleDatasetGridProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [problemTypeFilter, setProblemTypeFilter] = useState<string>("all");

    // Filter datasets
    const filteredDatasets = useMemo(() => {
        let result = SAMPLE_DATASETS;

        // Search filter
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            result = result.filter(
                (d) =>
                    d.name.toLowerCase().includes(query) ||
                    d.description.toLowerCase().includes(query) ||
                    d.tags.some((t) => t.toLowerCase().includes(query))
            );
        }

        // Problem type filter
        if (problemTypeFilter !== "all") {
            result = result.filter((d) =>
                d.availableProblemTypes.some((pt) => pt.value === problemTypeFilter)
            );
        }

        return result;
    }, [searchQuery, problemTypeFilter]);

    const problemTypeColors: Record<string, string> = {
        classification: "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300",
        regression: "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300",
        clustering: "bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300",
        time_series: "bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300",
        nlp: "bg-pink-100 text-pink-800 dark:bg-pink-900/50 dark:text-pink-300",
        image: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/50 dark:text-cyan-300",
    };

    const tagColors: Record<string, string> = {
        beginner: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300",
        intermediate: "bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300",
        advanced: "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300",
    };

    return (
        <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        placeholder="Search sample datasets..."
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
                        <SelectItem value="time_series">Time Series</SelectItem>
                        <SelectItem value="nlp">NLP</SelectItem>
                        <SelectItem value="image">Image</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            {/* Dataset count */}
            <p className="text-sm text-muted-foreground">
                Showing {filteredDatasets.length} of {SAMPLE_DATASETS.length} sample datasets
            </p>

            {/* Dataset Grid */}
            {filteredDatasets.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Sparkles className="w-12 h-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No sample datasets match your filters.</p>
                </div>
            ) : (
                <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                    {filteredDatasets.map((dataset) => (
                        <Card
                            key={dataset.id}
                            className="group cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
                            onClick={() => onUseDataset?.(dataset)}
                        >
                            <CardHeader className="pb-3">
                                <div className="flex items-start gap-3">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10">
                                        <Database className="h-5 w-5 text-purple-500" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-semibold truncate group-hover:text-primary transition-colors">
                                            {dataset.name}
                                        </h3>
                                        <p className="text-xs text-muted-foreground line-clamp-1">
                                            {dataset.description}
                                        </p>
                                    </div>
                                </div>
                            </CardHeader>

                            <CardContent className="space-y-3">
                                {/* Stats */}
                                <div className="grid grid-cols-3 gap-2 text-sm">
                                    <div>
                                        <p className="text-muted-foreground text-xs">Rows</p>
                                        <p className="font-medium">{formatRowCount(dataset.rows)}</p>
                                    </div>
                                    <div>
                                        <p className="text-muted-foreground text-xs">Cols</p>
                                        <p className="font-medium">{dataset.columns}</p>
                                    </div>
                                    <div>
                                        <p className="text-muted-foreground text-xs">Size</p>
                                        <p className="font-medium">{formatFileSize(dataset.size)}</p>
                                    </div>
                                </div>

                                {/* Problem Types */}
                                <div className="flex flex-wrap gap-1.5">
                                    {dataset.availableProblemTypes.map((pt) => (
                                        <Badge
                                            key={pt.value}
                                            variant="secondary"
                                            className={`text-xs ${problemTypeColors[pt.value] || ""}`}
                                        >
                                            {pt.label}
                                        </Badge>
                                    ))}
                                </div>

                                {/* Tags */}
                                <div className="flex flex-wrap gap-1.5">
                                    {dataset.tags.slice(0, 3).map((tag) => (
                                        <Badge
                                            key={tag}
                                            variant="outline"
                                            className={`text-xs ${tagColors[tag] || ""}`}
                                        >
                                            {tag}
                                        </Badge>
                                    ))}
                                </div>

                                {/* Target column */}
                                <p className="text-xs text-muted-foreground">
                                    Target: <span className="font-mono text-foreground">{dataset.defaultTarget}</span>
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
