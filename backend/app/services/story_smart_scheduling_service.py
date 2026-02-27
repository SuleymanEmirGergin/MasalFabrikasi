from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime, timedelta


class StorySmartSchedulingService:
    """Hikaye zamanlayıcı ve hatırlatıcılar servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.schedules_file = os.path.join(settings.STORAGE_PATH, "smart_schedules.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.schedules_file):
            with open(self.schedules_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_smart_reminder(
        self,
        user_id: str,
        task_description: str,
        priority: str = "medium"
    ) -> Dict:
        """Akıllı hatırlatıcı oluşturur."""
        reminder_id = str(uuid.uuid4())
        
        # Görevden uygun zamanı belirle
        suggested_time = self._suggest_optimal_time(task_description, priority)
        
        reminder = {
            "reminder_id": reminder_id,
            "user_id": user_id,
            "task_description": task_description,
            "priority": priority,
            "suggested_time": suggested_time,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        schedules = self._load_schedules()
        schedules.append(reminder)
        self._save_schedules(schedules)
        
        return {
            "reminder_id": reminder_id,
            "suggested_time": suggested_time,
            "message": "Hatırlatıcı oluşturuldu"
        }
    
    async def schedule_story_creation(
        self,
        user_id: str,
        theme: str,
        preferred_time: Optional[str] = None
    ) -> Dict:
        """Hikaye oluşturma zamanla."""
        schedule_id = str(uuid.uuid4())
        
        if not preferred_time:
            preferred_time = self._suggest_optimal_time("hikaye oluştur", "medium")
        
        schedule = {
            "schedule_id": schedule_id,
            "user_id": user_id,
            "task_type": "story_creation",
            "theme": theme,
            "scheduled_time": preferred_time,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        schedules = self._load_schedules()
        schedules.append(schedule)
        self._save_schedules(schedules)
        
        return {
            "schedule_id": schedule_id,
            "scheduled_time": preferred_time,
            "message": "Hikaye oluşturma zamanlandı"
        }
    
    async def get_upcoming_reminders(
        self,
        user_id: str,
        hours_ahead: int = 24
    ) -> List[Dict]:
        """Yaklaşan hatırlatıcıları getirir."""
        schedules = self._load_schedules()
        cutoff = datetime.now() + timedelta(hours=hours_ahead)
        
        upcoming = [
            s for s in schedules
            if s.get("user_id") == user_id
            and s.get("status") == "pending"
            and datetime.fromisoformat(s.get("suggested_time", datetime.now().isoformat())) <= cutoff
        ]
        
        upcoming.sort(key=lambda x: x.get("suggested_time", ""))
        
        return upcoming
    
    def _suggest_optimal_time(
        self,
        task_description: str,
        priority: str
    ) -> str:
        """Optimal zaman önerir."""
        now = datetime.now()
        
        if priority == "high":
            # Yüksek öncelik: 1 saat sonra
            suggested = now + timedelta(hours=1)
        elif priority == "low":
            # Düşük öncelik: Yarın aynı saat
            suggested = now + timedelta(days=1)
        else:
            # Orta öncelik: 3 saat sonra
            suggested = now + timedelta(hours=3)
        
        return suggested.isoformat()
    
    def _load_schedules(self) -> List[Dict]:
        """Zamanlamaları yükler."""
        try:
            with open(self.schedules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_schedules(self, schedules: List[Dict]):
        """Zamanlamaları kaydeder."""
        with open(self.schedules_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)

