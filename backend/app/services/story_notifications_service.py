from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class StoryNotificationsService:
    """Hikaye bildirimleri servisi"""
    
    def __init__(self):
        self.notifications_file = os.path.join(settings.STORAGE_PATH, "story_notifications.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.notifications_file):
            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,  # "story_created", "story_shared", "comment", "reminder", etc.
        title: str,
        message: str,
        story_id: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Dict:
        """Bildirim oluşturur."""
        notifications = self._load_notifications()
        
        if user_id not in notifications:
            notifications[user_id] = []
        
        notification = {
            "notification_id": str(uuid.uuid4()),
            "type": notification_type,
            "title": title,
            "message": message,
            "story_id": story_id,
            "action_url": action_url,
            "read": False,
            "created_at": datetime.now().isoformat()
        }
        
        notifications[user_id].append(notification)
        self._save_notifications(notifications)
        
        return {
            "notification_id": notification["notification_id"],
            "message": "Bildirim oluşturuldu"
        }
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Kullanıcının bildirimlerini getirir."""
        notifications = self._load_notifications()
        user_notifications = notifications.get(user_id, [])
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n.get("read", False)]
        
        # Tarihe göre sırala (en yeni önce)
        user_notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        if limit:
            user_notifications = user_notifications[:limit]
        
        return user_notifications
    
    async def mark_notification_read(
        self,
        notification_id: str,
        user_id: str
    ) -> Dict:
        """Bildirimi okundu olarak işaretler."""
        notifications = self._load_notifications()
        
        if user_id not in notifications:
            return {"message": "Bildirim bulunamadı"}
        
        notification = next(
            (n for n in notifications[user_id] if n["notification_id"] == notification_id),
            None
        )
        
        if not notification:
            return {"message": "Bildirim bulunamadı"}
        
        notification["read"] = True
        notification["read_at"] = datetime.now().isoformat()
        self._save_notifications(notifications)
        
        return {"message": "Bildirim okundu olarak işaretlendi"}
    
    async def mark_all_read(
        self,
        user_id: str
    ) -> Dict:
        """Tüm bildirimleri okundu olarak işaretler."""
        notifications = self._load_notifications()
        
        if user_id not in notifications:
            return {"message": "Bildirim bulunamadı"}
        
        for notification in notifications[user_id]:
            if not notification.get("read", False):
                notification["read"] = True
                notification["read_at"] = datetime.now().isoformat()
        
        self._save_notifications(notifications)
        
        return {"message": "Tüm bildirimler okundu olarak işaretlendi"}
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> Dict:
        """Bildirimi siler."""
        notifications = self._load_notifications()
        
        if user_id not in notifications:
            return {"message": "Bildirim bulunamadı"}
        
        notifications[user_id] = [
            n for n in notifications[user_id]
            if n["notification_id"] != notification_id
        ]
        
        self._save_notifications(notifications)
        
        return {"message": "Bildirim silindi"}
    
    async def get_notification_stats(
        self,
        user_id: str
    ) -> Dict:
        """Bildirim istatistiklerini getirir."""
        notifications = self._load_notifications()
        user_notifications = notifications.get(user_id, [])
        
        total = len(user_notifications)
        unread = len([n for n in user_notifications if not n.get("read", False)])
        
        return {
            "total": total,
            "unread": unread,
            "read": total - unread
        }
    
    def _load_notifications(self) -> Dict:
        """Bildirimleri yükler."""
        try:
            with open(self.notifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_notifications(self, notifications: Dict):
        """Bildirimleri kaydeder."""
        with open(self.notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)

