"""
Custom Exception Classes - Merkezi hata yönetimi
"""
from typing import Optional, Dict, Any


class MasalFabrikasiException(Exception):
    """Base exception for all custom exceptions"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# Business Logic Errors
class ValidationError(MasalFabrikasiException):
    """Input validation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ResourceNotFoundError(MasalFabrikasiException):
    """Resource not found errors"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} with ID {resource_id} not found",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "id": resource_id}
        )


class AuthenticationError(MasalFabrikasiException):
    """Authentication errors"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(MasalFabrikasiException):
    """Authorization/Permission errors"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class RateLimitError(MasalFabrikasiException):
    """Rate limit exceeded"""
    def __init__(self, limit: int, window: str):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window}
        )


class ExternalServiceError(MasalFabrikasiException):
    """External API/Service errors"""
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service error ({service}): {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


class DatabaseError(MasalFabrikasiException):
    """Database operation errors"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Database error: {message}",
            status_code=500,
            error_code="DATABASE_ERROR"
        )


class ConfigurationError(MasalFabrikasiException):
    """Configuration/Setup errors"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Configuration error: {message}",
            status_code=500,
            error_code="CONFIGURATION_ERROR"
        )


# Story Generation Specific Errors
class StoryGenerationError(MasalFabrikasiException):
    """Story generation specific errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Story generation failed: {message}",
            status_code=500,
            error_code="STORY_GENERATION_ERROR",
            details=details
        )


class InsufficientCreditsError(MasalFabrikasiException):
    """User has insufficient credits"""
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Insufficient credits. Required: {required}, Available: {available}",
            status_code=402,
            error_code="INSUFFICIENT_CREDITS",
            details={"required": required, "available": available}
        )


class QuotaExceededError(MasalFabrikasiException):
    """User quota exceeded"""
    def __init__(self, quota_type: str, limit: int):
        super().__init__(
            message=f"{quota_type} quota exceeded. Limit: {limit}",
            status_code=429,
            error_code="QUOTA_EXCEEDED",
            details={"quota_type": quota_type, "limit": limit}
        )
