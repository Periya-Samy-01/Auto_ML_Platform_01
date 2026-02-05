"use client";

import { useState, useMemo } from "react";
import { X, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AlgorithmId } from "@/configs/algorithms/types";
import { algorithmRegistry } from "@/configs/algorithms";

interface AlgorithmSelectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (algorithmId: AlgorithmId) => void;
}

// Task-based display configuration (grouped by problem type)
const taskConfig: Record<string, { label: string; icon: string; order: number }> = {
    classification: { label: "Classification", icon: "🏷️", order: 1 },
    regression: { label: "Regression", icon: "📈", order: 2 },
    clustering: { label: "Clustering", icon: "🎯", order: 3 },
};

export function AlgorithmSelectModal({
    isOpen,
    onClose,
    onSelect,
}: AlgorithmSelectModalProps) {
    const [searchQuery, setSearchQuery] = useState("");

    // Group algorithms by task (problem type)
    const groupedAlgorithms = useMemo(() => {
        const groups: Record<
            string,
            Array<{
                id: AlgorithmId;
                name: string;
                shortName: string;
                icon: string;
                description: string;
                category: string;
            }>
        > = {};

        Object.entries(algorithmRegistry).forEach(([id, config]) => {
            if (!config) return;

            // Filter by search query
            const matchesSearch =
                !searchQuery ||
                config.metadata.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                config.metadata.description.toLowerCase().includes(searchQuery.toLowerCase());

            if (!matchesSearch) return;

            const algorithmData = {
                id: id as AlgorithmId,
                name: config.metadata.name,
                shortName: config.metadata.shortName,
                icon: config.metadata.icon,
                description: config.metadata.description,
                category: config.metadata.category,
            };

            // Add algorithm to each problem type it supports
            const problemTypes = config.capabilities.problemTypes;

            // Handle clustering (K-Means doesn't have problemTypes, but has category)
            if (config.metadata.category === "clustering") {
                if (!groups["clustering"]) {
                    groups["clustering"] = [];
                }
                groups["clustering"].push(algorithmData);
            } else {
                // Add to each problem type group
                problemTypes.forEach((problemType) => {
                    if (!groups[problemType]) {
                        groups[problemType] = [];
                    }
                    groups[problemType].push(algorithmData);
                });
            }
        });

        // Sort groups by order and filter empty ones
        return Object.entries(groups)
            .filter(([, algorithms]) => algorithms.length > 0)
            .sort(([a], [b]) => {
                const orderA = taskConfig[a]?.order ?? 99;
                const orderB = taskConfig[b]?.order ?? 99;
                return orderA - orderB;
            });
    }, [searchQuery]);

    // Handle escape key
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Escape") {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center"
            onKeyDown={handleKeyDown}
        >
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className={cn(
                    "relative w-[600px] max-h-[80vh] overflow-hidden",
                    "bg-[rgba(20,20,20,0.98)] backdrop-blur-xl",
                    "border border-white/10 rounded-2xl",
                    "shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)]",
                    "flex flex-col"
                )}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">🤖</span>
                        <h2 className="text-lg font-semibold text-white">Select Algorithm</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors"
                    >
                        <X className="w-5 h-5 text-zinc-400" />
                    </button>
                </div>

                {/* Search */}
                <div className="px-6 py-3 border-b border-white/10">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <input
                            type="text"
                            placeholder="Search algorithms..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className={cn(
                                "w-full pl-10 pr-4 py-2.5 rounded-lg",
                                "bg-white/5 border border-white/10",
                                "text-sm text-white placeholder:text-zinc-500",
                                "focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20",
                                "transition-colors"
                            )}
                            autoFocus
                        />
                    </div>
                </div>

                {/* Algorithm List */}
                <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6">
                    {groupedAlgorithms.map(([taskType, algorithms]) => (
                        <div key={taskType}>
                            {/* Task Header */}
                            <div className="flex items-center gap-2 mb-3 px-2">
                                <span className="text-base">
                                    {taskConfig[taskType]?.icon ?? "📦"}
                                </span>
                                <span className="text-sm font-medium text-zinc-400">
                                    {taskConfig[taskType]?.label ?? taskType}
                                </span>
                                <div className="flex-1 h-px bg-white/10" />
                            </div>

                            {/* Algorithm Cards */}
                            <div className="grid grid-cols-2 gap-3">
                                {algorithms.map((algo) => (
                                    <button
                                        key={algo.id}
                                        onClick={() => onSelect(algo.id)}
                                        className={cn(
                                            "flex items-start gap-3 p-4 rounded-xl text-left",
                                            "bg-white/5 border border-white/10",
                                            "hover:bg-blue-500/10 hover:border-blue-500/30",
                                            "transition-all duration-200",
                                            "group"
                                        )}
                                    >
                                        <span className="text-2xl flex-shrink-0">{algo.icon}</span>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">
                                                {algo.name}
                                            </p>
                                            <p className="text-xs text-zinc-500 mt-1 line-clamp-2">
                                                {algo.description}
                                            </p>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* Empty State */}
                    {groupedAlgorithms.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-12">
                            <span className="text-4xl mb-3">🔍</span>
                            <p className="text-sm text-zinc-500">No algorithms found</p>
                            <button
                                onClick={() => setSearchQuery("")}
                                className="mt-2 text-xs text-blue-400 hover:text-blue-300"
                            >
                                Clear search
                            </button>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-white/10 bg-white/5">
                    <p className="text-xs text-zinc-500 text-center">
                        Choose an algorithm to create a model node. Configuration options will be available in the inspector panel.
                    </p>
                </div>
            </div>
        </div>
    );
}
