"""
Cache Service for Workers
Redis caching operations for worker tasks
"""

import os
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import timedelta

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheService:
    """Cache service for worker operations"""
    
    def __init__(self):
        """Initialize Redis client from environment"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(
            redis_url,
            decode_responses=True
        )
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test Redis connection"""
        try:
            self.redis_client.ping()
            logger.info("Redis cache connected")
        except RedisError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def cache_job_status(
        self,
        job_id: str,
        status: str,
        progress: int = 0,
        ttl: int = 3600
    ) -> None:
        """Cache job status and progress"""
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
            logger.debug(f"Cached job status: {job_id} -> {status} ({progress}%)")
        except RedisError as e:
            logger.error(f"Failed to cache job status: {e}")
    
    def cache_schema(
        self,
        dataset_id: str,
        version_id: str,
        schema: Dict[str, Any],
        ttl: int = 86400
    ) -> None:
        """Cache dataset schema"""
        key = f"dataset:{dataset_id}:version:{version_id}:schema"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(schema)
            )
            logger.debug(f"Cached schema for dataset {dataset_id} version {version_id}")
        except RedisError as e:
            logger.error(f"Failed to cache schema: {e}")
    
    def cache_preview(
        self,
        dataset_id: str,
        version_id: str,
        preview_rows: List[Dict[str, Any]],
        ttl: int = 3600
    ) -> None:
        """Cache dataset preview rows"""
        key = f"dataset:{dataset_id}:version:{version_id}:preview"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(preview_rows)
            )
            logger.debug(f"Cached preview for dataset {dataset_id} version {version_id}")
        except RedisError as e:
            logger.error(f"Failed to cache preview: {e}")
    
    def cache_profile(
        self,
        dataset_id: str,
        version_id: str,
        profile: Dict[str, Any],
        ttl: int = 21600
    ) -> None:
        """Cache dataset profile"""
        key = f"dataset:{dataset_id}:version:{version_id}:profile"
        try:
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(profile)
            )
            logger.debug(f"Cached profile for dataset {dataset_id} version {version_id}")
        except RedisError as e:
            logger.error(f"Failed to cache profile: {e}")
    
    def invalidate_dataset_cache(self, dataset_id: str) -> None:
        """Invalidate all cache entries for a dataset"""
        pattern = f"dataset:{dataset_id}:*"
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for dataset {dataset_id}")
        except RedisError as e:
            logger.error(f"Failed to invalidate cache: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        try:
            return self.redis_client.get(key)
        except RedisError as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    def set_with_ttl(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> None:
        """Set key with TTL"""
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
