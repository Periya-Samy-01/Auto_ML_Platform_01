import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Datasets | AutoML Platform",
  description:
    "Upload, manage, and explore your datasets. Supports CSV, Excel, and JSON formats with automatic profiling and visualization.",
};

export default function DatasetsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
