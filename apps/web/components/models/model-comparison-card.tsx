/**
 * Model Comparison Card Component
 * Combines metrics chart and hyperparameters table for a single model
 */

"use client";

import { MetricsBarChart } from "./metrics-bar-chart";
import { HyperparametersTable } from "./hyperparameters-table";
import type { Model } from "@/types";

interface ModelComparisonCardProps {
    model: Model | null;
    winningMetrics?: Record<string, boolean>;
    isOverallWinner?: boolean;
}

export function ModelComparisonCard({
    model,
    winningMetrics = {},
    isOverallWinner = false,
}: ModelComparisonCardProps) {
    if (!model) {
        return (
            <div className="flex-1 flex flex-col gap-4">
                <div className="h-[250px] flex items-center justify-center text-muted-foreground border border-dashed border-border rounded-lg bg-card/50">
                    <span>Select a model to compare</span>
                </div>
                <div className="h-[200px] flex items-center justify-center text-muted-foreground border border-dashed border-border rounded-lg bg-card/50">
                    <span>Hyperparameters will appear here</span>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 flex flex-col gap-4">
            {/* Metrics Chart */}
            <MetricsBarChart
                metrics={model.metricsJson}
                modelName={model.name || "Untitled Model"}
                isWinner={winningMetrics}
            />

            {/* Hyperparameters Table */}
            <HyperparametersTable
                modelName={model.name || "Untitled Model"}
                hyperparameters={model.hyperparametersJson}
                isWinningModel={isOverallWinner}
            />
        </div>
    );
}
