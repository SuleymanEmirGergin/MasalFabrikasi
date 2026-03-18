"""
Response Compression Middleware
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import gzip
import io


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Compresses response bodies using gzip for responses larger than min_size
    """
    
    def __init__(self, app, min_size: int = 1000, compression_level: int = 6):
        super().__init__(app)
        self.min_size = min_size
        self.compression_level = compression_level
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # Only compress if response is large enough
        if not hasattr(response, "body"):
            return response
        
        body = response.body
        if len(body) < self.min_size:
            return response
        
        # Compress the body
        compressed_body = self._compress(body)
        
        # If compression didn't help, return original
        if len(compressed_body) >= len(body):
            return response
        
        # Return compressed response
        response.headers["content-encoding"] = "gzip"
        response.headers["content-length"] = str(len(compressed_body))
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
    
    def _compress(self, body: bytes) -> bytes:
        """Compress body using gzip"""
        buffer = io.BytesIO()
        with gzip.GzipFile(
            fileobj=buffer,
            mode="wb",
            compresslevel=self.compression_level
        ) as f:
            f.write(body)
        return buffer.getvalue()
