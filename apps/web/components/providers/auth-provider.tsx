"use client";

/**
 * Auth Provider
 * Handles auth initialization and hydration
 */

import { useEffect, useState, type ReactNode } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { getCurrentUser } from "@/lib/api/auth";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const {
    accessToken,
    isInitialized,
    isAuthenticated,
    setUser,
    setInitialized,
    setLoading,
    logout
  } = useAuthStore();

  // Track if Zustand has hydrated from localStorage
  const [hydrated, setHydrated] = useState(false);

  // Wait for Zustand to hydrate before doing anything
  useEffect(() => {
    // Zustand persist middleware hydrates on client-side mount
    // We need to wait a tick for the state to be available
    const timer = setTimeout(() => {
      setHydrated(true);
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // Don't run until Zustand has hydrated
    if (!hydrated) return;

    const initAuth = async () => {
      // Skip if already initialized
      if (isInitialized) return;

      // Check if we have a token from hydrated state
      if (!accessToken) {
        setInitialized(true);
        return;
      }

      // We have a token - if we also have a user from localStorage, 
      // consider ourselves initialized (user data is persisted)
      if (isAuthenticated) {
        setInitialized(true);
        return;
      }

      // Try to fetch current user (token exists but no user data)
      setLoading(true);
      try {
        const user = await getCurrentUser();
        setUser(user);
      } catch (error) {
        // Token invalid, logout
        console.error("Failed to fetch user:", error);
        logout();
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    };

    initAuth();
  }, [hydrated, accessToken, isInitialized, isAuthenticated, setUser, setInitialized, setLoading, logout]);

  return <>{children}</>;
}
