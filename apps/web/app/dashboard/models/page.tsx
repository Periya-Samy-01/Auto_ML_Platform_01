"use client";

import { useState, useEffect, useMemo } from "react";
import { Loader2, GitCompare, Trophy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DatasetSelector,
  ModelSelector,
  ModelComparisonCard,
} from "@/components/models";
import { getModelDetails } from "@/lib/api/models";
import type { Model, ModelMetrics } from "@/types";

export default function ModelsPage() {
  // Selection state
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [selectedModel1Id, setSelectedModel1Id] = useState<string | null>(null);
  const [selectedModel2Id, setSelectedModel2Id] = useState<string | null>(null);

  // Model data state
  const [model1, setModel1] = useState<Model | null>(null);
  const [model2, setModel2] = useState<Model | null>(null);
  const [isLoadingModel1, setIsLoadingModel1] = useState(false);
  const [isLoadingModel2, setIsLoadingModel2] = useState(false);

  // Fetch model 1 details
  useEffect(() => {
    if (!selectedModel1Id) {
      setModel1(null);
      return;
    }

    const fetchModel = async () => {
      try {
        setIsLoadingModel1(true);
        const data = await getModelDetails(selectedModel1Id);
        setModel1(data);
      } catch (err) {
        console.error("Failed to fetch model 1:", err);
        setModel1(null);
      } finally {
        setIsLoadingModel1(false);
      }
    };

    fetchModel();
  }, [selectedModel1Id]);

  // Fetch model 2 details
  useEffect(() => {
    if (!selectedModel2Id) {
      setModel2(null);
      return;
    }

    const fetchModel = async () => {
      try {
        setIsLoadingModel2(true);
        const data = await getModelDetails(selectedModel2Id);
        setModel2(data);
      } catch (err) {
        console.error("Failed to fetch model 2:", err);
        setModel2(null);
      } finally {
        setIsLoadingModel2(false);
      }
    };

    fetchModel();
  }, [selectedModel2Id]);

  // Reset model selections when dataset changes
  useEffect(() => {
    setSelectedModel1Id(null);
    setSelectedModel2Id(null);
    setModel1(null);
    setModel2(null);
  }, [selectedDatasetId]);

  // Calculate winning metrics
  const { model1Wins, model2Wins, overallWinner } = useMemo(() => {
    const result: {
      model1Wins: Record<string, boolean>;
      model2Wins: Record<string, boolean>;
      overallWinner: 1 | 2 | null;
    } = {
      model1Wins: {},
      model2Wins: {},
      overallWinner: null,
    };

    if (!model1?.metricsJson || !model2?.metricsJson) {
      return result;
    }

    const metrics1 = model1.metricsJson;
    const metrics2 = model2.metricsJson;

    // Metrics where higher is better
    const higherIsBetter = ["accuracy", "precision", "recall", "f1_score", "roc_auc", "r2_score"];
    // Metrics where lower is better
    const lowerIsBetter = ["mae", "mse", "rmse"];

    let model1Score = 0;
    let model2Score = 0;

    // Compare each metric
    const allKeys = new Set([
      ...Object.keys(metrics1),
      ...Object.keys(metrics2),
    ]);

    for (const key of allKeys) {
      const val1 = metrics1[key as keyof ModelMetrics];
      const val2 = metrics2[key as keyof ModelMetrics];

      if (typeof val1 !== "number" || typeof val2 !== "number") continue;

      let model1Better = false;
      let model2Better = false;

      if (higherIsBetter.includes(key)) {
        if (val1 > val2) model1Better = true;
        else if (val2 > val1) model2Better = true;
      } else if (lowerIsBetter.includes(key)) {
        if (val1 < val2) model1Better = true;
        else if (val2 < val1) model2Better = true;
      }

      if (model1Better) {
        result.model1Wins[key] = true;
        model1Score++;
      }
      if (model2Better) {
        result.model2Wins[key] = true;
        model2Score++;
      }
    }

    // Determine overall winner
    if (model1Score > model2Score) {
      result.overallWinner = 1;
    } else if (model2Score > model1Score) {
      result.overallWinner = 2;
    }

    return result;
  }, [model1, model2]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold flex items-center gap-2">
            <GitCompare className="h-6 w-6 text-primary" />
            Model Comparison
          </h2>
          <p className="text-muted-foreground mt-1">
            Compare trained models side-by-side to find the best performer
          </p>
        </div>
      </div>

      {/* Selection Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Dataset Selector */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">
                Dataset:
              </span>
              <DatasetSelector
                value={selectedDatasetId}
                onChange={setSelectedDatasetId}
              />
            </div>

            {/* Separator */}
            <div className="h-8 w-px bg-border hidden sm:block" />

            {/* Model 1 Selector */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">
                Model 1:
              </span>
              <ModelSelector
                datasetId={selectedDatasetId}
                value={selectedModel1Id}
                onChange={setSelectedModel1Id}
                excludeModelId={selectedModel2Id}
                label="Select Model 1"
              />
            </div>

            {/* Model 2 Selector */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">
                Model 2:
              </span>
              <ModelSelector
                datasetId={selectedDatasetId}
                value={selectedModel2Id}
                onChange={setSelectedModel2Id}
                excludeModelId={selectedModel1Id}
                label="Select Model 2"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Winner Banner (if both models selected) */}
      {model1 && model2 && overallWinner && (
        <Card className="border-green-500/50 bg-green-500/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Trophy className="h-6 w-6 text-green-400" />
              <div>
                <span className="font-medium text-green-400">
                  {overallWinner === 1
                    ? model1.name || "Model 1"
                    : model2.name || "Model 2"}
                </span>
                <span className="text-muted-foreground">
                  {" "}
                  wins on more metrics!
                </span>
              </div>
              <Badge
                variant="secondary"
                className="bg-green-500/20 text-green-400 ml-auto"
              >
                Winner
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model 1 Card */}
        <div className="relative">
          {isLoadingModel1 && (
            <div className="absolute inset-0 bg-background/50 flex items-center justify-center z-10 rounded-lg">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          )}
          <ModelComparisonCard
            model={model1}
            winningMetrics={model1Wins}
            isOverallWinner={overallWinner === 1}
          />
        </div>

        {/* Model 2 Card */}
        <div className="relative">
          {isLoadingModel2 && (
            <div className="absolute inset-0 bg-background/50 flex items-center justify-center z-10 rounded-lg">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          )}
          <ModelComparisonCard
            model={model2}
            winningMetrics={model2Wins}
            isOverallWinner={overallWinner === 2}
          />
        </div>
      </div>
    </div>
  );
}
