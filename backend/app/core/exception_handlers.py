"""
Exception Handler Middleware - Merkezi hata yönetimi
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import uuid
from datetime import datetime
from typing import Union

from app.core.exceptions import MasalFabrikasiException
from app.core.config import settings


async def masalfabrikasi_exception_handler(
    request: Request,
    exc: MasalFabrikasiException
) -> JSONResponse:
    """Custom exception handler"""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    
    error_response = {
        "success": False,
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # In development, add stack trace
    if settings.DEBUG:
        error_response["error"]["trace"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    
    # Format validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"validation_errors": errors},
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    
    error_response = {
        "success": False,
        "error": {
            "code": "HTTP_ERROR",
            "message": exc.detail,
            "details": {},
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    
    error_response = {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # In development, show actual error
    if settings.DEBUG:
        error_response["error"]["message"] = str(exc)
        error_response["error"]["trace"] = traceback.format_exc()
    
    # Log the error
    print(f"[ERROR] Request ID: {request_id}")
    print(f"[ERROR] {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )
