from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import re


class StorySearchAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """Anlamsal arama yapar."""
        all_stories = self.story_storage.get_all_stories()
        
        # Basit anlamsal arama (gerçek uygulamada embedding kullanılabilir)
        query_lower = query.lower()
        scored_stories = []
        
        for story in all_stories:
            score = 0
            story_text = story.get('story_text', '').lower()
            theme = story.get('theme', '').lower()
            
            # Anahtar kelime eşleşmeleri
            query_words = query_lower.split()
            for word in query_words:
                if word in story_text:
                    score += 2
                if word in theme:
                    score += 5
            
            if score > 0:
                scored_stories.append({"story": story, "score": score})
        
        scored_stories.sort(key=lambda x: x['score'], reverse=True)
        return [s['story'] for s in scored_stories[:limit]]
    
    def advanced_filter(
        self,
        filters: Dict,
        limit: int = 50
    ) -> List[Dict]:
        """Gelişmiş filtreleme."""
        all_stories = self.story_storage.get_all_stories()
        
        # Filtreleme
        if filters.get('theme'):
            all_stories = [s for s in all_stories if filters['theme'].lower() in s.get('theme', '').lower()]
        
        if filters.get('story_type'):
            all_stories = [s for s in all_stories if s.get('story_type') == filters['story_type']]
        
        if filters.get('language'):
            all_stories = [s for s in all_stories if s.get('language') == filters['language']]
        
        if filters.get('min_length'):
            all_stories = [s for s in all_stories if len(s.get('story_text', '').split()) >= filters['min_length']]
        
        if filters.get('max_length'):
            all_stories = [s for s in all_stories if len(s.get('story_text', '').split()) <= filters['max_length']]
        
        if filters.get('date_from'):
            all_stories = [s for s in all_stories if s.get('created_at', '') >= filters['date_from']]
        
        if filters.get('date_to'):
            all_stories = [s for s in all_stories if s.get('created_at', '') <= filters['date_to']]
        
        # Sıralama
        sort_by = filters.get('sort_by', 'created_at')
        reverse = filters.get('sort_order', 'desc') == 'desc'
        
        if sort_by == 'created_at':
            all_stories.sort(key=lambda x: x.get('created_at', ''), reverse=reverse)
        elif sort_by == 'theme':
            all_stories.sort(key=lambda x: x.get('theme', '').lower(), reverse=reverse)
        
        return all_stories[:limit]
    
    async def search_by_sentiment(
        self,
        sentiment: str,
        limit: int = 10
    ) -> List[Dict]:
        """Duyguya göre arama."""
        # Placeholder - gerçek implementasyon için duygu analizi gerekli
        all_stories = self.story_storage.get_all_stories()
        return all_stories[:limit]
    
    def search_by_character(
        self,
        character_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """Karaktere göre arama."""
        all_stories = self.story_storage.get_all_stories()
        character_lower = character_name.lower()
        
        matching_stories = []
        for story in all_stories:
            story_text = story.get('story_text', '').lower()
            if character_lower in story_text:
                matching_stories.append(story)
        
        return matching_stories[:limit]

