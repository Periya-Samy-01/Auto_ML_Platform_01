/**
 * Axios Instance
 * Configured with base URL, interceptors for auth and token refresh
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getStoredTokens, setStoredTokens, clearStoredTokens } from "@/stores/auth-store";

// ⚠️ TEMPORARY: Set to true to bypass auth redirects for UI development
// Must match the same flag in auth-guard.tsx
const DEV_BYPASS_AUTH = false;

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance
export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 5 minutes - needed for synchronous workflow execution
});

// Track if we're currently refreshing to avoid multiple refresh calls
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = getStoredTokens();

    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // If not 401 or no config, reject immediately
    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    // DEV MODE: Skip auth redirects entirely - just reject the error
    if (DEV_BYPASS_AUTH) {
      console.warn("[DEV MODE] Skipping 401 auth redirect");
      return Promise.reject(error);
    }

    // If already retried, reject
    if (originalRequest._retry) {
      clearStoredTokens();
      // Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }
      return Promise.reject(error);
    }

    // If already refreshing, queue this request
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const { refreshToken } = getStoredTokens();

    if (!refreshToken) {
      isRefreshing = false;
      clearStoredTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }
      return Promise.reject(error);
    }

    try {
      // Call refresh endpoint
      const response = await axios.post(`${API_URL}/api/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token } = response.data;

      // Store new tokens
      setStoredTokens(access_token, refresh_token);

      // Update auth header for original request
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
      }

      // Process queued requests
      processQueue(null, access_token);

      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError as Error, null);
      clearStoredTokens();

      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }

      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
