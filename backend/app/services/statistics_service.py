from typing import Dict, List
from datetime import datetime, timedelta
from collections import Counter
from app.services.story_storage import StoryStorage


class StatisticsService:
    def __init__(self):
        self.story_storage = StoryStorage()
    
    def get_detailed_statistics(self) -> Dict:
        """
        Detaylı istatistikler getirir.
        """
        stories = self.story_storage.get_all_stories()
        
        if not stories:
            return self._empty_statistics()
        
        # Temel istatistikler
        total_stories = len(stories)
        favorite_stories = len([s for s in stories if s.get('is_favorite', False)])
        
        # Tür istatistikleri
        story_types = self._count_story_types(stories)
        
        # Tema istatistikleri (en çok kullanılan temalar)
        themes = [s.get('theme', '') for s in stories if s.get('theme')]
        top_themes = Counter(themes).most_common(10)
        
        # Tarih istatistikleri
        date_stats = self._get_date_statistics(stories)
        
        # Görsel stil istatistikleri
        image_styles = self._count_image_styles(stories)
        
        # Dil istatistikleri
        languages = self._count_languages(stories)
        
        # Ortalama hikâye uzunluğu
        avg_length = self._calculate_avg_story_length(stories)
        
        return {
            'total_stories': total_stories,
            'favorite_stories': favorite_stories,
            'story_types': story_types,
            'top_themes': [{'theme': theme, 'count': count} for theme, count in top_themes],
            'date_statistics': date_stats,
            'image_styles': image_styles,
            'languages': languages,
            'average_story_length': avg_length,
            'last_30_days': self._get_last_30_days_count(stories),
            'last_7_days': self._get_last_7_days_count(stories),
        }
    
    def _count_story_types(self, stories: List[Dict]) -> Dict[str, int]:
        """Hikâye türlerine göre sayım."""
        types = {}
        for story in stories:
            story_type = story.get('story_type', 'masal')
            types[story_type] = types.get(story_type, 0) + 1
        return types
    
    def _count_image_styles(self, stories: List[Dict]) -> Dict[str, int]:
        """Görsel stillerine göre sayım."""
        styles = {}
        for story in stories:
            style = story.get('image_style', 'fantasy')
            styles[style] = styles.get(style, 0) + 1
        return styles
    
    def _count_languages(self, stories: List[Dict]) -> Dict[str, int]:
        """Dillere göre sayım."""
        languages = {}
        for story in stories:
            lang = story.get('language', 'tr')
            languages[lang] = languages.get(lang, 0) + 1
        return languages
    
    def _calculate_avg_story_length(self, stories: List[Dict]) -> float:
        """Ortalama hikâye uzunluğu (karakter sayısı)."""
        if not stories:
            return 0.0
        
        lengths = [len(s.get('story_text', '')) for s in stories]
        return sum(lengths) / len(lengths) if lengths else 0.0
    
    def _get_date_statistics(self, stories: List[Dict]) -> Dict:
        """Tarih bazlı istatistikler."""
        now = datetime.now()
        today = now.date()
        this_week = today - timedelta(days=7)
        this_month = today - timedelta(days=30)
        
        today_count = 0
        week_count = 0
        month_count = 0
        
        for story in stories:
            created_at = story.get('created_at', '')
            if not created_at:
                continue
            
            try:
                story_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                
                if story_date == today:
                    today_count += 1
                if story_date >= this_week:
                    week_count += 1
                if story_date >= this_month:
                    month_count += 1
            except:
                continue
        
        return {
            'today': today_count,
            'this_week': week_count,
            'this_month': month_count,
        }
    
    def _get_last_30_days_count(self, stories: List[Dict]) -> int:
        """Son 30 günde üretilen hikâye sayısı."""
        now = datetime.now()
        thirty_days_ago = (now - timedelta(days=30)).date()
        
        count = 0
        for story in stories:
            created_at = story.get('created_at', '')
            if not created_at:
                continue
            
            try:
                story_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                if story_date >= thirty_days_ago:
                    count += 1
            except:
                continue
        
        return count
    
    def _get_last_7_days_count(self, stories: List[Dict]) -> int:
        """Son 7 günde üretilen hikâye sayısı."""
        now = datetime.now()
        seven_days_ago = (now - timedelta(days=7)).date()
        
        count = 0
        for story in stories:
            created_at = story.get('created_at', '')
            if not created_at:
                continue
            
            try:
                story_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                if story_date >= seven_days_ago:
                    count += 1
            except:
                continue
        
        return count
    
    def _empty_statistics(self) -> Dict:
        """Boş istatistikler."""
        return {
            'total_stories': 0,
            'favorite_stories': 0,
            'story_types': {},
            'top_themes': [],
            'date_statistics': {'today': 0, 'this_week': 0, 'this_month': 0},
            'image_styles': {},
            'languages': {},
            'average_story_length': 0.0,
            'last_30_days': 0,
            'last_7_days': 0,
        }

