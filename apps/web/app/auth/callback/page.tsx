"use client";

/**
 * Auth Callback Page
 * Handles OAuth redirect, extracts tokens, stores them, redirects to dashboard
 */

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { getCurrentUser } from "@/lib/api/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setTokens, setUser, setInitialized } = useAuthStore();

  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const processCallback = async () => {
      // Check for error first
      const errorParam = searchParams.get("error");
      if (errorParam) {
        const message = searchParams.get("message") || errorParam;
        setError(decodeURIComponent(message));
        setIsProcessing(false);
        return;
      }

      // Extract tokens
      const accessToken = searchParams.get("access_token");
      const refreshToken = searchParams.get("refresh_token");

      if (!accessToken || !refreshToken) {
        setError("Missing authentication tokens");
        setIsProcessing(false);
        return;
      }

      try {
        // Store tokens
        setTokens(accessToken, refreshToken);

        // Fetch user profile
        const user = await getCurrentUser();
        setUser(user);
        setInitialized(true);

        // Check if new user for onboarding
        const isNew = searchParams.get("is_new") === "true";

        // Get saved redirect URL or default to dashboard
        let redirectUrl = "/dashboard";
        if (typeof window !== "undefined") {
          const savedUrl = sessionStorage.getItem("auth_redirect_url");
          if (savedUrl && !isNew) {
            redirectUrl = savedUrl;
            sessionStorage.removeItem("auth_redirect_url");
          } else if (isNew) {
            redirectUrl = "/dashboard?welcome=true";
          }
        }

        router.push(redirectUrl);
      } catch (err) {
        console.error("Failed to process auth callback:", err);
        setError("Failed to complete authentication");
        setIsProcessing(false);
      }
    };

    processCallback();
  }, [searchParams, setTokens, setUser, setInitialized, router]);

  if (isProcessing) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Completing sign in...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 px-4 dark:bg-zinc-950">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-destructive">
              Authentication Failed
            </CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <Button onClick={() => router.push("/auth/login")}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return null;
}

function LoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <AuthCallbackContent />
    </Suspense>
  );
}
