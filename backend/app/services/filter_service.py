from typing import List, Dict, Optional
import uuid
from app.services.story_storage import StoryStorage
from datetime import datetime, timedelta


class FilterService:
    def __init__(self):
        self.story_storage = StoryStorage()
    
    def filter_stories(
        self,
        filters: Dict,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50
    ) -> List[Dict]:
        """
        Hikâyeleri filtreler ve sıralar.
        
        Args:
            filters: Filtreler {
                "themes": ["tema1", "tema2"],
                "story_types": ["masal", "hikaye"],
                "languages": ["tr", "en"],
                "min_word_count": 100,
                "max_word_count": 1000,
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "user_id": "user123",
                "is_public": True,
                "has_image": True,
                "has_audio": True
            }
            sort_by: Sıralama alanı (created_at, theme, word_count, like_count)
            sort_order: Sıralama yönü (asc, desc)
            limit: Maksimum sonuç sayısı
        
        Returns:
            Filtrelenmiş hikâyeler listesi
        """
        all_stories = self.story_storage.get_all_stories()
        filtered = []
        
        for story in all_stories:
            # Tema filtresi
            if filters.get('themes'):
                story_theme = story.get('theme', '').lower()
                if not any(theme.lower() in story_theme for theme in filters['themes']):
                    continue
            
            # Hikâye türü filtresi
            if filters.get('story_types'):
                story_type = story.get('story_type', '').lower()
                if story_type not in [t.lower() for t in filters['story_types']]:
                    continue
            
            # Dil filtresi
            if filters.get('languages'):
                if story.get('language') not in filters['languages']:
                    continue
            
            # Kelime sayısı filtresi
            word_count = len(story.get('story_text', '').split())
            if filters.get('min_word_count'):
                if word_count < filters['min_word_count']:
                    continue
            if filters.get('max_word_count'):
                if word_count > filters['max_word_count']:
                    continue
            
            # Tarih filtresi
            created_at = story.get('created_at', '')
            if filters.get('date_from'):
                try:
                    date_from = datetime.fromisoformat(filters['date_from'].replace('Z', '+00:00'))
                    story_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if story_date < date_from:
                        continue
                except:
                    pass
            
            if filters.get('date_to'):
                try:
                    date_to = datetime.fromisoformat(filters['date_to'].replace('Z', '+00:00'))
                    story_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if story_date > date_to:
                        continue
                except:
                    pass
            
            # Kullanıcı filtresi
            if filters.get('user_id'):
                if story.get('user_id') != filters['user_id']:
                    continue
            
            # Görünürlük filtresi
            if filters.get('is_public') is not None:
                if story.get('is_public', False) != filters['is_public']:
                    continue
            
            # Görsel filtresi
            if filters.get('has_image'):
                if not story.get('image_url'):
                    continue
            
            # Ses filtresi
            if filters.get('has_audio'):
                if not story.get('audio_url'):
                    continue
            
            filtered.append(story)
        
        # Sıralama
        if sort_by == "created_at":
            filtered.sort(
                key=lambda x: x.get('created_at', ''),
                reverse=(sort_order == "desc")
            )
        elif sort_by == "theme":
            filtered.sort(
                key=lambda x: x.get('theme', '').lower(),
                reverse=(sort_order == "desc")
            )
        elif sort_by == "word_count":
            filtered.sort(
                key=lambda x: len(x.get('story_text', '').split()),
                reverse=(sort_order == "desc")
            )
        elif sort_by == "like_count":
            # Beğeni sayısına göre sıralama (gerçek uygulamada like_service kullanılabilir)
            filtered.sort(
                key=lambda x: x.get('like_count', 0),
                reverse=(sort_order == "desc")
            )
        
        return filtered[:limit]
    
    def get_filter_options(self) -> Dict:
        """
        Mevcut filtre seçeneklerini getirir.
        """
        all_stories = self.story_storage.get_all_stories()
        
        # Tüm temalar
        themes = set()
        for story in all_stories:
            theme = story.get('theme', '').strip()
            if theme:
                themes.add(theme)
        
        # Tüm hikâye türleri
        story_types = set()
        for story in all_stories:
            story_type = story.get('story_type', '').strip()
            if story_type:
                story_types.add(story_type)
        
        # Tüm diller
        languages = set()
        for story in all_stories:
            language = story.get('language', '').strip()
            if language:
                languages.add(language)
        
        # Kelime sayısı aralığı
        word_counts = [len(s.get('story_text', '').split()) for s in all_stories]
        min_words = min(word_counts) if word_counts else 0
        max_words = max(word_counts) if word_counts else 0
        
        return {
            "themes": sorted(list(themes)),
            "story_types": sorted(list(story_types)),
            "languages": sorted(list(languages)),
            "word_count_range": {
                "min": min_words,
                "max": max_words
            },
            "date_range": {
                "min": min([s.get('created_at', '') for s in all_stories if s.get('created_at')]) or None,
                "max": max([s.get('created_at', '') for s in all_stories if s.get('created_at')]) or None
            }
        }
    
    def save_search(
        self,
        user_id: str,
        search_name: str,
        filters: Dict,
        sort_by: str,
        sort_order: str
    ) -> Dict:
        """
        Arama filtresini kaydeder.
        """
        import json
        import os
        from app.core.config import settings
        
        saved_searches_file = os.path.join(settings.STORAGE_PATH, "saved_searches.json")
        
        try:
            with open(saved_searches_file, 'r', encoding='utf-8') as f:
                saved_searches = json.load(f)
        except:
            saved_searches = {}
        
        if user_id not in saved_searches:
            saved_searches[user_id] = []
        
        search = {
            "search_id": str(uuid.uuid4()),
            "search_name": search_name,
            "filters": filters,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "created_at": datetime.now().isoformat()
        }
        
        saved_searches[user_id].append(search)
        
        with open(saved_searches_file, 'w', encoding='utf-8') as f:
            json.dump(saved_searches, f, ensure_ascii=False, indent=2)
        
        return search
    
    def get_saved_searches(self, user_id: str) -> List[Dict]:
        """Kaydedilmiş aramaları getirir."""
        import json
        import os
        from app.core.config import settings
        
        saved_searches_file = os.path.join(settings.STORAGE_PATH, "saved_searches.json")
        
        try:
            with open(saved_searches_file, 'r', encoding='utf-8') as f:
                saved_searches = json.load(f)
            return saved_searches.get(user_id, [])
        except:
            return []

