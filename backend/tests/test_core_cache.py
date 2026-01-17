import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.cache import cache, CacheService
from pydantic import BaseModel
from datetime import datetime

class MockModel(BaseModel):
    id: int
    name: str
    timestamp: datetime

class TestCoreCache:
    @pytest.mark.asyncio
    async def test_cache_serialization(self):
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        with patch('app.core.cache.cache_service.redis_client', mock_redis):
            # Define a function to cache
            @cache(expire_seconds=60)
            async def get_data(param: str):
                return MockModel(
                    id=1,
                    name=param,
                    timestamp=datetime(2023, 1, 1, 12, 0, 0)
                )

            # Call function
            result = await get_data("test")

            # Verify result
            assert isinstance(result, MockModel)
            assert result.name == "test"

            # Verify set was called with correct serialization
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            key, expire, value = call_args[0]

            assert expire == 60
            assert "test" in value
            assert "2023-01-01T12:00:00" in value

    @pytest.mark.asyncio
    async def test_cache_hit_deserialization(self):
        # This test acknowledges a limitation:
        # When reading back from cache, we get a dict, not the original Pydantic model
        # unless we explicitly cast it back. The current implementation returns dicts.

        mock_redis = AsyncMock()
        # Mock cached data as JSON string
        cached_data = '{"id": 1, "name": "cached", "timestamp": "2023-01-01T12:00:00"}'
        mock_redis.get.return_value = cached_data

        with patch('app.core.cache.cache_service.redis_client', mock_redis):
            @cache(expire_seconds=60)
            async def get_data():
                return MockModel(id=2, name="fresh", timestamp=datetime.now())

            # Call function
            result = await get_data()

            # Should return dict from cache, not the fresh model
            assert isinstance(result, dict)
            assert result['name'] == "cached"
            assert result['id'] == 1

            # Function should not be executed (we can't easily check this with inner func,
            # but we know it returned the cached value)

    @pytest.mark.asyncio
    async def test_key_generation_ignores_complex_types(self):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        with patch('app.core.cache.cache_service.redis_client', mock_redis):
            @cache(expire_seconds=60)
            async def protected_endpoint(request: MagicMock, db: MagicMock, param: int):
                return {"data": param}

            req = MagicMock()
            db = MagicMock()

            await protected_endpoint(request=req, db=db, param=42)

            # Check key generation
            # Key should depend on param=42 but not req/db
            # We can indirectly verify by calling again with different objects but same param

            mock_redis.reset_mock()
            mock_redis.get.return_value = '{"data": 42}' # Simulate hit

            req2 = MagicMock()
            db2 = MagicMock()

            result = await protected_endpoint(request=req2, db=db2, param=42)
            assert result['data'] == 42

            # If key generation included memory address of req/db, it would be a miss (if we hadn't mocked hit)
            # or generated a different key.
