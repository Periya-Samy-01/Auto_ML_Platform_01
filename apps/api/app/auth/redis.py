"""
Redis Client
Token blacklist and caching
"""

from typing import Optional

import redis.asyncio as redis

from app.core.config import settings


class RedisClient:
    """Async Redis client for token blacklist and caching"""
    
    _instance: Optional["RedisClient"] = None
    _redis: Optional[redis.Redis] = None
    
    # Key prefixes
    BLACKLIST_PREFIX = "token:blacklist:"
    OAUTH_STATE_PREFIX = "oauth:state:"
    
    # TTL (7 days for refresh token blacklist, 5 minutes for OAuth state)
    BLACKLIST_TTL_SECONDS = 7 * 24 * 60 * 60
    OAUTH_STATE_TTL_SECONDS = 5 * 60  # 5 minutes
    
    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> None:
        """Initialize Redis connection"""
        if self._redis is None:
            redis_url = settings.REDIS_URL.strip() if settings.REDIS_URL else ""
            
            # Debug: Print URL info (hide password)
            print(f"[Redis Debug] URL length: {len(redis_url)}")
            print(f"[Redis Debug] URL starts with 'redis://': {redis_url.startswith('redis://')}")
            print(f"[Redis Debug] URL starts with 'rediss://': {redis_url.startswith('rediss://')}")
            if "://" in redis_url:
                scheme = redis_url.split("://")[0]
                print(f"[Redis Debug] Detected scheme: '{scheme}'")
            else:
                print(f"[Redis Debug] No scheme found in URL! First 20 chars: '{redis_url[:20]}...'")
            
            # Auto-detect Upstash and ensure TLS (rediss://) is used
            if "upstash.io" in redis_url and redis_url.startswith("redis://"):
                redis_url = redis_url.replace("redis://", "rediss://", 1)
                print(f"[Redis Debug] Converted to rediss:// for Upstash")
            
            try:
                self._redis = redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except Exception as e:
                print(f"[Redis Debug] Failed to create Redis client: {e}")
                self._redis = None
                raise
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis connection, connecting if needed"""
        if self._redis is None:
            await self.connect()
        return self._redis
    
    # ========================================
    # Token Blacklist Operations
    # ========================================
    
    async def blacklist_token(self, token: str) -> bool:
        """
        Add a refresh token to the blacklist.
        
        Args:
            token: The refresh token to blacklist
            
        Returns:
            True if successful
        """
        r = await self._get_redis()
        key = f"{self.BLACKLIST_PREFIX}{token}"
        await r.setex(key, self.BLACKLIST_TTL_SECONDS, "1")
        return True
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a refresh token is blacklisted.
        
        Args:
            token: The refresh token to check
            
        Returns:
            True if blacklisted
        """
        r = await self._get_redis()
        key = f"{self.BLACKLIST_PREFIX}{token}"
        result = await r.exists(key)
        return result > 0
    
    # ========================================
    # OAuth State Management (CSRF Protection)
    # ========================================
    
    async def store_oauth_state(self, state: str) -> bool:
        """
        Store OAuth state for CSRF protection.
        
        Args:
            state: Random state string
            
        Returns:
            True if successful
        """
        r = await self._get_redis()
        key = f"{self.OAUTH_STATE_PREFIX}{state}"
        await r.setex(key, self.OAUTH_STATE_TTL_SECONDS, "1")
        return True
    
    async def verify_and_delete_oauth_state(self, state: str) -> bool:
        """
        Verify OAuth state exists and delete it (one-time use).
        
        Args:
            state: State string to verify
            
        Returns:
            True if state was valid, False if not found or already used
        """
        r = await self._get_redis()
        key = f"{self.OAUTH_STATE_PREFIX}{state}"
        
        # Use Redis transaction to check and delete atomically
        result = await r.delete(key)
        return result > 0
    
    # ========================================
    # Health Check
    # ========================================
    
    async def ping(self) -> bool:
        """Check Redis connectivity"""
        try:
            r = await self._get_redis()
            await r.ping()
            return True
        except Exception:
            return False


# Singleton instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency to get Redis client"""
    await redis_client.connect()
    return redis_client
