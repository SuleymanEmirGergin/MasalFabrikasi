from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.notification_service import NotificationService


class StorySchedulerService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.notification_service = NotificationService()
        self.schedules_file = os.path.join(settings.STORAGE_PATH, "story_schedules.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Zamanlamalar dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.schedules_file):
            with open(self.schedules_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def schedule_story_publication(
        self,
        story_id: str,
        user_id: str,
        publish_at: str,
        auto_publish: bool = True
    ) -> Dict:
        """
        Hikâye yayınlama zamanı planlar.
        
        Args:
            story_id: Hikâye ID'si
            user_id: Kullanıcı ID'si
            publish_at: Yayınlanma zamanı (ISO format)
            auto_publish: Otomatik yayınla
        
        Returns:
            Zamanlama objesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        schedule = {
            "schedule_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "publish_at": publish_at,
            "auto_publish": auto_publish,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "published_at": None
        }
        
        self._save_schedule(schedule)
        return schedule
    
    def _save_schedule(self, schedule: Dict):
        """Zamanlamayı kaydeder."""
        with open(self.schedules_file, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
        
        schedules.append(schedule)
        
        with open(self.schedules_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
    
    def get_scheduled_stories(self, user_id: Optional[str] = None) -> List[Dict]:
        """Zamanlanmış hikâyeleri getirir."""
        with open(self.schedules_file, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
        
        if user_id:
            schedules = [s for s in schedules if s.get('user_id') == user_id]
        
        # Sadece zamanlanmış olanları
        now = datetime.now().isoformat()
        scheduled = [s for s in schedules if s.get('publish_at', '') > now and s.get('status') == 'scheduled']
        
        return sorted(scheduled, key=lambda x: x.get('publish_at', ''))
    
    def check_and_publish_scheduled(self) -> List[Dict]:
        """
        Zamanı gelen hikâyeleri yayınlar (cron job için).
        """
        with open(self.schedules_file, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
        
        now = datetime.now().isoformat()
        published = []
        
        for schedule in schedules:
            if schedule.get('status') != 'scheduled':
                continue
            
            if schedule.get('publish_at', '') <= now:
                if schedule.get('auto_publish', False):
                    # Hikâyeyi yayınla
                    story = self.story_storage.get_story(schedule.get('story_id'))
                    if story:
                        story['is_public'] = True
                        story['published_at'] = now
                        self.story_storage.save_story(story)
                        
                        # Bildirim gönder
                        try:
                            self.notification_service.create_notification(
                                schedule.get('user_id'),
                                "Hikâyeniz Yayınlandı!",
                                f"{story.get('theme', 'Hikâyeniz')} başlıklı hikâyeniz planlanan zamanda yayınlandı.",
                                "success",
                                f"/story/{story.get('story_id')}"
                            )
                        except:
                            pass
                        
                        schedule['status'] = 'published'
                        schedule['published_at'] = now
                        published.append(schedule)
        
        # Güncellemeleri kaydet
        if published:
            with open(self.schedules_file, 'w', encoding='utf-8') as f:
                json.dump(schedules, f, ensure_ascii=False, indent=2)
        
        return published
    
    def cancel_schedule(self, schedule_id: str, user_id: str) -> bool:
        """Zamanlamayı iptal eder."""
        with open(self.schedules_file, 'r', encoding='utf-8') as f:
            schedules = json.load(f)
        
        schedule = next((s for s in schedules if s.get('schedule_id') == schedule_id), None)
        if not schedule:
            return False
        
        if schedule.get('user_id') != user_id:
            return False
        
        schedule['status'] = 'cancelled'
        
        with open(self.schedules_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)
        
        return True
    
    def create_recurring_schedule(
        self,
        user_id: str,
        schedule_type: str,
        schedule_config: Dict
    ) -> Dict:
        """
        Tekrarlayan zamanlama oluşturur (örn: her gün saat 10'da).
        
        Args:
            user_id: Kullanıcı ID'si
            schedule_type: Zamanlama tipi (daily, weekly, monthly)
            schedule_config: Zamanlama yapılandırması
        
        Returns:
            Tekrarlayan zamanlama objesi
        """
        recurring = {
            "recurring_id": str(uuid.uuid4()),
            "user_id": user_id,
            "schedule_type": schedule_type,
            "schedule_config": schedule_config,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "next_run": self._calculate_next_run(schedule_type, schedule_config)
        }
        
        recurring_file = os.path.join(settings.STORAGE_PATH, "recurring_schedules.json")
        try:
            with open(recurring_file, 'r', encoding='utf-8') as f:
                recurring_schedules = json.load(f)
        except:
            recurring_schedules = []
        
        recurring_schedules.append(recurring)
        
        with open(recurring_file, 'w', encoding='utf-8') as f:
            json.dump(recurring_schedules, f, ensure_ascii=False, indent=2)
        
        return recurring
    
    def _calculate_next_run(self, schedule_type: str, config: Dict) -> str:
        """Sonraki çalışma zamanını hesaplar."""
        now = datetime.now()
        
        if schedule_type == "daily":
            hour = config.get('hour', 10)
            minute = config.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        elif schedule_type == "weekly":
            day_of_week = config.get('day_of_week', 0)  # 0 = Monday
            hour = config.get('hour', 10)
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            next_run = now + timedelta(days=1)
        
        return next_run.isoformat()

