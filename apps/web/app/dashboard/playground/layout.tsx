import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ML Playground | AutoML Platform",
  description:
    "Build machine learning pipelines visually with our drag-and-drop workflow editor. Connect data processing, training, and evaluation nodes.",
};

export default function PlaygroundLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
