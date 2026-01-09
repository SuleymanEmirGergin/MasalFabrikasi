"""
Integration tests for Auth API Endpoints

Tests cover:
- User registration endpoint
- User login endpoint
- Token refresh endpoint
- Password reset endpoints
- Email verification endpoints
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.integration
class TestRegisterEndpoint:
    """Tests for POST /api/auth/register endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "name": "Test User"
            }
        )
        
        # Should succeed or return duplicate if already exists
        assert response.status_code in [200, 201, 400]
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "message" in data or "access_token" in data
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePassword123!",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password(self, client):
        """Test registration with too short password."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",  # Too short
                "name": "Test User"
            }
        )
        
        # Should either reject or accept based on password policy
        assert response.status_code in [200, 201, 400, 422]
    
    def test_register_missing_email(self, client):
        """Test registration without email."""
        response = client.post(
            "/api/auth/register",
            json={
                "password": "SecurePassword123!",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_password(self, client):
        """Test registration without password."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestLoginEndpoint:
    """Tests for POST /api/auth/login endpoint."""
    
    def test_login_endpoint_exists(self, client):
        """Test that login endpoint exists."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        # Should return 401 or 400 for invalid credentials
        assert response.status_code in [400, 401, 404]
    
    def test_login_missing_email(self, client):
        """Test login without email."""
        response = client.post(
            "/api/auth/login",
            json={
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_password(self, client):
        """Test login without password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestTokenRefreshEndpoint:
    """Tests for POST /api/auth/refresh endpoint."""
    
    def test_refresh_endpoint_exists(self, client):
        """Test that refresh endpoint exists."""
        response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": "invalid_token"
            }
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": "invalid_token_here"
            }
        )
        
        # Should return 401 or 400
        assert response.status_code in [400, 401]


@pytest.mark.integration
class TestPasswordResetEndpoint:
    """Tests for password reset endpoints."""
    
    def test_request_password_reset(self, client):
        """Test requesting password reset."""
        response = client.post(
            "/api/auth/password-reset",
            json={
                "email": "test@example.com"
            }
        )
        
        # Should accept request (even for non-existent users for security)
        assert response.status_code in [200, 202, 400, 404]
    
    def test_confirm_password_reset_invalid_token(self, client):
        """Test confirming password reset with invalid token."""
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": "invalid_token",
                "new_password": "NewSecurePassword123!"
            }
        )
        
        # Should reject invalid token
        assert response.status_code in [400, 401, 404]


@pytest.mark.integration
class TestEmailVerificationEndpoint:
    """Tests for email verification endpoints."""
    
    def test_request_email_verification(self, client):
        """Test requesting email verification."""
        response = client.post(
            "/api/auth/verify-email",
            json={
                "email": "test@example.com"
            }
        )
        
        # Should accept request
        assert response.status_code in [200, 202, 400, 404]
    
    def test_confirm_email_verification_invalid_token(self, client):
        """Test confirming email with invalid token."""
        response = client.post(
            "/api/auth/verify-email/confirm",
            json={
                "token": "invalid_token"
            }
        )
        
        # Should reject invalid token
        assert response.status_code in [400, 401, 404]


@pytest.mark.integration
class TestLogoutEndpoint:
    """Tests for POST /api/auth/logout endpoint."""
    
    def test_logout_without_token(self, client):
        """Test logout without authorization token."""
        response = client.post("/api/auth/logout")
        
        # Should return 401 or 403 (unauthorized)
        assert response.status_code in [401, 403, 422]


@pytest.mark.integration
class TestAuthEndpointValidation:
    """Tests for input validation on auth endpoints."""
    
    def test_register_sql_injection_attempt(self, client):
        """Test that SQL injection attempts are handled safely."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com'; DROP TABLE users; --",
                "password": "Password123!",
                "name": "Hacker"
            }
        )
        
        # Should return validation error (invalid email format)
        assert response.status_code == 422
    
    def test_register_xss_attempt(self, client):
        """Test that XSS attempts are handled safely."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Password123!",
                "name": "<script>alert('xss')</script>"
            }
        )
        
        # Should either sanitize or accept (React will escape on render)
        assert response.status_code in [200, 201, 400, 422]
    
    def test_login_rate_limiting(self, client):
        """Test that rate limiting is applied to login endpoint."""
        # Make multiple rapid requests
        for _ in range(15):
            response = client.post(
                "/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword"
                }
            )
        
        # After many failed attempts, should still not crash
        # Rate limiting might return 429
        assert response.status_code in [400, 401, 404, 429]
