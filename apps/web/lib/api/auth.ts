/**
 * Auth API
 * Authentication-related API calls
 */

import api from "@/lib/axios";
import type { User, TokenPair, MessageResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get OAuth login URL
 */
export const getGoogleAuthUrl = () => {
  return `${API_URL}/api/auth/google`;
};

export const getGitHubAuthUrl = () => {
  return `${API_URL}/api/auth/github`;
};

/**
 * Get current user profile
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>("/auth/me");
  return response.data;
};

/**
 * Refresh tokens
 */
export const refreshTokens = async (refreshToken: string): Promise<TokenPair> => {
  const response = await api.post<TokenPair>("/auth/refresh", {
    refresh_token: refreshToken,
  });
  return response.data;
};

/**
 * Logout
 */
export const logout = async (refreshToken: string): Promise<MessageResponse> => {
  const response = await api.post<MessageResponse>("/auth/logout", {
    refresh_token: refreshToken,
  });
  return response.data;
};

/**
 * Dev login (development only)
 */
export const devLogin = async (email: string, fullName?: string) => {
  const response = await api.post("/auth/dev-login", {
    email,
    full_name: fullName,
  });
  return response.data;
};
