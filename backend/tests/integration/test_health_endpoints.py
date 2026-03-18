"""
Integration tests for Health API endpoints.

Tests cover:
- GET /api/health (basic)
- GET /api/health/detailed (with DB)
"""
import pytest


@pytest.mark.integration
class TestHealthEndpoints:
    """Integration tests for health endpoints."""

    def test_health_basic_returns_200(self, client):
        """GET /api/health returns 200 and healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "service" in data
        assert "version" in data
        assert "wiro_configured" in data
        assert "features" in data
        assert "ai" in data["features"]
        assert "payments" in data["features"]
        assert "storage" in data["features"]

    def test_health_detailed_returns_200(self, client):
        """GET /api/health/detailed returns 200 (uses DB)."""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data or "status" in data or "components" in data
