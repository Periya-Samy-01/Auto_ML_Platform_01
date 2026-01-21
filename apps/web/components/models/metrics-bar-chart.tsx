/**
 * Metrics Bar Chart Component
 * Bar chart displaying model metrics with kebab menu
 */

"use client";

import { useState } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { MoreVertical, Download, Table2, BarChart3 } from "lucide-react";
import type { ModelMetrics } from "@/types";

interface MetricsBarChartProps {
    metrics: ModelMetrics | null;
    modelName: string;
    isWinner?: Record<string, boolean>; // Which metrics are "winning"
    onExport?: () => void;
}

// Metric display configuration
const METRIC_CONFIG: Record<string, { label: string; color: string }> = {
    accuracy: { label: "Accuracy", color: "#22c55e" },
    precision: { label: "Precision", color: "#3b82f6" },
    recall: { label: "Recall", color: "#8b5cf6" },
    f1_score: { label: "F1 Score", color: "#f59e0b" },
    roc_auc: { label: "ROC AUC", color: "#ec4899" },
    r2_score: { label: "R² Score", color: "#06b6d4" },
    mae: { label: "MAE", color: "#ef4444" },
    mse: { label: "MSE", color: "#f97316" },
    rmse: { label: "RMSE", color: "#a855f7" },
};

export function MetricsBarChart({
    metrics,
    modelName,
    isWinner = {},
    onExport,
}: MetricsBarChartProps) {
    const [viewMode, setViewMode] = useState<"chart" | "table">("chart");

    // Transform metrics to chart data
    const chartData = metrics
        ? Object.entries(metrics)
            .filter(([key, value]) => value !== undefined && METRIC_CONFIG[key])
            .map(([key, value]) => ({
                name: METRIC_CONFIG[key]?.label || key,
                value: typeof value === "number" ? value : 0,
                key,
                color: METRIC_CONFIG[key]?.color || "#6b7280",
                isWinner: isWinner[key] || false,
            }))
        : [];

    const handleExportJSON = () => {
        const exportData = {
            modelName,
            metrics,
            exportedAt: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${modelName.replace(/\s+/g, "_")}_metrics.json`;
        a.click();
        URL.revokeObjectURL(url);
        onExport?.();
    };

    const handleExportCSV = () => {
        if (!metrics) return;
        const headers = ["Metric", "Value"];
        const rows = chartData.map((d) => [d.name, d.value.toString()]);
        const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${modelName.replace(/\s+/g, "_")}_metrics.csv`;
        a.click();
        URL.revokeObjectURL(url);
        onExport?.();
    };

    if (!metrics || chartData.length === 0) {
        return (
            <div className="h-[250px] flex items-center justify-center text-muted-foreground border border-border rounded-lg bg-card">
                <span>No metrics available</span>
            </div>
        );
    }

    return (
        <div className="relative border border-border rounded-lg bg-card overflow-hidden">
            {/* Kebab Menu */}
            <div className="absolute top-2 right-2 z-10">
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setViewMode(viewMode === "chart" ? "table" : "chart")}>
                            {viewMode === "chart" ? (
                                <>
                                    <Table2 className="h-4 w-4 mr-2" />
                                    Switch to Table View
                                </>
                            ) : (
                                <>
                                    <BarChart3 className="h-4 w-4 mr-2" />
                                    Switch to Chart View
                                </>
                            )}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={handleExportJSON}>
                            <Download className="h-4 w-4 mr-2" />
                            Download JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={handleExportCSV}>
                            <Download className="h-4 w-4 mr-2" />
                            Download CSV
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>

            {/* Chart or Table View */}
            <div className="h-[250px] p-4">
                {viewMode === "chart" ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis
                                dataKey="name"
                                tick={{ fill: "#9ca3af", fontSize: 11 }}
                                axisLine={{ stroke: "#4b5563" }}
                                tickLine={{ stroke: "#4b5563" }}
                                angle={-45}
                                textAnchor="end"
                                height={60}
                            />
                            <YAxis
                                tick={{ fill: "#9ca3af", fontSize: 11 }}
                                axisLine={{ stroke: "#4b5563" }}
                                tickLine={{ stroke: "#4b5563" }}
                                domain={[0, 1]}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "#1f2937",
                                    border: "1px solid #374151",
                                    borderRadius: "8px",
                                    color: "#f9fafb",
                                }}
                                formatter={(value: number | undefined) => {
                                    const numValue = typeof value === 'number' ? value : 0;
                                    return [numValue.toFixed(4), "Value"];
                                }}
                            />
                            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                {chartData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={entry.color}
                                        stroke={entry.isWinner ? "#22c55e" : "transparent"}
                                        strokeWidth={entry.isWinner ? 3 : 0}
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full overflow-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border">
                                    <th className="text-left py-2 px-3 text-muted-foreground font-medium">
                                        Metric
                                    </th>
                                    <th className="text-right py-2 px-3 text-muted-foreground font-medium">
                                        Value
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {chartData.map((row) => (
                                    <tr
                                        key={row.key}
                                        className={`border-b border-border/50 ${row.isWinner ? "bg-green-500/10" : ""
                                            }`}
                                    >
                                        <td className="py-2 px-3">
                                            <span
                                                className="inline-block w-2 h-2 rounded-full mr-2"
                                                style={{ backgroundColor: row.color }}
                                            />
                                            {row.name}
                                        </td>
                                        <td
                                            className={`py-2 px-3 text-right font-mono ${row.isWinner ? "text-green-400 font-semibold" : ""
                                                }`}
                                        >
                                            {row.value.toFixed(4)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
