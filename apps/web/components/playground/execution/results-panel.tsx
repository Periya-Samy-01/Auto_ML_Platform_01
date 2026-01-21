"use client";

import { useState } from "react";
import { X, Download, ExternalLink, ChevronDown, ChevronRight, Trophy, Clock, Database } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import type { WorkflowResults, MetricResult, PlotResult } from "@/hooks/use-workflow-execution";

interface ResultsPanelProps {
  results: WorkflowResults;
  onClose: () => void;
  onDownloadModel?: () => void;
}

function formatMetricValue(value: number): string {
  if (Math.abs(value) < 0.01 || Math.abs(value) >= 1000) {
    return value.toExponential(3);
  }
  return value.toFixed(4);
}

function MetricCard({ metric }: { metric: MetricResult }) {
  return (
    <div className="p-4 rounded-lg border border-border bg-card/50">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-muted-foreground">{metric.name}</span>
      </div>
      <div className="text-2xl font-bold text-foreground">
        {formatMetricValue(metric.value)}
      </div>
      {metric.confidenceInterval && (
        <div className="text-xs text-muted-foreground mt-1">
          CI: [{formatMetricValue(metric.confidenceInterval[0])}, {formatMetricValue(metric.confidenceInterval[1])}]
        </div>
      )}
    </div>
  );
}

function PlotCard({ plot, onClick }: { plot: PlotResult; onClick: () => void }) {
  return (
    <div
      className="group relative rounded-lg border border-border overflow-hidden cursor-pointer hover:border-primary/50 transition-colors"
      onClick={onClick}
    >
      <div className="aspect-[4/3] bg-muted">
        <img
          src={plot.thumbnailUrl || plot.url}
          alt={plot.name}
          className="w-full h-full object-contain"
        />
      </div>
      <div className="p-2 bg-card">
        <span className="text-sm font-medium text-foreground">{plot.name}</span>
      </div>
      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
        <ExternalLink className="h-6 w-6 text-white" />
      </div>
    </div>
  );
}

function StatItem({ icon: Icon, label, value }: { icon: typeof Trophy; label: string; value: string | number }) {
  return (
    <div className="flex items-center gap-2">
      <Icon className="h-4 w-4 text-muted-foreground" />
      <span className="text-sm text-muted-foreground">{label}:</span>
      <span className="text-sm font-medium text-foreground">{value}</span>
    </div>
  );
}

export function ResultsPanel({ results, onClose, onDownloadModel }: ResultsPanelProps) {
  const [expandedPlot, setExpandedPlot] = useState<PlotResult | null>(null);
  const [metricsExpanded, setMetricsExpanded] = useState(true);

  return (
    <>
      {/* Results Panel */}
      <div className="fixed right-0 top-0 bottom-0 w-96 z-40 border-l border-border bg-card shadow-lg overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div>
            <h3 className="text-lg font-semibold text-foreground">Results</h3>
            <p className="text-sm text-muted-foreground">{results.algorithmName}</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Summary Stats */}
        <div className="p-4 border-b border-border bg-muted/30 grid grid-cols-2 gap-3">
          <StatItem icon={Trophy} label="Type" value={results.problemType} />
          <StatItem icon={Clock} label="Time" value={`${results.trainingTimeSeconds.toFixed(1)}s`} />
          <StatItem icon={Database} label="Train" value={results.trainSamples} />
          <StatItem icon={Database} label="Test" value={results.testSamples} />
        </div>

        {/* Content Tabs */}
        <Tabs defaultValue="metrics" className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="w-full justify-start px-4 pt-2 bg-transparent border-b border-border rounded-none">
            <TabsTrigger value="metrics" className="data-[state=active]:bg-muted">
              Metrics ({results.metrics.length})
            </TabsTrigger>
            <TabsTrigger value="plots" className="data-[state=active]:bg-muted">
              Plots ({results.plots.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="metrics" className="flex-1 overflow-y-auto p-4 mt-0">
            <div className="grid grid-cols-2 gap-3">
              {results.metrics.map((metric) => (
                <MetricCard key={metric.key} metric={metric} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="plots" className="flex-1 overflow-y-auto p-4 mt-0">
            <div className="grid grid-cols-2 gap-3">
              {results.plots.map((plot) => (
                <PlotCard
                  key={plot.key}
                  plot={plot}
                  onClick={() => setExpandedPlot(plot)}
                />
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Actions */}
        <div className="p-4 border-t border-border flex gap-2">
          {results.modelPath && onDownloadModel && (
            <Button onClick={onDownloadModel} className="flex-1 gap-2">
              <Download className="h-4 w-4" />
              Download Model
            </Button>
          )}
          <Button variant="outline" onClick={onClose} className={cn(!results.modelPath && "flex-1")}>
            Close
          </Button>
        </div>
      </div>

      {/* Expanded Plot Modal */}
      {expandedPlot && (
        <div
          className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-8"
          onClick={() => setExpandedPlot(null)}
        >
          <div
            className="max-w-4xl max-h-full bg-card rounded-lg border border-border shadow-lg overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h4 className="font-semibold text-foreground">{expandedPlot.name}</h4>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setExpandedPlot(null)}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4">
              <img
                src={expandedPlot.url}
                alt={expandedPlot.name}
                className="max-w-full max-h-[70vh] object-contain mx-auto"
              />
            </div>
            <div className="p-4 border-t border-border flex justify-end">
              <Button variant="outline" asChild>
                <a href={expandedPlot.url} download target="_blank" rel="noopener noreferrer">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </a>
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
