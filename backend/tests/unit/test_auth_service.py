"""
Unit tests for AuthService

Tests cover:
- Password hashing and verification
- Token creation and verification
- User authentication logic
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import jwt
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mock heavy dependencies before importing
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

from app.services.auth_service import AuthService, pwd_context


class TestPasswordHashing:
    """Tests for password hashing functionality."""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_hash_password(self):
        """Test that password hashing works correctly."""
        password = "secure_password_123"
        hashed = self.auth_service.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salting)."""
        password = "secure_password_123"
        hash1 = self.auth_service.hash_password(password)
        hash2 = self.auth_service.hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "secure_password_123"
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "secure_password_123"
        wrong_password = "wrong_password"
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "secure_password_123"
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password("", hashed)
        
        assert result is False


class TestTokenCreation:
    """Tests for JWT token creation."""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test_user_id"}
        
        token = self.auth_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test access token with custom expiry."""
        data = {"sub": "test_user_id"}
        expires_delta = timedelta(hours=1)
        
        token = self.auth_service.create_access_token(data, expires_delta)
        
        # Decode and verify expiry
        decoded = jwt.decode(
            token, 
            self.auth_service.secret_key, 
            algorithms=[self.auth_service.algorithm]
        )
        
        assert "exp" in decoded
        assert "sub" in decoded
        assert decoded["sub"] == "test_user_id"
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user_id = "test_user_id"
        
        token = self.auth_service.create_refresh_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0


class TestTokenVerification:
    """Tests for JWT token verification."""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_verify_token_valid(self):
        """Test verification of a valid token."""
        user_id = "test_user_id"
        token = self.auth_service.create_access_token({"sub": user_id})
        
        result = self.auth_service.verify_token(token)
        
        assert result == user_id
    
    def test_verify_token_expired(self):
        """Test verification of an expired token."""
        user_id = "test_user_id"
        # Create token that expires immediately
        token = self.auth_service.create_access_token(
            {"sub": user_id}, 
            expires_delta=timedelta(seconds=-1)
        )
        
        result = self.auth_service.verify_token(token)
        
        assert result is None
    
    def test_verify_token_invalid(self):
        """Test verification of an invalid token."""
        invalid_token = "invalid.token.here"
        
        result = self.auth_service.verify_token(invalid_token)
        
        assert result is None
    
    def test_verify_token_tampered(self):
        """Test verification of a tampered token."""
        user_id = "test_user_id"
        token = self.auth_service.create_access_token({"sub": user_id})
        
        # Tamper with the token
        tampered_token = token[:-5] + "xxxxx"
        
        result = self.auth_service.verify_token(tampered_token)
        
        assert result is None
    
    def test_verify_refresh_token_valid(self):
        """Test verification of a valid refresh token."""
        user_id = "test_user_id"
        refresh_token = self.auth_service.create_refresh_token(user_id)
        
        result = self.auth_service.verify_refresh_token(refresh_token)
        
        assert result == user_id
    
    def test_verify_refresh_token_invalid(self):
        """Test verification of an invalid refresh token."""
        result = self.auth_service.verify_refresh_token("invalid_token")
        
        assert result is None


class TestUserAuthentication:
    """Tests for user authentication."""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        email = "test@example.com"
        password = "secure_password_123"
        hashed_password = self.auth_service.hash_password(password)
        
        # Mock user from database
        mock_user = MagicMock()
        mock_user.password_hash = hashed_password
        mock_user.email = email
        mock_user.id = "user_123"
        
        with patch.object(
            self.auth_service, 
            'get_user_by_email', 
            new_callable=AsyncMock,
            return_value=mock_user
        ):
            result = await self.auth_service.authenticate_user(email, password)
            
            assert result is not None
            assert result.email == email
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        email = "test@example.com"
        password = "secure_password_123"
        wrong_password = "wrong_password"
        hashed_password = self.auth_service.hash_password(password)
        
        mock_user = MagicMock()
        mock_user.password_hash = hashed_password
        
        with patch.object(
            self.auth_service, 
            'get_user_by_email', 
            new_callable=AsyncMock,
            return_value=mock_user
        ):
            result = await self.auth_service.authenticate_user(email, wrong_password)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        with patch.object(
            self.auth_service, 
            'get_user_by_email', 
            new_callable=AsyncMock,
            return_value=None
        ):
            result = await self.auth_service.authenticate_user(
                "nonexistent@example.com", 
                "password"
            )
            
            assert result is None


class TestTokenBlacklisting:
    """Tests for token blacklisting."""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_blacklist_token(self):
        """Test adding token to blacklist."""
        token = self.auth_service.create_access_token({"sub": "user_123"})
        
        # Should not raise any exception
        self.auth_service.blacklist_token(token)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def setup_method(self):
        self.auth_service = AuthService()
    
    def test_hash_empty_password(self):
        """Test hashing an empty password."""
        # Should work, though not recommended
        hashed = self.auth_service.hash_password("")
        assert hashed is not None
    
    def test_hash_long_password(self):
        """Test hashing a very long password."""
        long_password = "a" * 1000
        hashed = self.auth_service.hash_password(long_password)
        assert hashed is not None
        assert self.auth_service.verify_password(long_password, hashed)
    
    def test_hash_unicode_password(self):
        """Test hashing a password with unicode characters."""
        unicode_password = "şifre_çok_güçlü_123"
        hashed = self.auth_service.hash_password(unicode_password)
        assert hashed is not None
        assert self.auth_service.verify_password(unicode_password, hashed)
    
    def test_create_token_with_special_chars_in_user_id(self):
        """Test token creation with special characters in user ID."""
        user_id = "user@example.com/special:chars"
        token = self.auth_service.create_access_token({"sub": user_id})
        
        result = self.auth_service.verify_token(token)
        
        assert result == user_id
