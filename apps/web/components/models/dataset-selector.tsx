/**
 * Dataset Selector Component
 * Dropdown to select a dataset that has trained models
 */

"use client";

import { useEffect, useState } from "react";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { getDatasetsWithModels } from "@/lib/api/models";
import { Database, Loader2 } from "lucide-react";

interface DatasetOption {
    id: string;
    name: string;
    modelCount: number;
}

interface DatasetSelectorProps {
    value: string | null;
    onChange: (datasetId: string | null) => void;
}

export function DatasetSelector({ value, onChange }: DatasetSelectorProps) {
    const [datasets, setDatasets] = useState<DatasetOption[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDatasets = async () => {
            try {
                setIsLoading(true);
                const data = await getDatasetsWithModels();
                setDatasets(data);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch datasets:", err);
                setError("Failed to load datasets");
            } finally {
                setIsLoading(false);
            }
        };

        fetchDatasets();
    }, []);

    if (isLoading) {
        return (
            <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Loading datasets...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-sm text-destructive">{error}</div>
        );
    }

    if (datasets.length === 0) {
        return (
            <div className="flex items-center gap-2 text-muted-foreground">
                <Database className="h-4 w-4" />
                <span className="text-sm">No datasets with trained models found</span>
            </div>
        );
    }

    return (
        <Select
            value={value || undefined}
            onValueChange={(val) => onChange(val || null)}
        >
            <SelectTrigger className="w-[280px]">
                <SelectValue placeholder="Select a dataset" />
            </SelectTrigger>
            <SelectContent>
                {datasets.map((dataset) => (
                    <SelectItem key={dataset.id} value={dataset.id}>
                        <div className="flex items-center gap-2">
                            <Database className="h-4 w-4 text-muted-foreground" />
                            <span>{dataset.name}</span>
                            <span className="text-xs text-muted-foreground">
                                ({dataset.modelCount} model{dataset.modelCount !== 1 ? "s" : ""})
                            </span>
                        </div>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    );
}
