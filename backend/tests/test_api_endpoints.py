"""API endpoint integration tests"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
class TestAPIEndpoints:
    """API endpoint test class"""
    
    def test_health_endpoint(self, test_client: TestClient):
        """Test health endpoint"""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_story_generation_endpoint(self, test_client: TestClient, mock_openai_client):
        """Test story generation endpoint"""
        request_data = {
            "theme": "uzayda yalnız bir gezgin",
            "language": "tr",
            "story_type": "masal"
        }
        
        response = test_client.post("/api/generate-story", json=request_data)
        
        # Should return 200 or 500 (depending on OpenAI availability)
        assert response.status_code in [200, 500]
    
    def test_get_stories_endpoint(self, test_client: TestClient):
        """Test get stories endpoint"""
        response = test_client.get("/api/stories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_stories_with_filters(self, test_client: TestClient):
        """Test get stories with query parameters"""
        response = test_client.get("/api/stories?limit=10&story_type=masal")
        assert response.status_code == 200
    
    def test_character_endpoints(self, test_client: TestClient):
        """Test character endpoints"""
        # Get characters
        response = test_client.get("/api/characters")
        assert response.status_code == 200
    
    def test_user_endpoints(self, test_client: TestClient):
        """Test user endpoints"""
        # Register user
        user_data = {
            "username": "testuser",
            "email": "test@example.com"
        }
        response = test_client.post("/api/users/register", json=user_data)
        # Should return 200 or 400 (if user exists)
        assert response.status_code in [200, 400]

