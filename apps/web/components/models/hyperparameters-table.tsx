/**
 * Hyperparameters Table Component
 * Displays model hyperparameters in a table format
 */

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HyperparametersTableProps {
    modelName: string;
    hyperparameters: Record<string, unknown> | null;
    isWinningModel?: boolean;
}

export function HyperparametersTable({
    modelName,
    hyperparameters,
    isWinningModel = false,
}: HyperparametersTableProps) {
    // Parse hyperparameters to display
    const entries = hyperparameters
        ? Object.entries(hyperparameters)
            .filter(([, value]) => value !== null && value !== undefined)
            .map(([key, value]) => ({
                key: formatKey(key),
                value: formatValue(value),
            }))
        : [];

    return (
        <Card
            className={`${isWinningModel ? "border-green-500/50 ring-1 ring-green-500/20" : ""
                }`}
        >
            <CardHeader className="py-3 px-4">
                <CardTitle className="text-base flex items-center gap-2">
                    <span className="truncate">{modelName || "Untitled Model"}</span>
                    {isWinningModel && (
                        <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                            Winner
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent className="px-0 py-0">
                {entries.length === 0 ? (
                    <div className="px-4 py-6 text-center text-muted-foreground text-sm">
                        No hyperparameters available
                    </div>
                ) : (
                    <div className="divide-y divide-border">
                        {entries.map((entry, index) => (
                            <div
                                key={index}
                                className="flex items-center justify-between px-4 py-2 text-sm hover:bg-muted/30 transition-colors"
                            >
                                <span className="text-muted-foreground">{entry.key}</span>
                                <span className="font-mono text-foreground">{entry.value}</span>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

/**
 * Format parameter key for display
 */
function formatKey(key: string): string {
    return key
        .replace(/_/g, " ")
        .replace(/([A-Z])/g, " $1")
        .split(" ")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(" ")
        .trim();
}

/**
 * Format parameter value for display
 */
function formatValue(value: unknown): string {
    if (typeof value === "boolean") {
        return value ? "Yes" : "No";
    }
    if (typeof value === "number") {
        // Format numbers nicely
        if (Number.isInteger(value)) {
            return value.toString();
        }
        return value.toFixed(4);
    }
    if (Array.isArray(value)) {
        return `[${value.join(", ")}]`;
    }
    if (typeof value === "object" && value !== null) {
        return JSON.stringify(value);
    }
    return String(value);
}
