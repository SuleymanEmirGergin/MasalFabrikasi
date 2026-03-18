from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings


class StoryReadingStatsService:
    """Hikaye okuma istatistikleri servisi"""
    
    def __init__(self):
        self.reading_stats_file = os.path.join(settings.STORAGE_PATH, "reading_stats.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.reading_stats_file):
            with open(self.reading_stats_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def record_reading_session(
        self,
        story_id: str,
        user_id: str,
        duration_seconds: int,
        pages_read: Optional[int] = None,
        completion_percentage: Optional[float] = None
    ) -> Dict:
        """Okuma oturumunu kaydeder."""
        stats = self._load_stats()
        
        if story_id not in stats:
            stats[story_id] = {
                "story_id": story_id,
                "total_reads": 0,
                "total_duration": 0,
                "unique_readers": set(),
                "reading_sessions": []
            }
        
        session = {
            "session_id": str(uuid.uuid4()),
            "user_id": user_id,
            "duration_seconds": duration_seconds,
            "pages_read": pages_read,
            "completion_percentage": completion_percentage,
            "timestamp": datetime.now().isoformat()
        }
        
        stats[story_id]["reading_sessions"].append(session)
        stats[story_id]["total_reads"] += 1
        stats[story_id]["total_duration"] += duration_seconds
        stats[story_id]["unique_readers"].add(user_id)
        
        # Set'i JSON'a uygun hale getir
        stats[story_id]["unique_readers"] = list(stats[story_id]["unique_readers"])
        
        self._save_stats(stats)
        
        return {
            "session_id": session["session_id"],
            "message": "Okuma oturumu kaydedildi"
        }
    
    async def get_story_reading_stats(
        self,
        story_id: str
    ) -> Dict:
        """Hikaye okuma istatistiklerini getirir."""
        stats = self._load_stats()
        story_stats = stats.get(story_id, {})
        
        if not story_stats:
            return {
                "story_id": story_id,
                "total_reads": 0,
                "total_duration": 0,
                "unique_readers": 0,
                "average_duration": 0
            }
        
        sessions = story_stats.get("reading_sessions", [])
        total_duration = story_stats.get("total_duration", 0)
        total_reads = story_stats.get("total_reads", 0)
        
        return {
            "story_id": story_id,
            "total_reads": total_reads,
            "total_duration": total_duration,
            "unique_readers": len(story_stats.get("unique_readers", [])),
            "average_duration": round(total_duration / total_reads, 2) if total_reads > 0 else 0,
            "completion_rate": self._calculate_completion_rate(sessions)
        }
    
    async def get_user_reading_stats(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Kullanıcı okuma istatistiklerini getirir."""
        stats = self._load_stats()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        user_sessions = []
        for story_id, story_stats in stats.items():
            for session in story_stats.get("reading_sessions", []):
                if session["user_id"] == user_id:
                    session_date = datetime.fromisoformat(session["timestamp"])
                    if session_date >= cutoff_date:
                        user_sessions.append(session)
        
        total_duration = sum(s["duration_seconds"] for s in user_sessions)
        stories_read = len(set(s.get("story_id", "") for s in user_sessions))
        
        return {
            "user_id": user_id,
            "total_sessions": len(user_sessions),
            "total_duration": total_duration,
            "stories_read": stories_read,
            "average_duration": round(total_duration / len(user_sessions), 2) if user_sessions else 0,
            "period_days": days
        }
    
    def _calculate_completion_rate(self, sessions: List[Dict]) -> float:
        """Tamamlanma oranını hesaplar."""
        if not sessions:
            return 0.0
        
        completed = len([s for s in sessions if s.get("completion_percentage", 0) >= 90])
        return round((completed / len(sessions)) * 100, 2)
    
    def _load_stats(self) -> Dict:
        """İstatistikleri yükler."""
        try:
            with open(self.reading_stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Set'leri geri yükle
                for story_id, story_stats in data.items():
                    if "unique_readers" in story_stats and isinstance(story_stats["unique_readers"], list):
                        story_stats["unique_readers"] = set(story_stats["unique_readers"])
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_stats(self, stats: Dict):
        """İstatistikleri kaydeder."""
        # Set'leri listeye çevir
        stats_copy = {}
        for story_id, story_stats in stats.items():
            stats_copy[story_id] = story_stats.copy()
            if "unique_readers" in stats_copy[story_id]:
                stats_copy[story_id]["unique_readers"] = list(stats_copy[story_id]["unique_readers"])
        
        with open(self.reading_stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_copy, f, ensure_ascii=False, indent=2)

