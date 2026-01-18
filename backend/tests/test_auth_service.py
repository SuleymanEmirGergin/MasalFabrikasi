import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.models import User, PasswordResetToken

@pytest.mark.asyncio
async def test_register_user_success():
    auth_service = AuthService()

    # Mock get_user_by_email to return None (user doesn't exist)
    auth_service.get_user_by_email = AsyncMock(return_value=None)

    # Mock AsyncSessionLocal
    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        user_data = await auth_service.register_user("test@example.com", "password123", "Test User")

        assert user_data["email"] == "test@example.com"
        assert user_data["name"] == "Test User"
        assert "password_hash" in user_data

        # Verify session calls
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_register_user_existing_email():
    auth_service = AuthService()

    # Mock get_user_by_email to return a user
    auth_service.get_user_by_email = AsyncMock(return_value={"id": "123", "email": "test@example.com"})

    with pytest.raises(ValueError, match="Bu email adresi zaten kayıtlı"):
        await auth_service.register_user("test@example.com", "password123")

@pytest.mark.asyncio
async def test_authenticate_user_success():
    auth_service = AuthService()

    # Mock password verification
    auth_service.verify_password = MagicMock(return_value=True)

    # Mock get_user_by_email
    user_data = {"id": "123", "email": "test@example.com", "password_hash": "hashed_pw"}
    auth_service.get_user_by_email = AsyncMock(return_value=user_data)

    result = await auth_service.authenticate_user("test@example.com", "password123")
    assert result == user_data

@pytest.mark.asyncio
async def test_authenticate_user_failure():
    auth_service = AuthService()

    # Mock get_user_by_email to return None
    auth_service.get_user_by_email = AsyncMock(return_value=None)

    result = await auth_service.authenticate_user("wrong@example.com", "password")
    assert result is None

@pytest.mark.asyncio
async def test_create_password_reset_token():
    auth_service = AuthService()

    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        await auth_service.create_password_reset_token("user-uuid", "reset-token")

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
