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
import { Github, Linkedin } from "lucide-react";

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
                  { title: "Render Cold Starts", desc: "NodeForge runs entirely on community free-tier hosting. If the app has been idle, please allow 1 to 2 minutes for the initial server to spin up and process your login." },
                  { title: "Temporary Redis Cache", desc: "Active workspace configurations and pipeline states use temporary cache sessions. Pipelines automatically reset after a period of inactivity to preserve resources." },
                  { title: "Fully Open Source", desc: "This platform is completely open-source. You are fully welcome to clone, copy, or modify any part of the architecture for your own personal or commercial projects." },
                  { title: "Instance Assistance", desc: "If you encounter a hard timeout, a broken canvas state, or need the database manually refreshed, connect with me directly via GitHub or LinkedIn to request a quick reboot." }
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full border border-fuchsia-400 bg-fuchsia-500/20 shadow-[0_0_10px_rgba(232,121,249,0.8)]" />
                    <span className="leading-relaxed">
                      <strong className="text-white font-semibold">{item.title}:</strong> {item.desc}
                    </span>
                  </li>
                ))}
              </ul>
              
              <div className="flex items-center gap-6 mt-8 pt-6 border-t border-indigo-500/20">
                <Link href="https://github.com/Periya-Samy-01" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-indigo-200/70 hover:text-fuchsia-400 transition-colors">
                  <Github className="w-5 h-5" />
                  <span>GitHub</span>
                </Link>
                <Link href="https://www.linkedin.com/in/periya-samy-ganesan-687370266" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-indigo-200/70 hover:text-fuchsia-400 transition-colors">
                  <Linkedin className="w-5 h-5" />
                  <span>LinkedIn</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
