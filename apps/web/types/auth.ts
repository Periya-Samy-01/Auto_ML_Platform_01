/**
 * Auth Types
 * Matches backend auth schemas
 */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  tier: "free" | "pro" | "enterprise";
  email_verified: boolean;
  oauth_provider: "google" | "github" | null;
  created_at: string;
  dataset_count: number;
  workflow_count: number;
  model_count: number;
  storage_used_bytes: number;
}

export interface UserBrief {
  id: string;
  email: string;
  full_name: string | null;
  tier: "free" | "pro" | "enterprise";
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse extends TokenPair {
  user: UserBrief;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
}

export interface AuthCallbackParams {
  access_token?: string;
  refresh_token?: string;
  is_new?: string;
  error?: string;
  message?: string;
}
