from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings


class NotificationsSystemService:
    def __init__(self):
        self.notifications_file = os.path.join(settings.STORAGE_PATH, "notifications_system.json")
        self.reminders_file = os.path.join(settings.STORAGE_PATH, "reminders.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.notifications_file, self.reminders_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        story_id: Optional[str] = None
    ) -> Dict:
        """Bildirim gönderir."""
        notification = {
            "notification_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "story_id": story_id,
            "read": False,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        if user_id not in notifications:
            notifications[user_id] = []
        
        notifications[user_id].append(notification)
        
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
        
        return notification
    
    def notify_new_story(
        self,
        user_id: str,
        story_id: str,
        story_title: str
    ) -> Dict:
        """Yeni hikâye bildirimi."""
        return self.send_notification(
            user_id,
            "Yeni Hikâye",
            f"'{story_title}' hikâyesi oluşturuldu!",
            "story_created",
            story_id
        )
    
    def create_reading_reminder(
        self,
        user_id: str,
        story_id: str,
        reminder_time: str,
        frequency: str = "once"
    ) -> Dict:
        """Okuma hatırlatıcısı oluşturur."""
        reminder = {
            "reminder_id": str(uuid.uuid4()),
            "user_id": user_id,
            "story_id": story_id,
            "reminder_time": reminder_time,
            "frequency": frequency,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.reminders_file, 'r', encoding='utf-8') as f:
            reminders = json.load(f)
        
        if user_id not in reminders:
            reminders[user_id] = []
        
        reminders[user_id].append(reminder)
        
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(reminders, f, ensure_ascii=False, indent=2)
        
        return reminder
    
    def create_quiz_reminder(
        self,
        user_id: str,
        story_id: str,
        reminder_time: str
    ) -> Dict:
        """Quiz hatırlatıcısı oluşturur."""
        return self.create_reading_reminder(
            user_id,
            story_id,
            reminder_time,
            "once"
        )
    
    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Kullanıcı bildirimlerini getirir."""
        with open(self.notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        user_notifications = notifications.get(user_id, [])
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n.get('read', False)]
        
        user_notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return user_notifications[:limit]
    
    def mark_as_read(
        self,
        user_id: str,
        notification_id: str
    ) -> Dict:
        """Bildirimi okundu olarak işaretler."""
        with open(self.notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        user_notifications = notifications.get(user_id, [])
        notification = next((n for n in user_notifications if n.get('notification_id') == notification_id), None)
        
        if notification:
            notification['read'] = True
            notification['read_at'] = datetime.now().isoformat()
        
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
        
        return notification or {}

