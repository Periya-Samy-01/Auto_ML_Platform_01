/**
 * Model Selector Component
 * Dropdown to select models for comparison
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
import { getModelsByDataset } from "@/lib/api/models";
import { Brain, Loader2 } from "lucide-react";
import { format } from "date-fns";
import type { ModelBrief } from "@/types";

interface ModelSelectorProps {
    datasetId: string | null;
    value: string | null;
    onChange: (modelId: string | null) => void;
    excludeModelId?: string | null; // Exclude already selected model
    label?: string;
}

export function ModelSelector({
    datasetId,
    value,
    onChange,
    excludeModelId,
    label = "Select Model",
}: ModelSelectorProps) {
    const [models, setModels] = useState<ModelBrief[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!datasetId) {
            setModels([]);
            onChange(null);
            return;
        }

        const fetchModels = async () => {
            try {
                setIsLoading(true);
                const data = await getModelsByDataset(datasetId);
                setModels(data);
                setError(null);

                // Reset selection if current value is not in new list
                if (value && !data.find((m) => m.id === value)) {
                    onChange(null);
                }
            } catch (err) {
                console.error("Failed to fetch models:", err);
                setError("Failed to load models");
            } finally {
                setIsLoading(false);
            }
        };

        fetchModels();
    }, [datasetId]); // eslint-disable-line react-hooks/exhaustive-deps

    // Filter out excluded model
    const availableModels = excludeModelId
        ? models.filter((m) => m.id !== excludeModelId)
        : models;

    if (!datasetId) {
        return (
            <div className="flex items-center gap-2 text-muted-foreground">
                <Brain className="h-4 w-4" />
                <span className="text-sm">Select a dataset first</span>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Loading models...</span>
            </div>
        );
    }

    if (error) {
        return <div className="text-sm text-destructive">{error}</div>;
    }

    if (availableModels.length === 0) {
        return (
            <div className="flex items-center gap-2 text-muted-foreground">
                <Brain className="h-4 w-4" />
                <span className="text-sm">
                    {excludeModelId ? "No other models available" : "No models found"}
                </span>
            </div>
        );
    }

    const formatModelType = (type: string | null) => {
        if (!type) return "Unknown";
        return type
            .split("_")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    };

    return (
        <Select
            value={value || undefined}
            onValueChange={(val) => onChange(val || null)}
        >
            <SelectTrigger className="w-[280px]">
                <SelectValue placeholder={label} />
            </SelectTrigger>
            <SelectContent>
                {availableModels.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                        <div className="flex flex-col">
                            <span className="font-medium">
                                {model.name || "Untitled Model"}
                            </span>
                            <span className="text-xs text-muted-foreground">
                                {formatModelType(model.modelType)} •{" "}
                                {format(new Date(model.createdAt), "MMM dd, yyyy")}
                            </span>
                        </div>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    );
}
