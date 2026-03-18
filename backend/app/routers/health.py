from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.health_check_service import HealthCheckService

router = APIRouter()


def _features():
    """Optional feature flags based on env configuration (for observability)."""
    return {
        "payments": {
            "iyzico_configured": bool(settings.IYZICO_API_KEY and settings.IYZICO_SECRET_KEY),
            "stripe_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_WEBHOOK_SECRET),
        },
        "storage": {
            "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY),
        },
        "ai": {
            "wiro_configured": bool(settings.WIRO_API_KEY),
        },
    }


@router.get("/health")
async def health_check():
    """Basic health check - fast response. Includes optional feature flags."""
    features = _features()
    return {
        "status": "healthy",
        "service": "Masal Fabrikası AI",
        "version": "2.0.0",
        "wiro_configured": features["ai"]["wiro_configured"],
        "features": features,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check - checks all components"""
    health_service = HealthCheckService()
    return await health_service.get_comprehensive_health(db)
