import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.models import User, PasswordResetToken

@pytest.mark.asyncio
async def test_register_user_success():
    auth_service = AuthService()
    auth_service.get_user_by_email = AsyncMock(return_value=None)

    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        user_data = await auth_service.register_user("test@example.com", "password123", "Test User")
        assert user_data["email"] == "test@example.com"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_register_user_existing_email():
    auth_service = AuthService()
    auth_service.get_user_by_email = AsyncMock(return_value={"id": "123", "email": "test@example.com"})
    with pytest.raises(ValueError, match="Bu email adresi zaten kayıtlı"):
        await auth_service.register_user("test@example.com", "password123")

@pytest.mark.asyncio
async def test_authenticate_user_success():
    auth_service = AuthService()
    auth_service.verify_password = MagicMock(return_value=True)
    user_data = {"id": "123", "email": "test@example.com", "password_hash": "hashed_pw"}
    auth_service.get_user_by_email = AsyncMock(return_value=user_data)
    result = await auth_service.authenticate_user("test@example.com", "password123")
    assert result == user_data

@pytest.mark.asyncio
async def test_authenticate_user_failure():
    auth_service = AuthService()
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

    # Mock update execution
    mock_session.execute.return_value = None

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        await auth_service.create_password_reset_token("user-uuid", "reset-token")

        # Should execute update to invalidate old tokens
        assert mock_session.execute.called
        # Should add new token
        mock_session.add.assert_called_once()
        # Verify hashing
        args, _ = mock_session.add.call_args
        token_obj = args[0]
        assert token_obj.token_hash != "reset-token"  # Should be hashed
        assert len(token_obj.token_hash) == 64  # SHA256 hex digest length

@pytest.mark.asyncio
async def test_reset_password_with_token_success():
    auth_service = AuthService()

    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    # Mock token lookup
    mock_token = MagicMock()
    mock_token.user_id = "user-uuid"
    mock_token.expires_at = datetime.utcnow() + timedelta(hours=1)
    mock_token.consumed_at = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_token
    mock_session.execute.return_value = mock_result

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        result = await auth_service.reset_password_with_token("valid-token", "new-password")

        assert result is True
        # Should update user
        assert mock_session.execute.call_count >= 2
        # Should mark consumed
        assert mock_token.consumed_at is not None
        mock_session.add.assert_called_with(mock_token)
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_reset_password_with_consumed_token():
    auth_service = AuthService()

    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    mock_token = MagicMock()
    mock_token.consumed_at = datetime.utcnow()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_token
    mock_session.execute.return_value = mock_result

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        result = await auth_service.reset_password_with_token("consumed-token", "new-password")
        assert result is False
