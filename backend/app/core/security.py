from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from typing import Dict, Tuple

# Rate limiting storage
rate_limit_store: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for API protection."""
    
    async def dispatch(self, request: Request, call_next):
        # Add security headers
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Max calls
        self.period = period  # Time period in seconds
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Check rate limit
        current_time = time.time()
        count, start_time = rate_limit_store[client_ip]
        
        # Reset if period expired
        if current_time - start_time > self.period:
            rate_limit_store[client_ip] = (1, current_time)
            return await call_next(request)
        
        # Check if limit exceeded
        if count >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Increment counter
        rate_limit_store[client_ip] = (count + 1, start_time)
        
        return await call_next(request)

# JWT Bearer for protected endpoints
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    """Dependency to get current authenticated user."""
    from app.services.auth_service import auth_service
    
    token = credentials.credentials
    user_id = auth_service.get_user_from_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id

# Input validation helpers
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    # Basic sanitization - remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

def validate_file_upload(filename: str) -> bool:
    """Validate uploaded file."""
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp3', '.wav', '.m4a'}
    import os
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

# Export
__all__ = [
    'SecurityMiddleware',
    'RateLimitMiddleware',
    'get_current_user',
    'sanitize_input',
    'validate_file_upload',
]
