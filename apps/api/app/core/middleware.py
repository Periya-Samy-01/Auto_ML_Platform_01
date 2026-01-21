"""
Rate Limiting Middleware
Simple in-memory rate limiter with Redis fallback
"""

import time
from typing import Dict, Tuple
from collections import defaultdict
import logging

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    
    Uses in-memory storage for simplicity. For production with multiple
    instances, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.window_size = 60  # 1 minute in seconds
        
        # In-memory storage: {ip: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (when behind proxy)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, ip: str, current_time: float) -> None:
        """Remove requests outside the current window"""
        cutoff = current_time - self.window_size
        self._requests[ip] = [
            ts for ts in self._requests[ip] 
            if ts > cutoff
        ]
    
    def _check_rate_limit(self, ip: str) -> Tuple[bool, int]:
        """
        Check if request should be allowed.
        
        Returns:
            Tuple of (allowed, remaining_requests)
        """
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(ip, current_time)
        
        # Count requests in current window
        request_count = len(self._requests[ip])
        
        if request_count >= self.requests_per_minute:
            return False, 0
        
        # Record this request
        self._requests[ip].append(current_time)
        remaining = self.requests_per_minute - request_count - 1
        
        return True, remaining
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        allowed, remaining = self._check_rate_limit(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window_size),
                    "Retry-After": str(self.window_size),
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_size)
        
        return response
