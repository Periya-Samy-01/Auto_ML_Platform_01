"use client";

/**
 * Dashboard Layout
 * Wraps all dashboard pages with auth protection and layout components
 */

import { type ReactNode } from "react";
import { AuthGuard } from "@/components/auth";
import { DashboardLayout } from "@/components/layout";

interface DashboardLayoutRootProps {
  children: ReactNode;
}

export default function DashboardLayoutRoot({ children }: DashboardLayoutRootProps) {
  return (
    <AuthGuard>
      <DashboardLayout>{children}</DashboardLayout>
    </AuthGuard>
  );
}
