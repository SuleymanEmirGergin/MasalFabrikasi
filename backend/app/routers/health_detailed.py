from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Optional
import time
import psutil
import os

router = APIRouter()

class HealthStatus(BaseModel):
    status: str
    timestamp: float
    version: str
    dependencies: Dict[str, str]
    system: Optional[Dict[str, any]] = None

@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Comprehensive health check endpoint.
    Checks all critical dependencies and system resources.
    """
    dependencies = {}
    overall_status = "healthy"
    
    # Check Redis
    try:
        from app.services.cache_service import cache_service
        if cache_service.enabled:
            cache_service.client.ping()
            dependencies["redis"] = "ok"
        else:
            dependencies["redis"] = "disabled"
    except Exception as e:
        dependencies["redis"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check OpenAI (optional - don't fail health check)
    openai_key = os.getenv("OPENAI_API_KEY")
    dependencies["openai"] = "configured" if openai_key else "not_configured"
    
    # Check Replicate
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    dependencies["replicate"] = "configured" if replicate_token else "not_configured"
    
    # System metrics
    system_info = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
    }
    
    # Determine overall health
    if system_info["cpu_percent"] > 90 or system_info["memory_percent"] > 90:
        overall_status = "degraded"
    
    return HealthStatus(
        status=overall_status,
        timestamp=time.time(),
        version=os.getenv("APP_VERSION", "1.0.0"),
        dependencies=dependencies,
        system=system_info if overall_status != "healthy" else None
    )

@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Kubernetes readiness probe.
    Returns 200 if app is ready to serve traffic.
    """
    # Check critical dependencies
    try:
        from app.services.cache_service import cache_service
        if cache_service.enabled:
            cache_service.client.ping()
    except Exception:
        return {"status": "not_ready", "reason": "redis_unavailable"}, 503
    
    return {"status": "ready"}

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe.
    Returns 200 if app is running (even if degraded).
    """
    return {"status": "alive", "timestamp": time.time()}
