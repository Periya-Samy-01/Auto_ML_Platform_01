"use client";

/**
 * Auth Guard
 * Protects routes that require authentication
 */

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

// ⚠️ TEMPORARY: Set to true to bypass auth for UI development
const DEV_BYPASS_AUTH = false;

// Mock user for dev bypass
const MOCK_USER = {
  id: "dev-user-123",
  email: "dev@example.com",
  full_name: "Dev User",
  tier: "pro" as const,
  email_verified: true,
  oauth_provider: "google" as const,
  created_at: new Date().toISOString(),
  dataset_count: 5,
  workflow_count: 3,
  model_count: 2,
  storage_used_bytes: 1024 * 1024 * 50, // 50MB
};

interface AuthGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function AuthGuard({ children, fallback }: AuthGuardProps) {
  const router = useRouter();
  const { isAuthenticated, isInitialized, isLoading, setUser, setTokens, setInitialized } = useAuthStore();

  useEffect(() => {
    // Dev bypass: set mock user and skip auth
    if (DEV_BYPASS_AUTH) {
      setUser(MOCK_USER);
      setTokens("dev-access-token", "dev-refresh-token");
      setInitialized(true);
      return;
    }

    if (isInitialized && !isAuthenticated) {
      // Save current URL to redirect back after login
      if (typeof window !== "undefined") {
        const currentPath = window.location.pathname + window.location.search;
        if (currentPath !== "/auth/login" && currentPath !== "/auth/callback") {
          sessionStorage.setItem("auth_redirect_url", currentPath);
        }
      }
      router.push("/auth/login");
    }
  }, [isInitialized, isAuthenticated, router, setUser, setTokens, setInitialized]);

  // Dev bypass: render immediately
  if (DEV_BYPASS_AUTH) {
    return <>{children}</>;
  }

  // Show loading state while initializing
  if (!isInitialized || isLoading) {
    return fallback || <AuthLoadingScreen />;
  }

  // Not authenticated, will redirect
  if (!isAuthenticated) {
    return fallback || <AuthLoadingScreen />;
  }

  return <>{children}</>;
}

function AuthLoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}
