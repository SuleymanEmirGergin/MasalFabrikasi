from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class MobileFeaturesService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.offline_file = os.path.join(settings.STORAGE_PATH, "offline_stories.json")
        self.notifications_file = os.path.join(settings.STORAGE_PATH, "notifications.json")
        self.widgets_file = os.path.join(settings.STORAGE_PATH, "widgets.json")
        self.shortcuts_file = os.path.join(settings.STORAGE_PATH, "shortcuts.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.offline_file, self.notifications_file, self.widgets_file, self.shortcuts_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def mark_story_for_offline(self, user_id: str, story_id: str) -> Dict:
        """Hikâyeyi offline okuma için işaretler."""
        with open(self.offline_file, 'r', encoding='utf-8') as f:
            offline = json.load(f)
        
        if user_id not in offline:
            offline[user_id] = []
        
        if story_id not in offline[user_id]:
            offline[user_id].append(story_id)
        
        with open(self.offline_file, 'w', encoding='utf-8') as f:
            json.dump(offline, f, ensure_ascii=False, indent=2)
        
        return {
            "user_id": user_id,
            "story_id": story_id,
            "offline": True,
            "marked_at": datetime.now().isoformat()
        }
    
    def get_offline_stories(self, user_id: str) -> List[str]:
        """Offline hikâyeleri getirir."""
        with open(self.offline_file, 'r', encoding='utf-8') as f:
            offline = json.load(f)
        return offline.get(user_id, [])
    
    def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        scheduled_time: Optional[str] = None
    ) -> Dict:
        """Bildirim oluşturur."""
        notification = {
            "notification_id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "scheduled_time": scheduled_time or datetime.now().isoformat(),
            "sent": False,
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
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict]:
        """Kullanıcı bildirimlerini getirir."""
        with open(self.notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        user_notifications = notifications.get(user_id, [])
        if unread_only:
            user_notifications = [n for n in user_notifications if not n.get('read', False)]
        
        return user_notifications
    
    def create_widget(
        self,
        user_id: str,
        widget_type: str,
        widget_data: Dict
    ) -> Dict:
        """Widget oluşturur."""
        widget = {
            "widget_id": str(uuid.uuid4()),
            "user_id": user_id,
            "widget_type": widget_type,
            "widget_data": widget_data,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.widgets_file, 'r', encoding='utf-8') as f:
            widgets = json.load(f)
        
        if user_id not in widgets:
            widgets[user_id] = []
        
        widgets[user_id].append(widget)
        
        with open(self.widgets_file, 'w', encoding='utf-8') as f:
            json.dump(widgets, f, ensure_ascii=False, indent=2)
        
        return widget
    
    def create_shortcut(
        self,
        user_id: str,
        action: str,
        shortcut_key: str,
        description: Optional[str] = None
    ) -> Dict:
        """Kısayol oluşturur."""
        shortcut = {
            "shortcut_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "shortcut_key": shortcut_key,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
            shortcuts = json.load(f)
        
        if user_id not in shortcuts:
            shortcuts[user_id] = []
        
        shortcuts[user_id].append(shortcut)
        
        with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
            json.dump(shortcuts, f, ensure_ascii=False, indent=2)
        
        return shortcut

