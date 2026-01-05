"""
Enhanced Health Check Service - Comprehensive health monitoring
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
import redis
from datetime import datetime

from app.core.config import settings


class HealthCheckService:
    """Comprehensive health check for all system components"""
    
    @staticmethod
    async def check_database(db: Session) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # Simple ping query
            db.execute(text("SELECT 1"))
            
            # Get database size (PostgreSQL specific)
            result = db.execute(text(
                "SELECT pg_database_size(current_database()) as size"
            )).fetchone()
            
            db_size_mb = result[0] / (1024 * 1024) if result else 0
            
            return {
                "status": "healthy",
                "latency_ms": 0,  # TODO: Measure actual latency
                "size_mb": round(db_size_mb, 2)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            
            # Ping Redis
            redis_client.ping()
            
            # Get info
            info = redis_client.info()
            
            return {
                "status": "healthy",
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    async def check_celery() -> Dict[str, Any]:
        """Check Celery worker status"""
        try:
            from app.celery_app import celery_app
            
            # Get active workers
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            
            if not active_workers:
                return {
                    "status": "warning",
                    "message": "No active workers found"
                }
            
            worker_count = len(active_workers)
            
            return {
                "status": "healthy",
                "active_workers": worker_count,
                "worker_names": list(active_workers.keys())
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @staticmethod
    async def check_disk_space() -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage("/")
            
            free_gb = free / (1024 ** 3)
            total_gb = total / (1024 ** 3)
            used_percent = (used / total) * 100
            
            status = "healthy"
            if used_percent > 90:
                status = "critical"
            elif used_percent > 80:
                status = "warning"
            
            return {
                "status": status,
                "total_gb": round(total_gb, 2),
                "free_gb": round(free_gb, 2),
                "used_percent": round(used_percent, 2)
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    @staticmethod
    async def get_comprehensive_health(db: Session) -> Dict[str, Any]:
        """Get comprehensive health status of all components"""
        
        database_health = await HealthCheckService.check_database(db)
        redis_health = await HealthCheckService.check_redis()
        celery_health = await HealthCheckService.check_celery()
        disk_health = await HealthCheckService.check_disk_space()
        
        # Determine overall status
        all_statuses = [
            database_health.get("status"),
            redis_health.get("status"),
            celery_health.get("status"),
            disk_health.get("status")
        ]
        
        if "unhealthy" in all_statuses or "critical" in all_statuses:
            overall_status = "unhealthy"
        elif "warning" in all_statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "components": {
                "database": database_health,
                "redis": redis_health,
                "celery": celery_health,
                "disk": disk_health
            }
        }
