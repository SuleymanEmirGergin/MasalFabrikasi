from typing import Dict, Optional, List
import json
import os
import hashlib
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StorySecurityService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.security_file = os.path.join(settings.STORAGE_PATH, "story_security.json")
        self.access_logs_file = os.path.join(settings.STORAGE_PATH, "access_logs.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.security_file, self.access_logs_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def encrypt_story(self, story_id: str, encryption_key: str) -> Dict:
        """Hikâyeyi şifreler."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Basit hash (gerçek uygulamada daha güvenli şifreleme kullanılmalı)
        encrypted_hash = hashlib.sha256((story.get('story_text', '') + encryption_key).encode()).hexdigest()
        
        security_data = {
            "story_id": story_id,
            "encrypted": True,
            "encryption_hash": encrypted_hash,
            "encrypted_at": datetime.now().isoformat()
        }
        
        with open(self.security_file, 'r', encoding='utf-8') as f:
            security = json.load(f)
        security[story_id] = security_data
        with open(self.security_file, 'w', encoding='utf-8') as f:
            json.dump(security, f, ensure_ascii=False, indent=2)
        
        return security_data
    
    def set_access_control(self, story_id: str, user_id: str, allowed_users: List[str], password: Optional[str] = None) -> Dict:
        """Erişim kontrolü ayarlar."""
        access_control = {
            "story_id": story_id,
            "owner_id": user_id,
            "allowed_users": allowed_users,
            "has_password": password is not None,
            "password_hash": hashlib.sha256(password.encode()).hexdigest() if password else None,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.security_file, 'r', encoding='utf-8') as f:
            security = json.load(f)
        if story_id not in security:
            security[story_id] = {}
        security[story_id]['access_control'] = access_control
        with open(self.security_file, 'w', encoding='utf-8') as f:
            json.dump(security, f, ensure_ascii=False, indent=2)
        
        return access_control
    
    def check_access(self, story_id: str, user_id: str, password: Optional[str] = None) -> bool:
        """Erişim kontrolü yapar."""
        with open(self.security_file, 'r', encoding='utf-8') as f:
            security = json.load(f)
        
        story_security = security.get(story_id, {})
        access_control = story_security.get('access_control')
        
        if not access_control:
            return True  # Erişim kontrolü yoksa erişim serbest
        
        # Şifre kontrolü
        if access_control.get('has_password'):
            if not password:
                return False
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash != access_control.get('password_hash'):
                return False
        
        # Kullanıcı kontrolü
        allowed_users = access_control.get('allowed_users', [])
        if user_id not in allowed_users and user_id != access_control.get('owner_id'):
            return False
        
        # Erişim logu
        self._log_access(story_id, user_id, "granted")
        
        return True
    
    def _log_access(self, story_id: str, user_id: str, status: str):
        """Erişim logu kaydeder."""
        log_entry = {
            "story_id": story_id,
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.access_logs_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        if story_id not in logs:
            logs[story_id] = []
        logs[story_id].append(log_entry)
        with open(self.access_logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_access_logs(self, story_id: str, limit: int = 50) -> List[Dict]:
        """Erişim loglarını getirir."""
        with open(self.access_logs_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        return logs.get(story_id, [])[-limit:]

