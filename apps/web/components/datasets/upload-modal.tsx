"use client";

/**
 * Upload Modal
 * Multi-step dataset upload with drag-drop and progress
 */

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  File,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useUploadDataset } from "@/hooks/use-datasets";
import type { ProblemType } from "@/types";

interface UploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: (datasetId: string, jobId: string) => void;
}

const ACCEPTED_FORMATS = {
  "text/csv": [".csv"],
  "application/json": [".json"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "application/vnd.ms-excel": [".xls"],
  "application/x-parquet": [".parquet"],
};

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB default

export function UploadModal({ open, onOpenChange, onSuccess }: UploadModalProps) {
  const [step, setStep] = useState<"select" | "details" | "uploading">("select");
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [problemType, setProblemType] = useState<ProblemType | "">("");
  const [targetColumn, setTargetColumn] = useState("");

  const { mutate: upload, uploadState, resetState } = useUploadDataset();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      setFile(selectedFile);
      const nameWithoutExt = selectedFile.name.replace(/\.[^/.]+$/, "");
      setName(nameWithoutExt);
      setStep("details");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: ACCEPTED_FORMATS,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
  });

  const handleUpload = () => {
    if (!file || !name.trim()) return;

    setStep("uploading");
    upload(
      {
        file,
        name: name.trim(),
        description: description.trim() || undefined,
        problemType: problemType || undefined,
        targetColumn: targetColumn.trim() || undefined,
      },
      {
        onSuccess: (data) => {
          onSuccess?.(data.dataset_id, data.job_id);
          setTimeout(() => {
            handleClose();
          }, 1500);
        },
      }
    );
  };

  const handleClose = () => {
    setStep("select");
    setFile(null);
    setName("");
    setDescription("");
    setProblemType("");
    setTargetColumn("");
    resetState();
    onOpenChange(false);
  };

  const handleBack = () => {
    if (step === "details") {
      setStep("select");
      setFile(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStepLabel = () => {
    switch (uploadState.step) {
      case "getting-url":
        return "Preparing upload...";
      case "uploading":
        return "Uploading file...";
      case "confirming":
        return "Starting processing...";
      case "processing":
        return "Upload complete!";
      case "error":
        return "Upload failed";
      default:
        return "Uploading...";
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Upload Dataset</DialogTitle>
          <DialogDescription>
            {step === "select" && "Select a file to upload. Supported formats: CSV, JSON, Excel, Parquet."}
            {step === "details" && "Provide details about your dataset."}
            {step === "uploading" && "Please wait while your file is being uploaded."}
          </DialogDescription>
        </DialogHeader>

        {/* Step 1: File Selection */}
        {step === "select" && (
          <div className="space-y-4">
            <div
              {...getRootProps()}
              className={cn(
                "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors",
                isDragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
              )}
            >
              <input {...getInputProps()} />
              <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
              {isDragActive ? (
                <p className="text-sm text-primary">Drop the file here</p>
              ) : (
                <>
                  <p className="text-sm font-medium">
                    Drag and drop a file here, or click to select
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    CSV, JSON, Excel, or Parquet (max 100MB)
                  </p>
                </>
              )}
            </div>

            {fileRejections.length > 0 && (
              <div className="flex items-center gap-2 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                {fileRejections[0].errors[0].message}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Dataset Details */}
        {step === "details" && file && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 rounded-lg border bg-muted/50 p-3">
              <File className="h-8 w-8 text-primary" />
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {formatFileSize(file.size)}
                </p>
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleBack}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Dataset Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter dataset name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional description"
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="problemType">Problem Type</Label>
              <Select value={problemType} onValueChange={(v) => setProblemType(v as ProblemType)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select problem type (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="classification">Classification</SelectItem>
                  <SelectItem value="regression">Regression</SelectItem>
                  <SelectItem value="clustering">Clustering</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="targetColumn">Target Column</Label>
              <Input
                id="targetColumn"
                value={targetColumn}
                onChange={(e) => setTargetColumn(e.target.value)}
                placeholder="Column name to predict (optional)"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={handleBack}>Back</Button>
              <Button onClick={handleUpload} disabled={!name.trim()}>Upload</Button>
            </div>
          </div>
        )}

        {/* Step 3: Uploading */}
        {step === "uploading" && (
          <div className="space-y-6 py-4">
            <div className="flex flex-col items-center">
              {uploadState.step === "processing" ? (
                <CheckCircle2 className="h-12 w-12 text-green-500" />
              ) : uploadState.step === "error" ? (
                <AlertCircle className="h-12 w-12 text-destructive" />
              ) : (
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
              )}
              <p className="mt-4 font-medium">{getStepLabel()}</p>
              {uploadState.error && (
                <p className="mt-2 text-sm text-destructive">{uploadState.error}</p>
              )}
            </div>

            {uploadState.step === "uploading" && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Uploading</span>
                  <span className="font-medium">{uploadState.progress}%</span>
                </div>
                <Progress value={uploadState.progress} />
              </div>
            )}

            {uploadState.step === "processing" && (
              <p className="text-center text-sm text-muted-foreground">
                Your dataset is being processed. You can close this dialog and track progress in the table.
              </p>
            )}

            {uploadState.step === "error" && (
              <div className="flex justify-center gap-2">
                <Button variant="outline" onClick={handleClose}>Cancel</Button>
                <Button onClick={() => setStep("details")}>Try Again</Button>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
