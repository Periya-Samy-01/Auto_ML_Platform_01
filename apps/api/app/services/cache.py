"""
Redis Cache Service
Handles caching for dataset schemas, profiles, and job statuses
"""

import json
import logging
from typing import Any, Optional, Dict, List
from datetime import timedelta

import redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis cache operations"""
    
    def __init__(self):
        """Initialize Redis client with graceful fallback"""
        self._available = False
        self.redis_client = None
        
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,  # 2 second timeout
                socket_timeout=2
            )
            self._test_connection()
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {e}")
    
    @property
    def available(self) -> bool:
        """Check if cache is available"""
        return self._available
    
    def _test_connection(self) -> None:
        """Test Redis connection on initialization"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                self._available = True
                logger.info("Redis cache connected successfully")
        except RedisError as e:
            logger.warning(f"Redis connection failed, caching disabled: {e}")
            self._available = False
    
    # Schema Cache Operations
    def cache_schema(
        self,
        dataset_id: str,
        version_id: str,
        schema: Dict[str, Any],
        ttl: int = 86400  # 24 hours
    ) -> None:
        """Cache dataset version schema"""
        if not self._available:
            return
        key = f"dataset:{dataset_id}:version:{version_id}:schema"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(schema)
            )
            logger.debug(f"Cached schema for {key}")
        except RedisError as e:
            logger.error(f"Failed to cache schema: {e}")
    
    def get_cached_schema(
        self,
        dataset_id: str,
        version_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached dataset schema"""
        if not self._available:
            return None
        key = f"dataset:{dataset_id}:version:{version_id}:schema"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except RedisError as e:
            logger.error(f"Failed to get cached schema: {e}")
            return None
    
    # Preview Cache Operations
    def cache_preview(
        self,
        dataset_id: str,
        version_id: str,
        preview_rows: List[Dict[str, Any]],
        ttl: int = 3600  # 1 hour
    ) -> None:
        """Cache dataset preview rows"""
        if not self._available:
            return
        key = f"dataset:{dataset_id}:version:{version_id}:preview"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(preview_rows)
            )
            logger.debug(f"Cached preview for {key}")
        except RedisError as e:
            logger.error(f"Failed to cache preview: {e}")
    
    def get_cached_preview(
        self,
        dataset_id: str,
        version_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached dataset preview"""
        if not self._available:
            return None
        key = f"dataset:{dataset_id}:version:{version_id}:preview"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except RedisError as e:
            logger.error(f"Failed to get cached preview: {e}")
            return None
    
    # Profile Cache Operations
    def cache_profile(
        self,
        dataset_id: str,
        version_id: str,
        profile: Dict[str, Any],
        ttl: int = 21600  # 6 hours
    ) -> None:
        """Cache dataset statistical profile"""
        key = f"dataset:{dataset_id}:version:{version_id}:profile"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(profile)
            )
            logger.debug(f"Cached profile for {key}")
        except RedisError as e:
            logger.error(f"Failed to cache profile: {e}")
    
    def get_cached_profile(
        self,
        dataset_id: str,
        version_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached dataset profile"""
        key = f"dataset:{dataset_id}:version:{version_id}:profile"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except RedisError as e:
            logger.error(f"Failed to get cached profile: {e}")
            return None
    
    # Job Status Cache
    def cache_job_status(
        self,
        job_id: str,
        status: str,
        progress: int = 0,
        ttl: int = 3600  # 1 hour
    ) -> None:
        """Cache ingestion job status"""
        key = f"job:{job_id}:status"
        value = {
            "status": status,
            "progress": progress
        }
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
            logger.debug(f"Cached job status for {job_id}: {status}")
        except RedisError as e:
            logger.error(f"Failed to cache job status: {e}")
    
    def get_cached_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get cached job status"""
        key = f"job:{job_id}:status"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except RedisError as e:
            logger.error(f"Failed to get cached job status: {e}")
            return None
    
    # User Dataset List Cache
    def cache_user_datasets(
        self,
        user_id: str,
        page: int,
        datasets: List[Dict[str, Any]],
        ttl: int = 300  # 5 minutes
    ) -> None:
        """Cache paginated user dataset list"""
        key = f"user:{user_id}:datasets:page:{page}"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(datasets)
            )
            logger.debug(f"Cached user datasets for {user_id}, page {page}")
        except RedisError as e:
            logger.error(f"Failed to cache user datasets: {e}")
    
    def get_cached_user_datasets(
        self,
        user_id: str,
        page: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached user dataset list"""
        key = f"user:{user_id}:datasets:page:{page}"
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except RedisError as e:
            logger.error(f"Failed to get cached user datasets: {e}")
            return None
    
    # Cache Invalidation
    def invalidate_dataset_cache(self, dataset_id: str) -> None:
        """Invalidate all cache entries for a dataset"""
        pattern = f"dataset:{dataset_id}:*"
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for dataset {dataset_id}")
        except RedisError as e:
            logger.error(f"Failed to invalidate dataset cache: {e}")
    
    def invalidate_user_dataset_cache(self, user_id: str) -> None:
        """Invalidate user's dataset list cache"""
        pattern = f"user:{user_id}:datasets:*"
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated dataset list cache for user {user_id}")
        except RedisError as e:
            logger.error(f"Failed to invalidate user dataset cache: {e}")
    
    # Utility Methods
    def set_with_ttl(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> None:
        """Set a key with TTL"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                value
            )
        except RedisError as e:
            logger.error(f"Failed to set key {key}: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            return self.redis_client.get(key)
        except RedisError as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    def delete(self, key: str) -> None:
        """Delete a key"""
        try:
            self.redis_client.delete(key)
        except RedisError as e:
            logger.error(f"Failed to delete key {key}: {e}")


# Lazy singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create the cache service singleton"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


# For backward compatibility - lazy property
class _LazyCache:
    """Lazy cache service wrapper"""
    _instance: Optional[CacheService] = None
    
    def __getattr__(self, name):
        if self._instance is None:
            self._instance = CacheService()
        return getattr(self._instance, name)

cache_service = _LazyCache()

