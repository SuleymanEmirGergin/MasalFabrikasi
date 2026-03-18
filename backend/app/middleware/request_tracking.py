"""
Request Tracking Middleware - Her isteğe unique ID atar
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uuid
import time


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Adds request ID and timing to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Track request start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request (in production, use proper logging)
        print(f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
        
        return response
