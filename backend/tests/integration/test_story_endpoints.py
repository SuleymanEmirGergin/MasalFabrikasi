"""
Integration tests for Story API endpoints (read-only / list endpoints).

Tests cover:
- GET /api/stories
- GET /api/templates
- GET /api/languages
- GET /api/stories/stats/summary
"""
import pytest


@pytest.mark.integration
class TestStoryListEndpoints:
    """Integration tests for story list and config endpoints."""

    def test_get_stories_returns_list(self, client):
        """GET /api/stories returns 200 and a list."""
        response = client.get("/api/stories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_stories_with_limit(self, client):
        """GET /api/stories?limit=5 returns at most 5 items."""
        response = client.get("/api/stories?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_templates_returns_list(self, client):
        """GET /api/templates returns 200 and a list."""
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_languages_returns_list(self, client):
        """GET /api/languages returns 200 and a list."""
        response = client.get("/api/languages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_stories_stats_summary(self, client):
        """GET /api/stories/stats/summary returns 200."""
        response = client.get("/api/stories/stats/summary")
        assert response.status_code in [200, 401, 403]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
