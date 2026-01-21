import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Model Library | AutoML Platform",
  description:
    "Explore and train machine learning models including Random Forest, XGBoost, Neural Networks, K-Means clustering, and more.",
};

export default function ModelsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
