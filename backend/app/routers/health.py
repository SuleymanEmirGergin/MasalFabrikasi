from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.health_check_service import HealthCheckService

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check - fast response"""
    return {
        "status": "healthy",
        "service": "Masal Fabrikası AI",
        "version": "2.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check - checks all components"""
    health_service = HealthCheckService()
    return await health_service.get_comprehensive_health(db)
