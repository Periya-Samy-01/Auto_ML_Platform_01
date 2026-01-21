# Authentication System

> **Note**: This documentation reflects the current authentication implementation. The system may evolve as the platform develops.

## Overview

The AutoML Platform uses a hybrid authentication system that combines OAuth providers (Google, GitHub) for login with JWT tokens for API access. This provides secure, third-party authentication without needing to store passwords.

---

## How Authentication Works

### The Login Flow

1. **User clicks "Login with Google/GitHub"** on the frontend
2. **Frontend redirects to API** (`/api/auth/google` or `/api/auth/github`)
3. **API redirects to OAuth provider** with a security token (state)
4. **User logs in** on Google/GitHub's page
5. **Provider redirects back to API** with an authorization code
6. **API exchanges code for user info** from the provider
7. **API creates or finds user** in the database
8. **API generates JWT tokens** (access + refresh)
9. **API redirects to frontend** with tokens in the URL
10. **Frontend stores tokens** and uses them for API requests

### Why This Approach?

- **No passwords to store**: Users authenticate with Google/GitHub
- **Secure by default**: OAuth is a well-tested standard
- **Easy for users**: One-click login with existing accounts
- **Stateless API**: JWT tokens don't require server-side session storage

---

## OAuth Providers

### Google OAuth

**Required Configuration**:
- `GOOGLE_CLIENT_ID`: OAuth client ID from Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: OAuth client secret

**Scopes Requested**:
- `email`: User's email address
- `profile`: User's name and profile picture

**User Information Retrieved**:
- Email address
- Full name
- Profile picture URL (if available)

### GitHub OAuth

**Required Configuration**:
- `GITHUB_CLIENT_ID`: OAuth app client ID from GitHub
- `GITHUB_CLIENT_SECRET`: OAuth app client secret

**Scopes Requested**:
- `user:email`: Access to email addresses
- `read:user`: Access to profile information

**User Information Retrieved**:
- Email address (primary email from GitHub)
- Username/display name
- Avatar URL

---

## JWT Tokens

The platform uses JSON Web Tokens (JWT) for stateless authentication. Two types of tokens are issued:

### Access Token

**Purpose**: Used for making API requests

**Lifetime**: 15 minutes

**Contents**:
- `sub`: User ID (UUID)
- `type`: "access"
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

**How to use**: Include in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

### Refresh Token

**Purpose**: Used to get new access tokens without re-logging in

**Lifetime**: 7 days

**Contents**:
- `sub`: User ID (UUID)
- `type`: "refresh"
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

**How to use**: Send to `/api/auth/refresh` endpoint

### Token Flow

```
Initial Login → Access Token (15 min) + Refresh Token (7 days)
                      ↓
            Access token expires
                      ↓
        Use refresh token to get new pair
                      ↓
          New Access Token (15 min)
          New Refresh Token (7 days)
          Old refresh token is invalidated
```

---

## Token Security

### State Tokens (CSRF Protection)

When initiating OAuth login, the API:
1. Generates a random state token
2. Stores it in Redis with 5-minute expiration
3. Includes it in the OAuth redirect URL
4. Verifies it when the callback returns

This prevents Cross-Site Request Forgery attacks.

### Refresh Token Blacklisting

When a refresh token is used:
1. The old token is added to a blacklist in Redis
2. A new token pair is generated
3. Blacklisted tokens are rejected even if not expired

This prevents:
- Token reuse if stolen
- Multiple sessions from the same refresh

### Token Signing

Tokens are signed using:
- **Algorithm**: HS256 (HMAC-SHA256)
- **Secret Key**: Configured via `SECRET_KEY` environment variable

The secret key should be a long, random string and kept secure.

---

## Redis Session Management

Redis is used for session-related data:

### OAuth State Storage

```
Key: oauth_state:{state_token}
Value: "1" (just marks existence)
TTL: 300 seconds (5 minutes)
```

### Token Blacklist

```
Key: token_blacklist:{token_hash}
Value: "1"
TTL: Same as original token expiration
```

This ensures:
- Blacklist entries auto-expire when tokens would have expired
- Memory doesn't grow unbounded

---

## User Tiers

Users are assigned a tier that affects their capabilities:

| Tier | Description |
|------|-------------|
| **FREE** | Default for new users. Limited resources. |
| **PRO** | Paid tier with increased limits. |
| **ENTERPRISE** | Highest limits for businesses. |

Tier affects:
- Maximum file upload size
- Storage quota
- Job priority in queue
- Available features

---

## User Properties

When a user is created via OAuth:

| Property | Source |
|----------|--------|
| `email` | From OAuth provider |
| `full_name` | From OAuth provider |
| `oauth_provider` | google or github |
| `email_verified` | true (OAuth verifies this) |
| `tier` | FREE (default) |
| `credit_balance` | Initial free credits |

---

## Development Login

For local development without OAuth configured, there's a bypass endpoint:

**Endpoint**: POST `/api/auth/dev-login`

**Requirements**:
- `DEBUG=true` or `ENVIRONMENT=development`

**How it works**:
1. Provide an email address
2. API creates user if not exists
3. Returns tokens immediately

**Use case**: Testing and development without OAuth setup

---

## How the Backend Validates Requests

When an API request comes in with an access token:

1. **Extract token** from Authorization header
2. **Verify signature** using the secret key
3. **Check expiration** (reject if expired)
4. **Extract user ID** from the `sub` claim
5. **Lookup user** in the database
6. **Check user status** (reject if deleted)
7. **Make user available** to the endpoint handler

This happens via FastAPI's dependency injection system (`get_current_user`).

---

## Files Involved

| File | Purpose |
|------|---------|
| `auth/router.py` | API endpoints for login, logout, refresh |
| `auth/jwt.py` | Token creation and verification |
| `auth/oauth.py` | OAuth provider integrations |
| `auth/redis.py` | Redis client for sessions |
| `auth/dependencies.py` | FastAPI dependencies for auth |
| `auth/schemas.py` | Request/response Pydantic models |
| `auth/service.py` | Business logic for user management |

---

## Configuration

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | JWT signing key | Random 32+ character string |
| `ALGORITHM` | JWT algorithm | "HS256" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | 15 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | 7 |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | From Google Cloud Console |
| `GITHUB_CLIENT_ID` | GitHub OAuth ID | From GitHub Settings |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret | From GitHub Settings |
| `FRONTEND_URL` | Frontend URL for redirects | http://localhost:3000 |

---

## Security Considerations

1. **HTTPS Required**: In production, all traffic should use HTTPS
2. **Secure Storage**: Frontend should store tokens securely (httpOnly cookies or secure storage)
3. **Token Rotation**: Refresh tokens are single-use
4. **Short Access Tokens**: 15-minute lifetime limits exposure if stolen
5. **State Validation**: CSRF protection on OAuth callbacks
6. **Secret Management**: JWT secret should never be exposed
