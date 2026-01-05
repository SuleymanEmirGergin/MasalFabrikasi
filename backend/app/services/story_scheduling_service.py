"""
Story Scheduling Service - Hikaye okuma zamanlama ve hatırlatıcılar
Rutin oluşturma, hatırlatma sistemi
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import uuid
from datetime import datetime, time


class ReadingSchedule:
    """Okuma programı modeli"""
    def __init__(
        self,
        schedule_id: str,
        user_id: str,
        name: str,
        days_of_week: List[int],  # 0=Monday, 6=Sunday
        time_of_day: str,  # "20:00"
        active: bool = True
    ):
        self.id = schedule_id
        self.user_id = user_id
        self.name = name
        self.days_of_week = days_of_week
        self.time_of_day = time_of_day
        self.active = active


class StorySchedulingService:
    """Hikaye okuma zamanlaması ve hatırlatıcılar"""
    
    # Önceden tanımlı okuma rutinleri
    PRESET_ROUTINES = {
        "bedtime_daily": {
            "name": "Günlük Uyku Öncesi",
            "description": "Her gün aynı saatte uyku masalı",
            "days_of_week": [0, 1, 2, 3, 4, 5, 6],
            "suggested_time": "20:30",
            "story_type": "bedtime"
        },
        "weekend_adventure": {
            "name": "Hafta Sonu Maceraları",
            "description": "Cumartesi ve Pazar macera hikayeleri",
            "days_of_week": [5, 6],
            "suggested_time": "10:00",
            "story_type": "adventure"
        },
        "weekday_morning": {
            "name": "Hafta İçi Sabah",
            "description": "İş/okul günleri sabah motivasyonu",
            "days_of_week": [0, 1, 2, 3, 4],
            "suggested_time": "07:30",
            "story_type": "educational"
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        # TODO: Create ScheduleModel in database
    
    def create_schedule(
        self,
        user_id: uuid.UUID,
        name: str,
        days_of_week: List[int],
        time_of_day: str,
        story_preference: Optional[str] = None
    ) -> Dict:
        """
        Yeni okuma programı oluşturur
        
        Args:
            user_id: Kullanıcı ID
            name: Program adı
            days_of_week: Haftanın günleri [0-6]
            time_of_day: Saat (HH:MM formatında)
            story_preference: Tercih edilen hikaye türü
        
        Returns:
            Oluşturulan program
        """
        schedule = {
            "id": str(uuid.uuid4()),
            "user_id": str(user_id),
            "name": name,
            "days_of_week": days_of_week,
            "time_of_day": time_of_day,
            "story_preference": story_preference,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        # TODO: Save to database
        return schedule
    
    def get_user_schedules(self, user_id: uuid.UUID) -> List[Dict]:
        """Kullanıcının tüm programlarını getirir"""
        # TODO: Fetch from database
        # Placeholder return
        return []
    
    def get_todays_schedule(self, user_id: uuid.UUID) -> List[Dict]:
        """
        Bugün için programlanmış okuma zamanlarını getirir
        
        Returns:
            Bugünkü hatırlatıcılar listesi
        """
        today = datetime.now().weekday()  # 0=Monday
        
        # TODO: Query schedules where today in days_of_week
        # For now, return empty
        return []
    
    def get_preset_routines(self) -> List[Dict]:
        """Önceden tanımlı rutin önerilerini getirir"""
        return [
            {
                "id": routine_id,
                **routine_data
            }
            for routine_id, routine_data in self.PRESET_ROUTINES.items()
        ]
    
    def create_routine_from_preset(
        self,
        user_id: uuid.UUID,
        preset_id: str,
        custom_time: Optional[str] = None
    ) -> Dict:
        """
        Hazır rutinden kişisel program oluşturur
        
        Args:
            user_id: Kullanıcı ID
            preset_id: Hazır rutin ID'si
            custom_time: Özel saat (opsiyonel)
        
        Returns:
            Oluşturulan program
        """
        if preset_id not in self.PRESET_ROUTINES:
            raise ValueError("Invalid preset ID")
        
        preset = self.PRESET_ROUTINES[preset_id]
        
        return self.create_schedule(
            user_id=user_id,
            name=preset["name"],
            days_of_week=preset["days_of_week"],
            time_of_day=custom_time or preset["suggested_time"],
            story_preference=preset.get("story_type")
        )
    
    def get_upcoming_reminders(self, user_id: uuid.UUID, hours_ahead: int = 24) -> List[Dict]:
        """
        Yaklaşan hatırlatıcıları getirir
        
        Args:
            user_id: Kullanıcı ID
            hours_ahead: Kaç saat sonrasına kadar (varsayılan 24)
        
        Returns:
            Hatırlatıcı listesi
        """
        # TODO: Calculate upcoming reminders based on schedules
        return [
            {
                "time": "20:30",
                "message": "Uyku öncesi hikaye zamanı! 📖",
                "story_type": "bedtime",
                "in_hours": 2
            }
        ]
    
    def toggle_schedule(self, schedule_id: str, active: bool) -> Dict:
        """Programı aktif/pasif yapar"""
        # TODO: Update in database
       
        return {
            "id": schedule_id,
            "active": active,
            "message": "Program güncellendi"
        }
