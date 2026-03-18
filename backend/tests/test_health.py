"""Health check endpoint tests"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
@pytest.mark.api
def test_health_check(test_client: TestClient):
    """Test health check endpoint"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.unit
@pytest.mark.api
def test_root_endpoint(test_client: TestClient):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

