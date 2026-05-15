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
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50 via-white to-white px-4 py-12 dark:from-indigo-900/40 dark:via-slate-950 dark:to-slate-950">
      <Card className="w-full max-w-5xl overflow-hidden border-indigo-100 shadow-2xl dark:border-indigo-500/20 dark:shadow-[0_0_40px_-15px_rgba(79,70,229,0.3)]">
        <div className="grid lg:grid-cols-2">
          {/* Left Side: Login */}
          <div className="flex flex-col justify-center p-8 lg:p-12 lg:border-r border-indigo-100 dark:border-indigo-500/20 bg-white/60 dark:bg-slate-950/80 backdrop-blur-xl">
            <div className="mx-auto w-full max-w-md space-y-8">
              <div className="space-y-2 text-center">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-indigo-50">Welcome Back</h1>
                <p className="text-slate-500 dark:text-indigo-200/70">
                  Sign in to your account to continue
                </p>
              </div>
              
              <div className="mt-8">
                <OAuthButtons />
              </div>
              
              <div className="mt-6 text-center text-sm text-slate-500 dark:text-indigo-200/60">
                <p>
                  By continuing, you agree to our{" "}
                  <Link href="/terms" className="underline underline-offset-4 hover:text-slate-900 dark:hover:text-indigo-100">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link href="/privacy" className="underline underline-offset-4 hover:text-slate-900 dark:hover:text-indigo-100">
                    Privacy Policy
                  </Link>
                </p>
              </div>
            </div>
          </div>

          {/* Right Side: Important Info */}
          <div className="flex flex-col justify-center p-8 lg:p-12 bg-indigo-50/30 dark:bg-indigo-950/20">
            <div className="mx-auto w-full max-w-md space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-indigo-50">
                  Important Information
                </h2>
                <p className="text-sm text-slate-500 dark:text-indigo-200/70">
                  Please review the latest updates and announcements.
                </p>
              </div>
              
              <ul className="space-y-4 text-sm text-slate-700 dark:text-indigo-100/80 mt-6">
                {[
                  "Platform maintenance is scheduled for this weekend. Expect brief downtimes.",
                  "New state-of-the-art models have been deployed to the platform registry.",
                  "We've updated our API rate limits. Please check the new documentation.",
                  "Security update: Ensure your access tokens are rotated every 30 days.",
                  "Join our upcoming webinar on optimizing AutoML pipelines for production."
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full border border-indigo-500 dark:border-fuchsia-500 bg-transparent dark:shadow-[0_0_8px_rgba(217,70,239,0.8)]" />
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
