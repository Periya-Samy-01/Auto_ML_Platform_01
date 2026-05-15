"use client";

/**
 * Login Page
 * OAuth login with Google and GitHub and Information Panel
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth-store";
import { OAuthButtons } from "@/components/auth";
import { Card } from "@/components/ui/card";

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isInitialized } = useAuthStore();

  // Redirect if already authenticated
  useEffect(() => {
    if (isInitialized && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isInitialized, isAuthenticated, router]);

  return (
    <div className="flex min-h-screen items-center justify-center dashboard-bg px-4 py-12 relative">
      <div className="dashboard-mesh absolute inset-0 z-0"></div>
      <Card className="w-full max-w-5xl overflow-hidden glass-card shadow-2xl relative z-10">
        <div className="grid lg:grid-cols-2">
          {/* Left Side: Login */}
          <div className="flex flex-col justify-center p-8 lg:p-12 lg:border-r border-indigo-500/20 bg-white/5 dark:bg-black/10 backdrop-blur-md">
            <div className="mx-auto w-full max-w-md space-y-8">
              <div className="space-y-2 text-center">
                <h1 className="text-3xl font-bold tracking-tight text-white gradient-text">Welcome Back</h1>
                <p className="text-indigo-200/70">
                  Sign in to your account to continue
                </p>
              </div>
              
              <div className="mt-8">
                <OAuthButtons />
              </div>
              
              <div className="mt-6 text-center text-sm text-indigo-200/60">
                <p>
                  By continuing, you agree to our{" "}
                  <Link href="/terms" className="underline underline-offset-4 hover:text-indigo-100">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link href="/privacy" className="underline underline-offset-4 hover:text-indigo-100">
                    Privacy Policy
                  </Link>
                </p>
              </div>
            </div>
          </div>

          {/* Right Side: Important Info */}
          <div className="flex flex-col justify-center p-8 lg:p-12 bg-indigo-950/20">
            <div className="mx-auto w-full max-w-md space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight text-white gradient-text">
                  Important Information
                </h2>
                <p className="text-sm text-indigo-200/70">
                  Please review the latest updates and announcements.
                </p>
              </div>
              
              <ul className="space-y-4 text-sm text-indigo-100/90 mt-6">
                {[
                  "Platform maintenance is scheduled for this weekend. Expect brief downtimes.",
                  "New state-of-the-art models have been deployed to the platform registry.",
                  "We've updated our API rate limits. Please check the new documentation.",
                  "Security update: Ensure your access tokens are rotated every 30 days.",
                  "Join our upcoming webinar on optimizing AutoML pipelines for production."
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full border border-fuchsia-400 bg-fuchsia-500/20 shadow-[0_0_10px_rgba(232,121,249,0.8)]" />
                    <span className="leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
