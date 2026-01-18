from fastapi import APIRouter, Response, status
from sqlalchemy import text
from app.core.database import get_db_context
from app.core.cache import cache_service
from app.core.config import settings
import time

router = APIRouter()

@router.get("/health/live")
async def liveness_probe():
    """
    K8s Liveness Probe: Service is running.
    Does NOT check dependencies.
    """
    return {"status": "ok", "service": "Masal Fabrikası AI", "version": settings.APP_VERSION}

@router.get("/health/ready")
async def readiness_probe(response: Response):
    """
    K8s Readiness Probe: Service handles traffic.
    Checks DB and Redis connections.
    """
    checks = {
        "database": False,
        "redis": False
    }

    # Check Database
    try:
        start_time = time.time()
        async with get_db_context() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = True
        checks["database_latency_ms"] = int((time.time() - start_time) * 1000)
    except Exception as e:
        checks["database_error"] = str(e)

    # Check Redis
    try:
        start_time = time.time()
        if cache_service.redis_client:
            await cache_service.redis_client.ping()
            checks["redis"] = True
            checks["redis_latency_ms"] = int((time.time() - start_time) * 1000)
        else:
            checks["redis_error"] = "Client not initialized"
    except Exception as e:
        checks["redis_error"] = str(e)

    all_healthy = all([checks["database"], checks["redis"]])

    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": time.time()
    }
