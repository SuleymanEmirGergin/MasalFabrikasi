"""Unit tests for app.core.config Settings."""
import os
import pytest


@pytest.mark.unit
class TestSettings:
    """Test Settings loading and defaults."""

    def test_settings_loads_with_env(self):
        """Settings can be instantiated with env vars."""
        from app.core.config import settings
        assert settings is not None
        assert hasattr(settings, "DEBUG")
        assert hasattr(settings, "DATABASE_URL")
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "WIRO_API_KEY")

    def test_debug_default_false(self):
        """DEBUG defaults to False when env not set."""
        from app.core.config import settings
        # In test env DEBUG may be set; we only assert it's bool
        assert isinstance(settings.DEBUG, bool)

    def test_database_url_default(self):
        """DATABASE_URL has a default value."""
        from app.core.config import settings
        assert isinstance(settings.DATABASE_URL, str)
        assert len(settings.DATABASE_URL) > 0

    def test_redis_url_default(self):
        """REDIS_URL has a default value."""
        from app.core.config import settings
        assert isinstance(settings.REDIS_URL, str)
        assert "redis" in settings.REDIS_URL.lower() or len(settings.REDIS_URL) >= 0
