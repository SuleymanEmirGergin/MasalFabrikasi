import redis
import json
import os
from typing import Optional, Any
import hashlib

class CacheService:
    """
    Redis-based caching service for API responses and expensive operations.
    """
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.client = redis.from_url(
                redis_url, 
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            self.enabled = True
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            self.client = None
            self.enabled = False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (default 1 hour)."""
        if not self.enabled:
            return
        
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache."""
        if not self.enabled:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        if not self.enabled:
            return
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            print(f"Cache invalidate error: {e}")
    
    def cache_decorator(self, prefix: str, ttl: int = 3600):
        """Decorator for caching function results."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                # Generate cache key
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached = self.get(cache_key)
                if cached is not None:
                    print(f"✅ Cache HIT: {prefix}")
                    return cached
                
                # Execute function
                print(f"❌ Cache MISS: {prefix}")
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator

# Global instance
cache_service = CacheService()
