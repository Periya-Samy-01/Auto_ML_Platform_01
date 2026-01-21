"use client";

/**
 * Providers
 * Combines all providers into a single component
 */

import { type ReactNode } from "react";
import { QueryProvider } from "./query-provider";
import { AuthProvider } from "./auth-provider";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryProvider>
      <AuthProvider>{children}</AuthProvider>
    </QueryProvider>
  );
}

export { QueryProvider } from "./query-provider";
export { AuthProvider } from "./auth-provider";
