"""
Metrics endpoint - Expose Prometheus metrics
"""
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.metrics import registry

router = APIRouter()


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    
    Exposes application metrics in Prometheus format
    """
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )
