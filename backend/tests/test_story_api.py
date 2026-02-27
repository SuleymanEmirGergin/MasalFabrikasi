"""
Integration Tests for Story API
"""
import pytest


@pytest.mark.integration
class TestStoryAPI:
    """Integration tests for story endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_stories_empty(self, client, sample_user_id):
        """Test getting stories when none exist"""
        response = client.get(f"/api/stories?user_id={sample_user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data
    
    def test_create_story_validation(self, client):
        """Test story creation with invalid data"""
        response = client.post(
            "/api/generate-story",
            json={"theme": ""}  # Invalid: empty theme
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
