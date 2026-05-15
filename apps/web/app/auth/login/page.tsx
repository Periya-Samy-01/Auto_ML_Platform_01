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
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-100 via-zinc-50 to-white px-4 py-12 dark:from-zinc-900 dark:via-zinc-950 dark:to-black">
      <Card className="w-full max-w-5xl overflow-hidden border-zinc-200/50 shadow-2xl dark:border-zinc-800/50">
        <div className="grid lg:grid-cols-2">
          {/* Left Side: Login */}
          <div className="flex flex-col justify-center p-8 lg:p-12 lg:border-r border-zinc-200 dark:border-zinc-800 bg-white/50 dark:bg-zinc-950/50 backdrop-blur-sm">
            <div className="mx-auto w-full max-w-md space-y-8">
              <div className="space-y-2 text-center">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">Welcome Back</h1>
                <p className="text-zinc-500 dark:text-zinc-400">
                  Sign in to your account to continue
                </p>
              </div>
              
              <div className="mt-8">
                <OAuthButtons />
              </div>
              
              <div className="mt-6 text-center text-sm text-zinc-500 dark:text-zinc-400">
                <p>
                  By continuing, you agree to our{" "}
                  <Link href="/terms" className="underline underline-offset-4 hover:text-zinc-900 dark:hover:text-zinc-50">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link href="/privacy" className="underline underline-offset-4 hover:text-zinc-900 dark:hover:text-zinc-50">
                    Privacy Policy
                  </Link>
                </p>
              </div>
            </div>
          </div>

          {/* Right Side: Important Info */}
          <div className="flex flex-col justify-center p-8 lg:p-12 bg-zinc-50/50 dark:bg-zinc-900/30">
            <div className="mx-auto w-full max-w-md space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                  Important Information
                </h2>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                  Please review the latest updates and announcements.
                </p>
              </div>
              
              <ul className="space-y-4 text-sm text-zinc-700 dark:text-zinc-300 mt-6">
                {[
                  "Platform maintenance is scheduled for this weekend. Expect brief downtimes.",
                  "New state-of-the-art models have been deployed to the platform registry.",
                  "We've updated our API rate limits. Please check the new documentation.",
                  "Security update: Ensure your access tokens are rotated every 30 days.",
                  "Join our upcoming webinar on optimizing AutoML pipelines for production."
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full border border-blue-600 dark:border-blue-400 bg-transparent" />
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
