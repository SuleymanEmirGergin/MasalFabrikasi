import pytest
from app.services.cache_service import CacheService, cache_service

class TestCacheService:
    """Test cases for CacheService."""
    
    def test_cache_set_and_get(self, mock_redis):
        """Test basic cache set and get operations."""
        cache_service.set("test_key", {"data": "test_value"}, ttl=60)
        result = cache_service.get("test_key")
        
        if cache_service.enabled:
            assert result == {"data": "test_value"}
    
    def test_cache_miss(self, mock_redis):
        """Test cache miss returns None."""
        result = cache_service.get("nonexistent_key")
        assert result is None
    
    def test_cache_delete(self, mock_redis):
        """Test cache deletion."""
        cache_service.set("test_key", {"data": "test_value"})
        cache_service.delete("test_key")
        result = cache_service.get("test_key")
        assert result is None
    
    def test_cache_decorator(self, mock_redis):
        """Test cache decorator function."""
        call_count = 0
        
        @cache_service.cache_decorator(prefix="test_func", ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call - cache miss
        result1 = expensive_function(1, 2)
        assert result1 == 3
        first_call_count = call_count
        
        # Second call - cache hit (if enabled)
        result2 = expensive_function(1, 2)
        assert result2 == 3
        
        if cache_service.enabled:
            # Call count should not increase on cache hit
            assert call_count == first_call_count
        else:
            # Without cache, function is called again
            assert call_count == first_call_count + 1
    
    def test_generate_key(self):
        """Test cache key generation."""
        key1 = cache_service._generate_key("prefix", "arg1", "arg2", kwarg1="value1")
        key2 = cache_service._generate_key("prefix", "arg1", "arg2", kwarg1="value1")
        key3 = cache_service._generate_key("prefix", "arg1", "arg3", kwarg1="value1")
        
        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different inputs = different key
    
    def test_invalidate_pattern(self, mock_redis):
        """Test pattern-based cache invalidation."""
        cache_service.set("user:1:data", {"name": "User1"})
        cache_service.set("user:2:data", {"name": "User2"})
        cache_service.set("post:1:data", {"title": "Post1"})
        
        # Invalidate all user cache
        cache_service.invalidate_pattern("user:*")
        
        if cache_service.enabled:
            assert cache_service.get("user:1:data") is None
            assert cache_service.get("user:2:data") is None
            # Post cache should still exist
            assert cache_service.get("post:1:data") == {"title": "Post1"}
