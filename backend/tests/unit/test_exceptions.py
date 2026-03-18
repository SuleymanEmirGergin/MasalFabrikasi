"""Unit tests for app.core.exceptions."""
import pytest

from app.core.exceptions import (
    MasalFabrikasiException,
    ValidationError,
    ResourceNotFoundError,
    AuthenticationError,
)


@pytest.mark.unit
class TestMasalFabrikasiException:
    """Tests for base exception."""

    def test_message_and_status_code(self):
        e = MasalFabrikasiException("Test error", status_code=400)
        assert str(e) == "Test error"
        assert e.message == "Test error"
        assert e.status_code == 400
        assert e.error_code == "INTERNAL_ERROR"
        assert e.details == {}

    def test_with_details(self):
        e = MasalFabrikasiException("Error", details={"key": "value"})
        assert e.details == {"key": "value"}


@pytest.mark.unit
class TestValidationError:
    """Tests for ValidationError."""

    def test_default_status_and_code(self):
        e = ValidationError("Invalid input")
        assert e.status_code == 400
        assert e.error_code == "VALIDATION_ERROR"
        assert e.message == "Invalid input"


@pytest.mark.unit
class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError."""

    def test_message_includes_resource_and_id(self):
        e = ResourceNotFoundError("Story", "abc-123")
        assert e.status_code == 404
        assert e.error_code == "RESOURCE_NOT_FOUND"
        assert "Story" in e.message
        assert "abc-123" in e.message
        assert e.details.get("resource") == "Story"
        assert e.details.get("id") == "abc-123"


@pytest.mark.unit
class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_message(self):
        e = AuthenticationError()
        assert e.status_code == 401
        assert "Authentication" in e.message

    def test_custom_message(self):
        e = AuthenticationError("Invalid token")
        assert e.message == "Invalid token"
