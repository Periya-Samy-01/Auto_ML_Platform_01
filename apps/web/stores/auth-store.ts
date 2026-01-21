/**
 * Auth Store
 * Zustand store for authentication state
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User, AuthState } from "@/types";

const TOKEN_KEYS = {
  ACCESS: "automl_access_token",
  REFRESH: "automl_refresh_token",
} as const;

interface AuthActions {
  // Actions
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
  setInitialized: (initialized: boolean) => void;
  logout: () => void;
  reset: () => void;
  
  // Computed
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  isInitialized: false,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      setTokens: (accessToken: string, refreshToken: string) => {
        // Also store in localStorage for axios interceptor access
        if (typeof window !== "undefined") {
          localStorage.setItem(TOKEN_KEYS.ACCESS, accessToken);
          localStorage.setItem(TOKEN_KEYS.REFRESH, refreshToken);
        }
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setLoading: (isLoading: boolean) => {
        set({ isLoading });
      },

      setInitialized: (isInitialized: boolean) => {
        set({ isInitialized });
      },

      logout: () => {
        // Clear localStorage
        if (typeof window !== "undefined") {
          localStorage.removeItem(TOKEN_KEYS.ACCESS);
          localStorage.removeItem(TOKEN_KEYS.REFRESH);
        }
        set({
          ...initialState,
          isInitialized: true, // Keep initialized after logout
        });
      },

      reset: () => {
        if (typeof window !== "undefined") {
          localStorage.removeItem(TOKEN_KEYS.ACCESS);
          localStorage.removeItem(TOKEN_KEYS.REFRESH);
        }
        set(initialState);
      },

      getAccessToken: () => {
        // Prefer store state, fallback to localStorage
        const state = get();
        if (state.accessToken) return state.accessToken;
        if (typeof window !== "undefined") {
          return localStorage.getItem(TOKEN_KEYS.ACCESS);
        }
        return null;
      },

      getRefreshToken: () => {
        const state = get();
        if (state.refreshToken) return state.refreshToken;
        if (typeof window !== "undefined") {
          return localStorage.getItem(TOKEN_KEYS.REFRESH);
        }
        return null;
      },
    }),
    {
      name: "automl-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Utility to get tokens outside of React components (for axios interceptors)
export const getStoredTokens = () => {
  if (typeof window === "undefined") {
    return { accessToken: null, refreshToken: null };
  }
  return {
    accessToken: localStorage.getItem(TOKEN_KEYS.ACCESS),
    refreshToken: localStorage.getItem(TOKEN_KEYS.REFRESH),
  };
};

export const setStoredTokens = (accessToken: string, refreshToken: string) => {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEYS.ACCESS, accessToken);
    localStorage.setItem(TOKEN_KEYS.REFRESH, refreshToken);
  }
};

export const clearStoredTokens = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEYS.ACCESS);
    localStorage.removeItem(TOKEN_KEYS.REFRESH);
  }
};
