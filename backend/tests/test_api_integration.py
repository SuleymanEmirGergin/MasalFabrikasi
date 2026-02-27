import pytest

@pytest.mark.integration
class TestHealthEndpoint:
    """Integration tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

@pytest.mark.integration
class TestStoryEndpoints:
    """Integration tests for story API endpoints."""
    
    def test_get_stories_empty(self, client):
        """Test getting stories when none exist."""
        response = client.get("/api/stories")
        assert response.status_code == 200
        # Response should be a list (empty or with items)
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_stories_with_filters(self, client):
        """Test story filtering."""
        response = client.get("/api/stories?favorite_only=true&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_nonexistent_story(self, client):
        """Test getting a story that doesn't exist."""
        response = client.get("/api/story/nonexistent_id")
        assert response.status_code == 404

@pytest.mark.integration
class TestCharacterEndpoints:
    """Integration tests for character API endpoints."""
    
    def test_get_characters(self, client):
        """Test getting character list."""
        response = client.get("/api/characters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_character(self, client, mock_character_data):
        """Test character creation."""
        response = client.post("/api/character", json=mock_character_data)
        
        # Should return 200 or 201
        assert response.status_code in [200, 201]
        
        if response.status_code == 200:
            data = response.json()
            assert "character_id" in data or "id" in data

@pytest.mark.integration
class TestMarketEndpoints:
    """Integration tests for market API endpoints."""
    
    def test_get_balance(self, client):
        """Test getting user balance."""
        response = client.get("/api/market/balance/test_user")
        assert response.status_code == 200
        data = response.json()
        assert "credits" in data
        assert "is_premium" in data
    
    def test_get_packages(self, client):
        """Test getting credit packages."""
        response = client.get("/api/market/packages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
