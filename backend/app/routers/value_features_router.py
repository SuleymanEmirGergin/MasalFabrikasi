"""
Cost-Free Features Router - Maliyet artırmayan özellikler için tek router
Analytics, achievements, organization, scheduling, parental
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.services.reading_analytics_service import ReadingAnalyticsService
from app.services.advanced_achievement_service import AdvancedAchievementService
from app.services.story_organization_service import StoryOrganizationService
from app.services.story_scheduling_service import StorySchedulingService
from app.services.enhanced_parental_service import EnhancedParentalService

router = APIRouter()


# ==================== READING ANALYTICS ====================

@router.get("/analytics/stats/{user_id}")
async def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """Kullanıcı okuma istatistikleri"""
    try:
        service = ReadingAnalyticsService(db)
        return service.get_reading_stats(uuid.UUID(user_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard/{user_id}")
async def get_analytics_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Tam analytics dashboard"""
    try:
        service = ReadingAnalyticsService(db)
        user_uuid = uuid.UUID(user_id)
        
        return {
            "stats": service.get_reading_stats(user_uuid),
            "distribution": service.get_reading_distribution(user_uuid),
            "goals": service.get_reading_goals(user_uuid),
            "insights": service.get_reading_insights(user_uuid)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ACHIEVEMENTS ====================

@router.get("/achievements/all")
async def get_all_achievements(db: Session = Depends(get_db)):
    """Tüm mevcut başarılar"""
    try:
        service = AdvancedAchievementService(db)
        return {"achievements": service.get_all_achievements()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/achievements/user/{user_id}")
async def get_user_achievements(user_id: str, db: Session = Depends(get_db)):
    """Kullanıcının başarıları"""
    try:
        service = AdvancedAchievementService(db)
        return service.get_user_achievements(uuid.UUID(user_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/achievements/check/{user_id}")
async def check_achievements(user_id: str, db: Session = Depends(get_db)):
    """Yeni başarıları kontrol et ve unlock et"""
    try:
        service = AdvancedAchievementService(db)
        newly_unlocked = service.check_and_unlock_achievements(uuid.UUID(user_id))
        return {
            "newly_unlocked": newly_unlocked,
            "count": len(newly_unlocked)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ORGANIZATION ====================

@router.get("/organization/tags")
async def get_all_tags(db: Session = Depends(get_db)):
    """Tüm tag'leri listele"""
    try:
        service = StoryOrganizationService(db)
        return {"tags": service.get_all_tags()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organization/smart-filters/{user_id}")
async def get_smart_filters(user_id: str, db: Session = Depends(get_db)):
    """Akıllı filtreler"""
    try:
        service = StoryOrganizationService(db)
        return service.get_smart_filters(uuid.UUID(user_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CollectionRequest(BaseModel):
    name: str
    description: str = ""
    story_ids: List[str] = []


@router.post("/organization/collections")
async def create_collection(
    user_id: str,
    request: CollectionRequest,
    db: Session = Depends(get_db)
):
    """Özel koleksiyon oluştur"""
    try:
        service = StoryOrganizationService(db)
        return service.create_custom_collection(
            user_id=uuid.UUID(user_id),
            name=request.name,
            description=request.description,
            story_ids=request.story_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SCHEDULING ====================

@router.get("/scheduling/presets")
async def get_scheduling_presets(db: Session = Depends(get_db)):
    """Hazır okuma rutinleri"""
    try:
        service = StorySchedulingService(db)
        return {"presets": service.get_preset_routines()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScheduleRequest(BaseModel):
    name: str
    days_of_week: List[int]
    time_of_day: str
    story_preference: Optional[str] = None


@router.post("/scheduling/create")
async def create_schedule(
    user_id: str,
    request: ScheduleRequest,
    db: Session = Depends(get_db)
):
    """Yeni okuma programı oluştur"""
    try:
        service = StorySchedulingService(db)
        return service.create_schedule(
            user_id=uuid.UUID(user_id),
            name=request.name,
            days_of_week=request.days_of_week,
            time_of_day=request.time_of_day,
            story_preference=request.story_preference
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduling/upcoming/{user_id}")
async def get_upcoming_reminders(user_id: str, hours: int = 24, db: Session = Depends(get_db)):
    """Yaklaşan hatırlatıcılar"""
    try:
        service = StorySchedulingService(db)
        return {
            "reminders": service.get_upcoming_reminders(uuid.UUID(user_id), hours)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PARENTAL DASHBOARD ====================

@router.get("/parental/development/{child_user_id}")
async def get_child_development(
    child_user_id: str,
    age_group: str = "7-10",
    db: Session = Depends(get_db)
):
    """Çocuk okuma gelişimi raporu"""
    try:
        service = EnhancedParentalService(db)
        return service.get_child_reading_development(uuid.UUID(child_user_id), age_group)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parental/topics/{child_user_id}")
async def get_topic_analysis(child_user_id: str, db: Session = Depends(get_db)):
    """Konu dağılımı analizi"""
    try:
        service = EnhancedParentalService(db)
        return service.get_topic_distribution_analysis(uuid.UUID(child_user_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parental/comparison/{child_user_id}")
async def compare_with_peers(
    child_user_id: str,
    age_group: str = "7-10",
    db: Session = Depends(get_db)
):
    """Yaş grubu karşılaştırması"""
    try:
        service = EnhancedParentalService(db)
        return service.compare_with_age_group(uuid.UUID(child_user_id), age_group)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
