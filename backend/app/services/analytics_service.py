from typing import Dict, List, Optional
from app.services.story_storage import StoryStorage
from app.services.user_service import UserService
from app.services.like_service import LikeService
from app.services.comment_service import CommentService
from datetime import datetime, timedelta
import json
import os
from app.core.config import settings


class AnalyticsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.user_service = UserService()
        self.like_service = LikeService()
        self.comment_service = CommentService()
    
    def get_dashboard_statistics(self, user_id: Optional[str] = None) -> Dict:
        """
        Dashboard istatistiklerini getirir.
        
        Args:
            user_id: Kullanıcı ID'si (opsiyonel - belirtilirse sadece o kullanıcının istatistikleri)
        
        Returns:
            İstatistikler
        """
        all_stories = self.story_storage.get_all_stories()
        
        if user_id:
            all_stories = [s for s in all_stories if s.get('user_id') == user_id]
        
        # Genel istatistikler
        total_stories = len(all_stories)
        total_words = sum(len(s.get('story_text', '').split()) for s in all_stories)
        
        # Tarih bazlı istatistikler
        now = datetime.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        stories_today = sum(
            1 for s in all_stories
            if self._parse_date(s.get('created_at', '')) == today
        )
        
        stories_this_week = sum(
            1 for s in all_stories
            if self._parse_date(s.get('created_at', '')) >= week_ago.date()
        )
        
        stories_this_month = sum(
            1 for s in all_stories
            if self._parse_date(s.get('created_at', '')) >= month_ago.date()
        )
        
        # Tema istatistikleri
        themes = {}
        for story in all_stories:
            theme = story.get('theme', 'Bilinmeyen')
            themes[theme] = themes.get(theme, 0) + 1
        
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Hikâye türü istatistikleri
        story_types = {}
        for story in all_stories:
            story_type = story.get('story_type', 'Bilinmeyen')
            story_types[story_type] = story_types.get(story_type, 0) + 1
        
        # Beğeni istatistikleri
        total_likes = 0
        for story in all_stories:
            story_id = story.get('story_id')
            likes = self.like_service.get_story_likes(story_id)
            total_likes += len(likes)
        
        # Yorum istatistikleri
        total_comments = 0
        for story in all_stories:
            story_id = story.get('story_id')
            comments = self.comment_service.get_story_comments(story_id)
            total_comments += len(comments)
        
        # Ortalama hikâye uzunluğu
        avg_story_length = total_words / total_stories if total_stories > 0 else 0
        
        return {
            "overview": {
                "total_stories": total_stories,
                "total_words": total_words,
                "average_story_length": round(avg_story_length, 1),
                "total_likes": total_likes,
                "total_comments": total_comments
            },
            "time_based": {
                "today": stories_today,
                "this_week": stories_this_week,
                "this_month": stories_this_month
            },
            "themes": {
                "top_themes": [{"theme": t[0], "count": t[1]} for t in top_themes],
                "total_unique_themes": len(themes)
            },
            "story_types": {
                "distribution": story_types,
                "total_types": len(story_types)
            },
            "engagement": {
                "average_likes_per_story": round(total_likes / total_stories, 2) if total_stories > 0 else 0,
                "average_comments_per_story": round(total_comments / total_stories, 2) if total_stories > 0 else 0
            }
        }
    
    def _parse_date(self, date_string: str) -> datetime.date:
        """Tarih string'ini parse eder."""
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
        except:
            return datetime.now().date()
    
    def get_user_analytics(self, user_id: str) -> Dict:
        """
        Kullanıcı analitiklerini getirir.
        """
        user_stories = self.story_storage.get_user_stories(user_id)
        
        total_stories = len(user_stories)
        total_words = sum(len(s.get('story_text', '').split()) for s in user_stories)
        
        # En popüler hikâye
        most_liked_story = None
        max_likes = 0
        for story in user_stories:
            story_id = story.get('story_id')
            likes = self.like_service.get_story_likes(story_id)
            if len(likes) > max_likes:
                max_likes = len(likes)
                most_liked_story = story
        
        # Aktivite grafiği (son 30 gün)
        activity_data = {}
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).date()
            activity_data[date.isoformat()] = 0
        
        for story in user_stories:
            story_date = self._parse_date(story.get('created_at', ''))
            if story_date.isoformat() in activity_data:
                activity_data[story_date.isoformat()] += 1
        
        return {
            "total_stories": total_stories,
            "total_words": total_words,
            "average_story_length": round(total_words / total_stories, 1) if total_stories > 0 else 0,
            "most_liked_story": {
                "story_id": most_liked_story.get('story_id') if most_liked_story else None,
                "theme": most_liked_story.get('theme') if most_liked_story else None,
                "likes": max_likes
            },
            "activity_chart": activity_data
        }
    
    def get_trending_analysis(self, days: int = 7) -> Dict:
        """
        Trend analizi yapar.
        """
        all_stories = self.story_storage.get_all_stories()
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        
        recent_stories = [
            s for s in all_stories
            if self._parse_date(s.get('created_at', '')) >= cutoff_date
        ]
        
        # En çok beğenilen hikâyeler
        story_scores = []
        for story in recent_stories:
            story_id = story.get('story_id')
            likes = self.like_service.get_story_likes(story_id)
            comments = self.comment_service.get_story_comments(story_id)
            
            # Skor: beğeni * 2 + yorum
            score = len(likes) * 2 + len(comments)
            
            story_scores.append({
                "story": story,
                "score": score,
                "likes": len(likes),
                "comments": len(comments)
            })
        
        story_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            "period_days": days,
            "total_stories": len(recent_stories),
            "trending_stories": [
                {
                    "story_id": s['story'].get('story_id'),
                    "theme": s['story'].get('theme'),
                    "score": s['score'],
                    "likes": s['likes'],
                    "comments": s['comments']
                }
                for s in story_scores[:10]
            ]
        }

