from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class StoryActivityLogService:
    """Hikaye geçmişi ve aktivite logları servisi"""
    
    def __init__(self):
        self.activity_log_file = os.path.join(settings.STORAGE_PATH, "story_activity_log.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.activity_log_file):
            with open(self.activity_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def log_activity(
        self,
        story_id: str,
        user_id: str,
        activity_type: str,  # "created", "edited", "shared", "deleted", "viewed", etc.
        details: Optional[Dict] = None
    ) -> Dict:
        """Aktivite kaydeder."""
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        logs = self._load_logs()
        logs.append(log_entry)
        self._save_logs(logs)
        
        return {
            "log_id": log_entry["log_id"],
            "message": "Aktivite kaydedildi"
        }
    
    async def get_story_activity(
        self,
        story_id: str,
        activity_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Hikaye aktivitelerini getirir."""
        logs = self._load_logs()
        story_logs = [log for log in logs if log["story_id"] == story_id]
        
        if activity_type:
            story_logs = [log for log in story_logs if log["activity_type"] == activity_type]
        
        # Tarihe göre sırala (en yeni önce)
        story_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        if limit:
            story_logs = story_logs[:limit]
        
        return story_logs
    
    async def get_user_activity(
        self,
        user_id: str,
        activity_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Kullanıcı aktivitelerini getirir."""
        logs = self._load_logs()
        user_logs = [log for log in logs if log["user_id"] == user_id]
        
        if activity_type:
            user_logs = [log for log in user_logs if log["activity_type"] == activity_type]
        
        # Tarihe göre sırala (en yeni önce)
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        if limit:
            user_logs = user_logs[:limit]
        
        return user_logs
    
    async def get_activity_stats(
        self,
        story_id: Optional[str] = None,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """Aktivite istatistiklerini getirir."""
        logs = self._load_logs()
        
        # Filtrele
        if story_id:
            logs = [log for log in logs if log["story_id"] == story_id]
        if user_id:
            logs = [log for log in logs if log["user_id"] == user_id]
        
        # Tarih filtresi
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        logs = [
            log for log in logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff_date
        ]
        
        # İstatistikler
        activity_counts = {}
        for log in logs:
            activity_type = log["activity_type"]
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
        
        return {
            "total_activities": len(logs),
            "activity_breakdown": activity_counts,
            "period_days": days
        }
    
    def _load_logs(self) -> List[Dict]:
        """Logları yükler."""
        try:
            with open(self.activity_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_logs(self, logs: List[Dict]):
        """Logları kaydeder."""
        with open(self.activity_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

