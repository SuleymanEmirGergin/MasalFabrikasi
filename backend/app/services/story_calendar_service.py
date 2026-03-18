from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings


class StoryCalendarService:
    """Hikaye takvimi ve planlama servisi"""
    
    def __init__(self):
        self.calendar_file = os.path.join(settings.STORAGE_PATH, "story_calendar.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.calendar_file):
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def schedule_story(
        self,
        story_id: str,
        user_id: str,
        scheduled_date: str,
        scheduled_time: Optional[str] = None,
        reminder: bool = False,
        reminder_minutes: int = 15
    ) -> Dict:
        """Hikayeyi takvime ekler."""
        schedule_id = str(uuid.uuid4())
        
        schedule = {
            "schedule_id": schedule_id,
            "story_id": story_id,
            "user_id": user_id,
            "scheduled_date": scheduled_date,
            "scheduled_time": scheduled_time,
            "reminder": reminder,
            "reminder_minutes": reminder_minutes,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        schedules = self._load_schedules()
        schedules.append(schedule)
        self._save_schedules(schedules)
        
        return {
            "schedule_id": schedule_id,
            "message": "Hikaye takvime eklendi"
        }
    
    async def get_scheduled_stories(
        self,
        user_id: str,
        date: Optional[str] = None
    ) -> List[Dict]:
        """Planlanmış hikayeleri getirir."""
        schedules = self._load_schedules()
        user_schedules = [s for s in schedules if s["user_id"] == user_id]
        
        if date:
            user_schedules = [s for s in user_schedules if s["scheduled_date"] == date]
        
        # Tarihe göre sırala
        user_schedules.sort(key=lambda x: (
            x.get("scheduled_date", ""),
            x.get("scheduled_time", "")
        ))
        
        return user_schedules
    
    async def mark_scheduled_story_completed(
        self,
        schedule_id: str,
        user_id: str
    ) -> Dict:
        """Planlanmış hikayeyi tamamlandı olarak işaretler."""
        schedules = self._load_schedules()
        schedule = next((s for s in schedules if s["schedule_id"] == schedule_id), None)
        
        if not schedule:
            raise ValueError("Plan bulunamadı")
        
        if schedule["user_id"] != user_id:
            raise ValueError("Bu planı düzenleme yetkiniz yok")
        
        schedule["completed"] = True
        schedule["completed_at"] = datetime.now().isoformat()
        self._save_schedules(schedules)
        
        return {"message": "Hikaye tamamlandı olarak işaretlendi"}
    
    async def get_upcoming_stories(
        self,
        user_id: str,
        days_ahead: int = 7
    ) -> List[Dict]:
        """Yaklaşan hikayeleri getirir."""
        schedules = self._load_schedules()
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        upcoming = [
            s for s in schedules
            if s["user_id"] == user_id
            and not s.get("completed", False)
            and datetime.fromisoformat(s["scheduled_date"]).date() <= end_date
        ]
        
        upcoming.sort(key=lambda x: x.get("scheduled_date", ""))
        
        return upcoming
    
    async def get_calendar_stats(
        self,
        user_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict:
        """Takvim istatistiklerini getirir."""
        schedules = self._load_schedules()
        user_schedules = [s for s in schedules if s["user_id"] == user_id]
        
        if month and year:
            user_schedules = [
                s for s in user_schedules
                if datetime.fromisoformat(s["scheduled_date"]).month == month
                and datetime.fromisoformat(s["scheduled_date"]).year == year
            ]
        
        completed = len([s for s in user_schedules if s.get("completed", False)])
        total = len(user_schedules)
        
        return {
            "total_scheduled": total,
            "completed": completed,
            "pending": total - completed,
            "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
        }
    
    def _load_schedules(self) -> List[Dict]:
        """Planları yükler."""
        try:
            with open(self.calendar_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_schedules(self, schedules: List[Dict]):
        """Planları kaydeder."""
        with open(self.calendar_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)

