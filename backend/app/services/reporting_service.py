from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.services.story_storage import StoryStorage
from app.services.user_service import UserService
from app.services.like_service import LikeService
from app.services.comment_service import CommentService


class ReportingService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.user_service = UserService()
        self.like_service = LikeService()
        self.comment_service = CommentService()
    
    def generate_weekly_report(self, user_id: str) -> Dict:
        """
        Haftalık rapor oluşturur.
        """
        week_ago = datetime.now() - timedelta(days=7)
        
        all_stories = self.story_storage.get_user_stories(user_id)
        recent_stories = [
            s for s in all_stories
            if datetime.fromisoformat(s.get('created_at', '').replace('Z', '+00:00')) >= week_ago
        ]
        
        total_likes = 0
        total_comments = 0
        
        for story in recent_stories:
            story_id = story.get('story_id')
            likes = self.like_service.get_story_likes(story_id)
            comments = self.comment_service.get_story_comments(story_id)
            total_likes += len(likes)
            total_comments += len(comments)
        
        total_words = sum(len(s.get('story_text', '').split()) for s in recent_stories)
        
        return {
            "period": "weekly",
            "start_date": week_ago.isoformat(),
            "end_date": datetime.now().isoformat(),
            "stories_created": len(recent_stories),
            "total_words": total_words,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "average_story_length": round(total_words / len(recent_stories), 1) if recent_stories else 0,
            "top_story": self._get_top_story(recent_stories)
        }
    
    def generate_monthly_report(self, user_id: str) -> Dict:
        """
        Aylık rapor oluşturur.
        """
        month_ago = datetime.now() - timedelta(days=30)
        
        all_stories = self.story_storage.get_user_stories(user_id)
        recent_stories = [
            s for s in all_stories
            if datetime.fromisoformat(s.get('created_at', '').replace('Z', '+00:00')) >= month_ago
        ]
        
        total_likes = 0
        total_comments = 0
        
        for story in recent_stories:
            story_id = story.get('story_id')
            likes = self.like_service.get_story_likes(story_id)
            comments = self.comment_service.get_story_comments(story_id)
            total_likes += len(likes)
            total_comments += len(comments)
        
        total_words = sum(len(s.get('story_text', '').split()) for s in recent_stories)
        
        # Tema dağılımı
        themes = {}
        for story in recent_stories:
            theme = story.get('theme', 'Bilinmeyen')
            themes[theme] = themes.get(theme, 0) + 1
        
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period": "monthly",
            "start_date": month_ago.isoformat(),
            "end_date": datetime.now().isoformat(),
            "stories_created": len(recent_stories),
            "total_words": total_words,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "average_story_length": round(total_words / len(recent_stories), 1) if recent_stories else 0,
            "top_themes": [{"theme": t[0], "count": t[1]} for t in top_themes],
            "top_story": self._get_top_story(recent_stories)
        }
    
    def _get_top_story(self, stories: List[Dict]) -> Optional[Dict]:
        """En popüler hikâyeyi getirir."""
        if not stories:
            return None
        
        story_scores = []
        for story in stories:
            story_id = story.get('story_id')
            likes = self.like_service.get_story_likes(story_id)
            comments = self.comment_service.get_story_comments(story_id)
            
            score = len(likes) * 2 + len(comments)
            story_scores.append({
                "story": story,
                "score": score
            })
        
        story_scores.sort(key=lambda x: x['score'], reverse=True)
        top = story_scores[0]['story'] if story_scores else None
        
        if top:
            return {
                "story_id": top.get('story_id'),
                "theme": top.get('theme'),
                "likes": len(self.like_service.get_story_likes(top.get('story_id'))),
                "comments": len(self.comment_service.get_story_comments(top.get('story_id')))
            }
        
        return None
    
    def generate_achievement_report(self, user_id: str) -> Dict:
        """
        Başarı raporu oluşturur.
        """
        # Bu gerçek uygulamada achievement_service kullanılabilir
        return {
            "total_achievements": 0,
            "recent_achievements": [],
            "progress": {}
        }
    
    def generate_reading_statistics(self, user_id: str) -> Dict:
        """
        Okuma istatistikleri raporu oluşturur.
        """
        all_stories = self.story_storage.get_user_stories(user_id)
        
        total_words = sum(len(s.get('story_text', '').split()) for s in all_stories)
        total_stories = len(all_stories)
        
        # Ortalama okuma süresi (kelime sayısına göre tahmin)
        avg_reading_time = (total_words / 200) / 60  # Dakika cinsinden (200 kelime/dakika)
        
        return {
            "total_stories": total_stories,
            "total_words": total_words,
            "average_story_length": round(total_words / total_stories, 1) if total_stories > 0 else 0,
            "estimated_reading_time_hours": round(avg_reading_time / 60, 1),
            "estimated_reading_time_minutes": round(avg_reading_time, 1)
        }

