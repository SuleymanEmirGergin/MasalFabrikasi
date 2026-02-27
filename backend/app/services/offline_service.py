from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class OfflineService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.offline_stories_file = os.path.join(settings.STORAGE_PATH, "offline_stories.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Offline hikâyeler dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.offline_stories_file):
            with open(self.offline_stories_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def mark_story_for_offline(
        self,
        user_id: str,
        story_id: str
    ) -> Dict:
        """
        Hikâyeyi offline okuma için işaretler.
        
        Args:
            user_id: Kullanıcı ID'si
            story_id: Hikâye ID'si
        
        Returns:
            Offline işaretleme bilgisi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        try:
            with open(self.offline_stories_file, 'r', encoding='utf-8') as f:
                offline_stories = json.load(f)
        except:
            offline_stories = {}
        
        if user_id not in offline_stories:
            offline_stories[user_id] = []
        
        if story_id not in offline_stories[user_id]:
            offline_stories[user_id].append(story_id)
        
        with open(self.offline_stories_file, 'w', encoding='utf-8') as f:
            json.dump(offline_stories, f, ensure_ascii=False, indent=2)
        
        return {
            "user_id": user_id,
            "story_id": story_id,
            "marked_for_offline": True,
            "story": story
        }
    
    def get_offline_stories(self, user_id: str) -> List[Dict]:
        """
        Kullanıcının offline hikâyelerini getirir.
        """
        try:
            with open(self.offline_stories_file, 'r', encoding='utf-8') as f:
                offline_stories = json.load(f)
        except:
            return []
        
        story_ids = offline_stories.get(user_id, [])
        stories = []
        
        for story_id in story_ids:
            story = self.story_storage.get_story(story_id)
            if story:
                stories.append(story)
        
        return stories
    
    def remove_offline_story(self, user_id: str, story_id: str) -> bool:
        """
        Hikâyeyi offline listesinden çıkarır.
        """
        try:
            with open(self.offline_stories_file, 'r', encoding='utf-8') as f:
                offline_stories = json.load(f)
        except:
            return False
        
        if user_id in offline_stories:
            if story_id in offline_stories[user_id]:
                offline_stories[user_id].remove(story_id)
                
                with open(self.offline_stories_file, 'w', encoding='utf-8') as f:
                    json.dump(offline_stories, f, ensure_ascii=False, indent=2)
                
                return True
        
        return False
    
    def prepare_offline_package(self, user_id: str) -> Dict:
        """
        Offline paketi hazırlar (tüm offline hikâyeleri içeren JSON).
        """
        offline_stories = self.get_offline_stories(user_id)
        
        package = {
            "user_id": user_id,
            "stories": offline_stories,
            "total_stories": len(offline_stories),
            "package_size": self._calculate_package_size(offline_stories),
            "created_at": datetime.now().isoformat()
        }
        
        return package
    
    def _calculate_package_size(self, stories: List[Dict]) -> int:
        """Paket boyutunu hesaplar (byte cinsinden)."""
        import sys
        return sys.getsizeof(json.dumps(stories, ensure_ascii=False))
    
    def can_access_offline(self, user_id: str, story_id: str) -> bool:
        """
        Kullanıcının hikâyeye offline erişip erişemeyeceğini kontrol eder.
        """
        try:
            with open(self.offline_stories_file, 'r', encoding='utf-8') as f:
                offline_stories = json.load(f)
        except:
            return False
        
        return story_id in offline_stories.get(user_id, [])

