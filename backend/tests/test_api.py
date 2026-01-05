import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_story_generation_validation():
    """Test story generation validates required fields"""
    response = client.post("/api/story/generate-story", json={})
    assert response.status_code == 422  # Validation error

def test_rate_limiting():
    """Test rate limiting on story generation"""
    # Make 6 requests (limit is 5/minute)
    for i in range(6):
        response = client.post("/api/story/generate-story", json={
            "theme": "test story",
            "language": "tr"
        })
        if i < 5:
            assert response.status_code in [200, 422]  # Valid or validation error
        else:
            assert response.status_code == 429  # Rate limit exceeded

@pytest.mark.asyncio
async def test_atmosphere_analysis():
    """Test atmosphere service"""
    from app.services.atmosphere_service import atmosphere_service
    
    result = await atmosphere_service.analyze_mood("The dark forest was scary")
    
    assert "color" in result
    assert "brightness" in result
    assert "mood" in result
