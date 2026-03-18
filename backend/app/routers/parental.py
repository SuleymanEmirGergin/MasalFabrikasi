from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import random

router = APIRouter()

class LearningAnalytics(BaseModel):
    week_stories_count: int
    learned_concepts: List[str]
    emotional_state: str # happy, calm, adventurous, etc.
    reading_time_minutes: int
    favorite_themes: List[str]

class ActivityLog(BaseModel):
    date: str
    stories_read: int
    duration_minutes: int

class ParentalSettings(BaseModel):
    daily_time_limit_minutes: int
    sleep_mode_enabled: bool
    sleep_mode_start_hour: int # 21 = 9 PM
    allowed_content_filter: str # all, educational_only, etc.

# Mock data storage
CURRENT_SETTINGS = {
    "daily_time_limit_minutes": 60,
    "sleep_mode_enabled": True,
    "sleep_mode_start_hour": 21,
    "allowed_content_filter": "all"
}

@router.get("/analytics/{user_id}", response_model=LearningAnalytics)
async def get_learning_analytics(user_id: str):
    """
    Çocuğun haftalık öğrenme verilerini getirir.
    """
    # Mock analytics
    return {
        "week_stories_count": random.randint(5, 15),
        "learned_concepts": ["cesaret", "arkadaşlık", "sorumluluk", "hayal gücü"],
        "emotional_state": random.choice(["happy", "calm", "adventurous", "curious"]),
        "reading_time_minutes": random.randint(120, 300),
        "favorite_themes": ["uzay", "hayvanlar", "macera"]
    }

@router.get("/activity/{user_id}", response_model=List[ActivityLog])
async def get_activity_logs(user_id: str, days: int = 7):
    """
    Son N günün aktivite loglarını getirir.
    """
    logs = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        logs.append({
            "date": date,
            "stories_read": random.randint(0, 3),
            "duration_minutes": random.randint(10, 60)
        })
    return logs

@router.get("/settings", response_model=ParentalSettings)
async def get_parental_settings():
    """
    Ebeveyn kontrol ayarlarını getirir.
    """
    return CURRENT_SETTINGS

@router.post("/settings")
async def update_parental_settings(settings: ParentalSettings):
    """
    Ebeveyn kontrol ayarlarını günceller.
    """
    CURRENT_SETTINGS.update(settings.dict())
    return {"message": "Ayarlar başarıyla güncellendi."}
