import pytest
from app.services.auth_service import AuthService
from app.services.stripe_service import StripeService
from app.models import PasswordResetToken, ProcessedStripeEvent
from app.core.config import settings
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_security_jwt_algorithm_enforcement():
    """Regression Test: Reject JWT alg != HS256"""
    auth_service = AuthService()

    # Create a token with "none" algorithm
    unsafe_token = jwt.encode({"sub": "user_123"}, key=None, algorithm="none")

    # AuthService should reject it
    result = await auth_service.verify_token(unsafe_token)
    assert result is None

@pytest.mark.asyncio
async def test_security_token_hashing():
    """Regression Test: Tokens must be stored hashed"""
    auth_service = AuthService()
    plain_token = "my-secret-token"

    # Mock DB session
    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        await auth_service.create_password_reset_token("user_123", plain_token)

        # Verify that what was added to DB is NOT the plain token
        args, _ = mock_session.add.call_args
        token_obj = args[0]
        assert isinstance(token_obj, PasswordResetToken)
        assert token_obj.token_hash != plain_token
        assert len(token_obj.token_hash) == 64 # SHA256 hex digest

@pytest.mark.asyncio
async def test_security_token_reuse_prevention():
    """Regression Test: Token reuse rejected after consumed_at"""
    auth_service = AuthService()

    mock_session = AsyncMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    # Simulate a token that is already consumed
    mock_token = MagicMock()
    mock_token.consumed_at = datetime.utcnow()
    mock_token.expires_at = datetime.utcnow() + timedelta(hours=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_token
    mock_session.execute.return_value = mock_result

    with patch("app.services.auth_service.AsyncSessionLocal", return_value=mock_session_cm):
        result = await auth_service.reset_password_with_token("some-token", "new-pass")
        assert result is False

@pytest.mark.asyncio
async def test_security_log_redaction():
    """Regression Test: Redaction applies to logs"""
    from app.core.logging_config import SensitiveDataFilter
    import logging

    log_filter = SensitiveDataFilter()

    # Test dictionary args redaction
    # Pass args as a dict directly, simulating `logger.info("msg", {"password": "..."})`
    # LogRecord(name, level, pathname, lineno, msg, args, exc_info, func=None, sinfo=None)
    args = {"password": "secret_password"}
    record = logging.LogRecord("name", logging.INFO, "path", 10, "msg", args, None)
    log_filter.filter(record)
    assert record.args["password"] == "***REDACTED***"

    # Test token key redaction
    args = {"auth_token": "secret_token"}
    record = logging.LogRecord("name", logging.INFO, "path", 10, "msg", args, None)
    log_filter.filter(record)
    assert record.args["auth_token"] == "***REDACTED***"
