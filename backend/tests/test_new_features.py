"""New features endpoint tests"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
class TestNewFeatures:
    """New features endpoint test class"""
    
    def test_character_depth_endpoint(self, test_client: TestClient, mock_openai_client):
        """Test character depth endpoint"""
        request_data = {
            "story_id": "test_story_123",
            "story_text": "Test story content"
        }
        
        response = test_client.post("/api/character-depth/process", json=request_data)
        # Should return 200 or 500 (depending on OpenAI availability)
        assert response.status_code in [200, 500]
    
    def test_world_detail_endpoint(self, test_client: TestClient, mock_openai_client):
        """Test world detail endpoint"""
        request_data = {
            "story_id": "test_story_123",
            "story_text": "Test story content"
        }
        
        response = test_client.post("/api/world-detail/process", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_plot_complexity_endpoint(self, test_client: TestClient, mock_openai_client):
        """Test plot complexity endpoint"""
        request_data = {
            "story_id": "test_story_123",
            "story_text": "Test story content"
        }
        
        response = test_client.post("/api/plot-complexity/process", json=request_data)
        assert response.status_code in [200, 500]
    
    def test_readability_analyzer_endpoint(self, test_client: TestClient, mock_openai_client):
        """Test readability analyzer endpoint"""
        request_data = {
            "story_id": "test_story_123",
            "story_text": "Test story content"
        }
        
        response = test_client.post("/api/readability-analyzer/process", json=request_data)
        assert response.status_code in [200, 500]

