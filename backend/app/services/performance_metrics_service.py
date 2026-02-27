from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.like_service import LikeService
from app.services.comment_service import CommentService


class PerformanceMetricsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.like_service = LikeService()
        self.comment_service = CommentService()
        self.metrics_file = os.path.join(settings.STORAGE_PATH, "story_metrics.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Metrikler dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def record_story_view(
        self,
        story_id: str,
        user_id: Optional[str] = None,
        duration: Optional[float] = None
    ):
        """
        Hikâye görüntüleme kaydı yapar.
        
        Args:
            story_id: Hikâye ID'si
            user_id: Kullanıcı ID'si (opsiyonel)
            duration: Okuma süresi (saniye, opsiyonel)
        """
        metrics = self._load_metrics()
        
        if story_id not in metrics:
            metrics[story_id] = {
                "views": 0,
                "unique_viewers": set(),
                "total_reading_time": 0.0,
                "reading_sessions": [],
                "popular_sections": {},
                "engagement_map": {}
            }
        
        metrics[story_id]["views"] += 1
        
        if user_id:
            metrics[story_id]["unique_viewers"].add(user_id)
        
        if duration:
            metrics[story_id]["total_reading_time"] += duration
            metrics[story_id]["reading_sessions"].append({
                "user_id": user_id,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
        
        self._save_metrics(metrics)
    
    def record_section_view(
        self,
        story_id: str,
        section_index: int,
        user_id: Optional[str] = None
    ):
        """
        Hikâye bölümü görüntüleme kaydı yapar.
        """
        metrics = self._load_metrics()
        
        if story_id not in metrics:
            metrics[story_id] = {
                "views": 0,
                "unique_viewers": set(),
                "total_reading_time": 0.0,
                "reading_sessions": [],
                "popular_sections": {},
                "engagement_map": {}
            }
        
        section_key = f"section_{section_index}"
        if section_key not in metrics[story_id]["popular_sections"]:
            metrics[story_id]["popular_sections"][section_key] = 0
        
        metrics[story_id]["popular_sections"][section_key] += 1
        
        self._save_metrics(metrics)
    
    def _load_metrics(self) -> Dict:
        """Metrikleri yükler."""
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            # set'leri string'e çevir (JSON uyumluluğu için)
            for story_id, data in metrics.items():
                if "unique_viewers" in data and isinstance(data["unique_viewers"], list):
                    data["unique_viewers"] = set(data["unique_viewers"])
            
            return metrics
        except:
            return {}
    
    def _save_metrics(self, metrics: Dict):
        """Metrikleri kaydeder."""
        # set'leri list'e çevir (JSON uyumluluğu için)
        metrics_copy = {}
        for story_id, data in metrics.items():
            data_copy = data.copy()
            if "unique_viewers" in data_copy and isinstance(data_copy["unique_viewers"], set):
                data_copy["unique_viewers"] = list(data_copy["unique_viewers"])
            metrics_copy[story_id] = data_copy
        
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_copy, f, ensure_ascii=False, indent=2)
    
    def get_story_metrics(self, story_id: str) -> Dict:
        """
        Hikâye performans metriklerini getirir.
        """
        metrics = self._load_metrics()
        story_metrics = metrics.get(story_id, {})
        
        story = self.story_storage.get_story(story_id)
        if not story:
            return {}
        
        # Beğeni ve yorum sayıları
        likes = self.like_service.get_story_likes(story_id)
        comments = self.comment_service.get_story_comments(story_id)
        
        # Ortalama okuma süresi
        total_time = story_metrics.get("total_reading_time", 0)
        views = story_metrics.get("views", 0)
        avg_reading_time = total_time / views if views > 0 else 0
        
        # En popüler bölümler
        popular_sections = story_metrics.get("popular_sections", {})
        sorted_sections = sorted(
            popular_sections.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "story_id": story_id,
            "total_views": story_metrics.get("views", 0),
            "unique_viewers": len(story_metrics.get("unique_viewers", set())),
            "total_likes": len(likes),
            "total_comments": len(comments),
            "total_reading_time": round(total_time, 2),
            "average_reading_time": round(avg_reading_time, 2),
            "popular_sections": [
                {"section": section, "views": views}
                for section, views in sorted_sections
            ],
            "engagement_score": self._calculate_engagement_score(
                story_metrics.get("views", 0),
                len(likes),
                len(comments),
                avg_reading_time
            )
        }
    
    def _calculate_engagement_score(
        self,
        views: int,
        likes: int,
        comments: int,
        avg_reading_time: float
    ) -> float:
        """Etkileşim skoru hesaplar."""
        # Basit bir skorlama: görüntüleme, beğeni, yorum ve okuma süresine göre
        like_ratio = (likes / views * 100) if views > 0 else 0
        comment_ratio = (comments / views * 100) if views > 0 else 0
        
        # Skor: 0-100 arası
        score = (
            min(views / 10, 30) +  # Görüntüleme (maks 30)
            min(like_ratio * 2, 30) +  # Beğeni oranı (maks 30)
            min(comment_ratio * 3, 20) +  # Yorum oranı (maks 20)
            min(avg_reading_time / 10, 20)  # Okuma süresi (maks 20)
        )
        
        return round(min(score, 100), 2)
    
    def get_reading_progress(
        self,
        story_id: str,
        user_id: str
    ) -> Dict:
        """
        Kullanıcının hikâye okuma ilerlemesini getirir.
        """
        metrics = self._load_metrics()
        story_metrics = metrics.get(story_id, {})
        
        sessions = story_metrics.get("reading_sessions", [])
        user_sessions = [s for s in sessions if s.get("user_id") == user_id]
        
        total_time = sum(s.get("duration", 0) for s in user_sessions)
        last_read = user_sessions[-1].get("timestamp") if user_sessions else None
        
        story = self.story_storage.get_story(story_id)
        word_count = len(story.get('story_text', '').split()) if story else 0
        
        # Tahmini ilerleme (kelime sayısına göre)
        estimated_progress = min((total_time / 60) * 200 / word_count * 100, 100) if word_count > 0 else 0
        
        return {
            "story_id": story_id,
            "user_id": user_id,
            "total_reading_time": round(total_time, 2),
            "session_count": len(user_sessions),
            "last_read": last_read,
            "estimated_progress": round(estimated_progress, 1)
        }
    
    def get_trending_stories(
        self,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        """
        Trend hikâyeleri getirir.
        """
        metrics = self._load_metrics()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        story_scores = []
        
        for story_id, story_metrics in metrics.items():
            # Son 7 gün içindeki görüntülemeler
            recent_views = sum(
                1 for session in story_metrics.get("reading_sessions", [])
                if session.get("timestamp", "") >= cutoff_date
            )
            
            if recent_views > 0:
                likes = self.like_service.get_story_likes(story_id)
                comments = self.comment_service.get_story_comments(story_id)
                
                score = self._calculate_engagement_score(
                    recent_views,
                    len(likes),
                    len(comments),
                    story_metrics.get("total_reading_time", 0) / max(recent_views, 1)
                )
                
                story_scores.append({
                    "story_id": story_id,
                    "score": score,
                    "recent_views": recent_views,
                    "likes": len(likes),
                    "comments": len(comments)
                })
        
        story_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return story_scores[:limit]

