"""
Reading Analytics Router - Okuma istatistikleri API endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.reading_analytics_service import ReadingAnalyticsService
import uuid

router = APIRouter()


@router.get("/stats/{user_id}")
async def get_reading_stats(user_id: str, db: Session = Depends(get_db)):
    """
    Kullanıcının okuma istatistiklerini getirir
    
    Returns:
        - Toplam okunan hikaye
        - Okuma süresi
        - Favoriler
        - Haftalık/aylık

 okumalar
        - Streak bilgileri
    """
    try:
        service = ReadingAnalyticsService(db)
        stats = service.get_reading_stats(uuid.UUID(user_id))
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/distribution/{user_id}")
async def get_reading_distribution(user_id: str, db: Session = Depends(get_db)):
    """
    Okuma dağılımı analizi
    
    Returns:
        - Türlere göre dağılım
        - Dillere göre dağılım
        - Saatlere göre okuma tercihi
        - Haftanın günlerine göre
    """
    try:
        service = ReadingAnalyticsService(db)
        distribution = service.get_reading_distribution(uuid.UUID(user_id))
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals/{user_id}")
async def get_reading_goals(user_id: str, db: Session = Depends(get_db)):
    """
    Okuma hedefleri ve ilerleme
    
    Returns:
        - Haftalık hedef (3 hikaye)
        - Aylık hedef (12 hikaye)
        - Streak hedefi (7 gün)
    """
    try:
        service = ReadingAnalyticsService(db)
        goals = service.get_reading_goals(uuid.UUID(user_id))
        return goals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{user_id}")
async def get_reading_insights(user_id: str, db: Session = Depends(get_db)):
    """
    Kişiselleştirilmiş okuma içgörüleri ve öneriler
    
    Returns:
        - Streak bilgilendirmeleri
        - Favori tür bilgisi
        - Okuma zamanı tercihleri
        - Başarılar
    """
    try:
        service = ReadingAnalyticsService(db)
        insights = service.get_reading_insights(uuid.UUID(user_id))
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{user_id}")
async def get_full_dashboard(user_id: str, db: Session = Depends(get_db)):
    """
    Tüm analytics bilgilerini tek endpoint'te toplar
    
    Returns:
        - stats: Genel istatistikler
        - distribution: Dağılım analizi
        - goals: Hedefler ve ilerleme
        - insights: Kişisel öneriler
    """
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
