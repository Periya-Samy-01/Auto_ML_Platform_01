import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Learning Center | AutoML Platform",
  description:
    "Master machine learning concepts with interactive tutorials. Learn about classification, regression, clustering, neural networks, and more.",
};

export default function LearnLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
