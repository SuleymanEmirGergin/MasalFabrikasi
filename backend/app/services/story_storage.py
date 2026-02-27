import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from app.core.config import settings


class StoryStorage:
    def __init__(self):
        self.storage_file = f"{settings.STORAGE_PATH}/stories.json"
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Storage dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_stories(self) -> List[Dict]:
        """Tüm hikâyeleri yükler."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_stories(self, stories: List[Dict]):
        """Hikâyeleri kaydeder."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)
    
    def save_story(self, story_data: Dict) -> Dict:
        """
        Yeni bir hikâye kaydeder.
        
        Args:
            story_data: Hikâye verisi (story_id, story_text, image_url, audio_url, theme, language, story_type)
        
        Returns:
            Kaydedilen hikâye verisi
        """
        stories = self._load_stories()
        
        # Hikâye zaten varsa güncelle, yoksa ekle
        story_id = story_data.get('story_id')
        existing_index = next(
            (i for i, s in enumerate(stories) if s.get('story_id') == story_id),
            None
        )
        
        story_entry = {
            **story_data,
            'created_at': story_data.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat(),
            'is_favorite': story_data.get('is_favorite', False),
            'story_type': story_data.get('story_type', 'masal'),
        }
        
        if existing_index is not None:
            # Mevcut hikâyeyi güncelle
            story_entry['is_favorite'] = stories[existing_index].get('is_favorite', False)
            stories[existing_index] = story_entry
        else:
            # Yeni hikâye ekle
            stories.append(story_entry)
        
        self._save_stories(stories)
        return story_entry
    
    def get_story(self, story_id: str) -> Optional[Dict]:
        """Belirli bir hikâyeyi getirir."""
        stories = self._load_stories()
        return next((s for s in stories if s.get('story_id') == story_id), None)
    
    def get_all_stories(
        self, 
        limit: Optional[int] = None, 
        favorite_only: bool = False,
        search_query: Optional[str] = None,
        story_type: Optional[str] = None,
        sort_by: str = "date_desc"  # "date_desc", "date_asc", "title_asc", "title_desc"
    ) -> List[Dict]:
        """
        Tüm hikâyeleri getirir.
        
        Args:
            limit: Maksimum hikâye sayısı
            favorite_only: Sadece favorileri getir
            search_query: Arama sorgusu (tema ve metinde ara)
            story_type: Hikâye türü filtresi
            sort_by: Sıralama türü
        
        Returns:
            Hikâye listesi
        """
        stories = self._load_stories()
        
        # Filtreleme
        if favorite_only:
            stories = [s for s in stories if s.get('is_favorite', False)]
        
        if story_type:
            stories = [s for s in stories if s.get('story_type') == story_type]
        
        if search_query:
            query_lower = search_query.lower()
            stories = [
                s for s in stories
                if query_lower in s.get('theme', '').lower() or
                   query_lower in s.get('story_text', '').lower()
            ]
        
        # Sıralama
        if sort_by == "date_desc":
            stories.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == "date_asc":
            stories.sort(key=lambda x: x.get('created_at', ''))
        elif sort_by == "title_asc":
            stories.sort(key=lambda x: (x.get('theme') or '').lower())
        elif sort_by == "title_desc":
            stories.sort(key=lambda x: (x.get('theme') or '').lower(), reverse=True)
        
        if limit:
            stories = stories[:limit]
        
        return stories
    
    def toggle_favorite(self, story_id: str) -> Optional[Dict]:
        """Favori durumunu değiştirir."""
        stories = self._load_stories()
        story = next((s for s in stories if s.get('story_id') == story_id), None)
        
        if story:
            story['is_favorite'] = not story.get('is_favorite', False)
            story['updated_at'] = datetime.now().isoformat()
            self._save_stories(stories)
            return story
        
        return None
    
    def delete_story(self, story_id: str) -> bool:
        """Bir hikâyeyi siler."""
        stories = self._load_stories()
        initial_count = len(stories)
        stories = [s for s in stories if s.get('story_id') != story_id]
        
        if len(stories) < initial_count:
            self._save_stories(stories)
            return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """Hikâye istatistiklerini getirir."""
        stories = self._load_stories()
        return {
            'total_stories': len(stories),
            'favorite_stories': len([s for s in stories if s.get('is_favorite', False)]),
            'story_types': self._count_story_types(stories),
        }
    
    def _count_story_types(self, stories: List[Dict]) -> Dict[str, int]:
        """Hikâye türlerine göre sayım yapar."""
        types = {}
        for story in stories:
            story_type = story.get('story_type', 'masal')
            types[story_type] = types.get(story_type, 0) + 1
        return types

