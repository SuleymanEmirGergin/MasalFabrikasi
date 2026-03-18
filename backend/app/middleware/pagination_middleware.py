"""
API Pagination Middleware
Enforces pagination limits on all list endpoints to prevent performance issues
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# Maximum items per page
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

class PaginationEnforcementMiddleware(BaseHTTPMiddleware):
    """
    Enforces pagination limits on all GET requests that return lists.
    Prevents users from requesting thousands of items at once.
    """
    
    async def dispatch(self, request: Request, call_next):
        if request.method == "GET":
            # Check for limit/page_size query parameters
            query_params = dict(request.query_params)
            
            limit = query_params.get("limit")
            page_size = query_params.get("page_size")
            
            # Check and enforce limit
            if limit:
                try:
                    limit_val = int(limit)
                    if limit_val > MAX_PAGE_SIZE:
                        logger.warning(f"Requested limit {limit_val} exceeds max {MAX_PAGE_SIZE}")
                        return HTTPException(
                            status_code=400,
                            detail=f"Limit cannot exceed {MAX_PAGE_SIZE}"
                        )
                except ValueError:
                    pass
            
            # Check and enforce page_size
            if page_size:
                try:
                    page_size_val = int(page_size)
                    if page_size_val > MAX_PAGE_SIZE:
                        logger.warning(f"Requested page_size {page_size_val} exceeds max {MAX_PAGE_SIZE}")
                        return HTTPException(
                            status_code=400,
                            detail=f"Page size cannot exceed {MAX_PAGE_SIZE}"
                        )
                except ValueError:
                    pass
        
        response = await call_next(request)
        return response
