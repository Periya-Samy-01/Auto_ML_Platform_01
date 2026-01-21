# Security Improvements: HTTP-Only Cookie Authentication

This document outlines the changes needed to migrate from localStorage-based JWT storage to HTTP-only cookies for improved security.

## Current Implementation

### Problem with localStorage

The current implementation stores JWT tokens in localStorage:

- **XSS Vulnerability**: JavaScript can access localStorage, meaning any XSS attack can steal tokens
- **No automatic CSRF protection**: Tokens must be manually attached to requests
- **Tokens persist indefinitely**: Unless explicitly cleared, tokens remain in localStorage

### Current Files Involved

1. **`stores/auth-store.ts`** - Manages auth state and token storage
2. **`lib/axios.ts`** - Attaches tokens to API requests and handles refresh

---

## Proposed Changes

### 1. Backend API Changes (Required First)

The backend API must be modified to:

1. **Set HTTP-only cookies** on login/refresh responses:
   ```python
   # Example FastAPI response
   response.set_cookie(
       key="access_token",
       value=access_token,
       httponly=True,
       secure=True,  # Only send over HTTPS
       samesite="lax",  # or "strict" for more security
       max_age=900,  # 15 minutes
       path="/api"
   )
   response.set_cookie(
       key="refresh_token",
       value=refresh_token,
       httponly=True,
       secure=True,
       samesite="lax",
       max_age=604800,  # 7 days
       path="/api/auth/refresh"  # Only sent to refresh endpoint
   )
   ```

2. **Read tokens from cookies** instead of request body/headers

3. **Implement CSRF protection**:
   - Generate CSRF token on login
   - Return CSRF token in response body (not cookie)
   - Validate CSRF token on state-changing requests

---

### 2. Changes to `lib/axios.ts`

#### Current Code (Remove)
```typescript
// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = getStoredTokens();

    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;
  },
  ...
);
```

#### New Code (Add)
```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with credentials
export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
  withCredentials: true, // ← CRITICAL: Send cookies with requests
});

// Store CSRF token in memory (not localStorage)
let csrfToken: string | null = null;

export const setCsrfToken = (token: string) => {
  csrfToken = token;
};

export const getCsrfToken = () => csrfToken;

// Request interceptor - add CSRF token to state-changing requests
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add CSRF token for non-GET requests
    if (config.method !== "get" && csrfToken && config.headers) {
      config.headers["X-CSRF-Token"] = csrfToken;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401 (unchanged logic, but no token management)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    if (originalRequest._retry) {
      // Redirect to login - cookie will be cleared by backend
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      // Call refresh endpoint - cookies are sent automatically
      const response = await axios.post(
        `${API_URL}/api/auth/refresh`,
        {},
        { withCredentials: true }
      );

      // Update CSRF token from response
      if (response.data.csrf_token) {
        setCsrfToken(response.data.csrf_token);
      }

      return api(originalRequest);
    } catch (refreshError) {
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }
      return Promise.reject(refreshError);
    }
  }
);

export default api;
```

---

### 3. Changes to `stores/auth-store.ts`

#### Remove Token Storage Logic

```typescript
// REMOVE these constants
const TOKEN_KEYS = {
  ACCESS: "automl_access_token",
  REFRESH: "automl_refresh_token",
} as const;

// REMOVE these utility functions
export const getStoredTokens = () => { ... };
export const setStoredTokens = () => { ... };
export const clearStoredTokens = () => { ... };
```

#### Simplified Auth Store

```typescript
/**
 * Auth Store (HTTP-Only Cookie Version)
 * Zustand store for authentication state
 *
 * Note: Tokens are now managed by HTTP-only cookies.
 * This store only tracks user info and auth status.
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  csrfToken: string | null;
}

interface AuthActions {
  setUser: (user: User | null) => void;
  setCsrfToken: (token: string) => void;
  setLoading: (loading: boolean) => void;
  setInitialized: (initialized: boolean) => void;
  logout: () => void;
  reset: () => void;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isInitialized: false,
  csrfToken: null,
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      ...initialState,

      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },

      setCsrfToken: (csrfToken: string) => {
        set({ csrfToken });
        // Also update the axios module's CSRF token
        import("@/lib/axios").then(({ setCsrfToken }) => {
          setCsrfToken(csrfToken);
        });
      },

      setLoading: (isLoading: boolean) => {
        set({ isLoading });
      },

      setInitialized: (isInitialized: boolean) => {
        set({ isInitialized });
      },

      logout: async () => {
        // Call logout endpoint to clear HTTP-only cookies
        try {
          const { api } = await import("@/lib/axios");
          await api.post("/auth/logout");
        } catch (error) {
          console.error("Logout failed:", error);
        }
        set({
          ...initialState,
          isInitialized: true,
        });
      },

      reset: () => {
        set(initialState);
      },
    }),
    {
      name: "automl-auth",
      storage: createJSONStorage(() => localStorage),
      // Only persist user info and auth status (not tokens!)
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

---

### 4. Changes to Auth Callback Handler

Update `app/auth/callback/page.tsx` to handle the new flow:

```typescript
// After successful OAuth callback, the backend sets cookies
// We only need to fetch user info and CSRF token

const handleCallback = async () => {
  try {
    // Backend has already set HTTP-only cookies
    // Fetch user info (cookies sent automatically)
    const response = await api.get("/auth/me");

    setUser(response.data.user);
    setCsrfToken(response.data.csrf_token);

    router.push("/dashboard");
  } catch (error) {
    router.push("/auth/login?error=callback_failed");
  }
};
```

---

### 5. Auth Provider Changes

Update `components/providers/auth-provider.tsx` to check auth status via API:

```typescript
useEffect(() => {
  const checkAuth = async () => {
    setLoading(true);
    try {
      // Check if we have a valid session (cookies sent automatically)
      const response = await api.get("/auth/me");
      setUser(response.data.user);
      setCsrfToken(response.data.csrf_token);
    } catch (error) {
      // Not authenticated - that's okay
      setUser(null);
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  };

  checkAuth();
}, []);
```

---

## Migration Steps

### Phase 1: Backend Preparation
1. Add cookie-setting logic to login/refresh endpoints
2. Add `/auth/me` endpoint to fetch current user from cookie
3. Add `/auth/logout` endpoint to clear cookies
4. Implement CSRF token generation and validation
5. Keep existing token-in-body endpoints for backwards compatibility

### Phase 2: Frontend Migration
1. Update `lib/axios.ts` with `withCredentials: true`
2. Add CSRF token handling to axios interceptors
3. Simplify `stores/auth-store.ts` to remove token management
4. Update auth callback to use new flow
5. Update auth provider to check session via API

### Phase 3: Cleanup
1. Remove localStorage token storage code
2. Remove token-in-body support from backend
3. Update any remaining direct localStorage access

---

## Security Considerations

### CSRF Protection
- CSRF tokens should be:
  - Generated server-side with cryptographic randomness
  - Tied to the user's session
  - Validated on all state-changing requests (POST, PUT, DELETE)
  - Rotated on login and privilege escalation

### Cookie Configuration
```
httpOnly: true      # Prevents JavaScript access
secure: true        # Only sent over HTTPS
sameSite: "lax"     # Prevents CSRF on cross-origin requests
path: "/api"        # Only sent to API routes
```

### Additional Recommendations
1. **Implement token rotation**: Rotate refresh token on each use
2. **Add rate limiting**: Prevent brute force attacks on refresh endpoint
3. **Monitor for anomalies**: Log unusual patterns (multiple refresh attempts, etc.)
4. **Consider fingerprinting**: Bind tokens to browser fingerprint for extra security

---

## Testing Checklist

- [ ] Login sets HTTP-only cookies
- [ ] Cookies are sent with API requests (`withCredentials`)
- [ ] CSRF token is validated on POST/PUT/DELETE
- [ ] Token refresh works with cookie-based auth
- [ ] Logout clears all cookies
- [ ] Auth state persists across page refreshes
- [ ] Auth state clears when cookies expire
- [ ] Cross-origin requests are properly blocked
- [ ] XSS attacks cannot access tokens
