from typing import Dict, List, Optional
from app.services.story_storage import StoryStorage
from app.services.user_profile_service import UserProfileService
import json
import os
from datetime import datetime, timedelta
from app.core.config import settings


class StatisticsAnalyticsAdvancedService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.user_profile_service = UserProfileService()
        self.analytics_file = os.path.join(settings.STORAGE_PATH, "advanced_analytics.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def get_detailed_reading_statistics(self, user_id: Optional[str] = None) -> Dict:
        """Detaylı okuma istatistikleri getirir."""
        if user_id:
            all_stories = self.story_storage.get_all_stories()
            stories = [s for s in all_stories if s.get('user_id') == user_id]
        else:
            stories = self.story_storage.get_all_stories()
        
        total_words = sum(len(s.get('story_text', '').split()) for s in stories)
        total_reading_time = total_words / 200  # Ortalama okuma hızı: 200 kelime/dakika
        
        return {
            "total_stories": len(stories),
            "total_words": total_words,
            "estimated_reading_time_minutes": round(total_reading_time, 1),
            "average_story_length": round(total_words / len(stories) if stories else 0, 1),
            "stories_by_type": self._count_by_type(stories),
            "stories_by_language": self._count_by_language(stories)
        }
    
    def _count_by_type(self, stories: List[Dict]) -> Dict:
        """Türe göre sayım."""
        types = {}
        for story in stories:
            story_type = story.get('story_type', 'masal')
            types[story_type] = types.get(story_type, 0) + 1
        return types
    
    def _count_by_language(self, stories: List[Dict]) -> Dict:
        """Dile göre sayım."""
        languages = {}
        for story in stories:
            lang = story.get('language', 'tr')
            languages[lang] = languages.get(lang, 0) + 1
        return languages
    
    def get_story_performance_metrics(self, story_id: str) -> Dict:
        """Hikâye performans metrikleri getirir."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Placeholder metrikler - gerçek uygulamada daha detaylı olabilir
        return {
            "story_id": story_id,
            "views": story.get('views', 0),
            "likes": story.get('likes', 0),
            "shares": story.get('shares', 0),
            "reading_time_avg": story.get('avg_reading_time', 0),
            "completion_rate": story.get('completion_rate', 0),
            "engagement_score": self._calculate_engagement_score(story)
        }
    
    def _calculate_engagement_score(self, story: Dict) -> float:
        """Etkileşim skoru hesaplar."""
        views = story.get('views', 0)
        likes = story.get('likes', 0)
        shares = story.get('shares', 0)
        
        score = (views * 0.1) + (likes * 2) + (shares * 5)
        return round(score, 2)
    
    def analyze_user_behavior(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """Kullanıcı davranış analizi yapar."""
        start_date = datetime.now() - timedelta(days=days)
        
        # Placeholder - gerçek uygulamada daha detaylı analiz
        return {
            "user_id": user_id,
            "period_days": days,
            "stories_created": 0,
            "stories_read": 0,
            "favorite_stories": 0,
            "most_active_time": "evening",
            "preferred_story_types": [],
            "reading_streak": 0
        }
    
    def get_trend_analysis(
        self,
        period: str = "week"
    ) -> Dict:
        """Trend analizi yapar."""
        stories = self.story_storage.get_all_stories()
        
        # Son dönem hikâyeleri
        if period == "week":
            cutoff = datetime.now() - timedelta(days=7)
        elif period == "month":
            cutoff = datetime.now() - timedelta(days=30)
        else:
            cutoff = datetime.now() - timedelta(days=7)
        
        recent_stories = [
            s for s in stories
            if datetime.fromisoformat(s.get('created_at', datetime.now().isoformat())) > cutoff
        ]
        
        trending_themes = {}
        for story in recent_stories:
            theme = story.get('theme', '')
            if theme:
                trending_themes[theme] = trending_themes.get(theme, 0) + 1
        
        top_themes = sorted(trending_themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period": period,
            "total_stories": len(recent_stories),
            "trending_themes": [{"theme": t[0], "count": t[1]} for t in top_themes],
            "trending_story_types": self._count_by_type(recent_stories)
        }
    
    def record_story_interaction(
        self,
        story_id: str,
        interaction_type: str,
        user_id: Optional[str] = None
    ):
        """Hikâye etkileşimini kaydeder."""
        with open(self.analytics_file, 'r', encoding='utf-8') as f:
            analytics = json.load(f)
        
        if story_id not in analytics:
            analytics[story_id] = {
                "views": 0,
                "likes": 0,
                "shares": 0,
                "reads": 0
            }
        
        if interaction_type in analytics[story_id]:
            analytics[story_id][interaction_type] += 1
        
        analytics[story_id]["last_interaction"] = datetime.now().isoformat()
        if user_id:
            if "users" not in analytics[story_id]:
                analytics[story_id]["users"] = []
            if user_id not in analytics[story_id]["users"]:
                analytics[story_id]["users"].append(user_id)
        
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)

