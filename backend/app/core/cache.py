import functools
import hashlib
import json
import logging
from typing import Callable, Any, Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
            logger.info("✅ Redis cache connection established (Async)")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        try:
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 300):
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Cache set error: {e}")

cache_service = CacheService()

def cache(expire_seconds: int = 300):
    """
    Redis-based cache decorator for FastAPI endpoints.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}:{json.dumps(kwargs, sort_keys=True)}"
            cache_key = f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_service.set(cache_key, result, expire_seconds)
            
            return result
        return wrapper
    return decorator
