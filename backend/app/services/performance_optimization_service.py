from typing import Dict, List, Optional
import json
import os
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage
try:
    from PIL import Image
except ImportError:
    Image = None
import hashlib


class PerformanceOptimizationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.cache_file = os.path.join(settings.STORAGE_PATH, "performance_cache.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.cache_file):
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def cache_story_data(self, story_id: str, data: Dict, ttl: int = 3600) -> bool:
        """Hikâye verisini önbelleğe alır."""
        cache_entry = {
            "story_id": story_id,
            "data": data,
            "cached_at": datetime.now().isoformat(),
            "ttl": ttl,
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        cache[story_id] = cache_entry
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_cached_story(self, story_id: str) -> Optional[Dict]:
        """Önbellekten hikâye getirir."""
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        entry = cache.get(story_id)
        if not entry:
            return None
        
        expires_at = datetime.fromisoformat(entry.get('expires_at', ''))
        if datetime.now() > expires_at:
            # Süresi dolmuş, önbellekten sil
            del cache[story_id]
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            return None
        
        return entry.get('data')
    
    def optimize_image(self, image_path: str, max_size: tuple = (800, 800), quality: int = 85) -> str:
        """Görseli optimize eder."""
        try:
            img = Image.open(image_path)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            optimized_path = image_path.replace('.', '_optimized.')
            img.save(optimized_path, optimize=True, quality=quality)
            
            return optimized_path
        except Exception as e:
            print(f"Görsel optimizasyonu hatası: {e}")
            return image_path
    
    def lazy_load_story(self, story_id: str, load_images: bool = False, load_audio: bool = False) -> Dict:
        """Lazy loading ile hikâye yükler."""
        story = self.story_storage.get_story(story_id)
        if not story:
            return {}
        
        # Sadece temel verileri yükle
        basic_data = {
            "story_id": story.get('story_id'),
            "theme": story.get('theme'),
            "story_type": story.get('story_type'),
            "created_at": story.get('created_at')
        }
        
        # İsteğe bağlı olarak görsel ve ses
        if load_images:
            basic_data["image_url"] = story.get('image_url')
        if load_audio:
            basic_data["audio_url"] = story.get('audio_url')
        
        return basic_data
    
    def preload_stories(self, story_ids: List[str]) -> Dict:
        """Hikâyeleri önceden yükler."""
        preloaded = {}
        for story_id in story_ids:
            cached = self.get_cached_story(story_id)
            if not cached:
                story = self.story_storage.get_story(story_id)
                if story:
                    self.cache_story_data(story_id, story)
                    preloaded[story_id] = story
            else:
                preloaded[story_id] = cached
        
        return preloaded

