from typing import Dict, List, Optional
import json
import os
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class IntegrationsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.integrations_file = os.path.join(settings.STORAGE_PATH, "integrations.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.integrations_file):
            with open(self.integrations_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def publish_to_social_media(
        self,
        story_id: str,
        platform: str,
        access_token: str
    ) -> Dict:
        """Sosyal medyaya yayınlar."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Placeholder - gerçek implementasyon için platform API'leri gerekli
        return {
            "story_id": story_id,
            "platform": platform,
            "published": True,
            "post_url": f"https://{platform}.com/post/123",
            "published_at": datetime.now().isoformat()
        }
    
    def export_to_ebook_platform(
        self,
        story_id: str,
        platform: str,
        credentials: Dict
    ) -> Dict:
        """E-kitap platformuna dışa aktarır."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Placeholder - gerçek implementasyon için platform API'leri gerekli
        return {
            "story_id": story_id,
            "platform": platform,
            "exported": True,
            "ebook_url": f"https://{platform}.com/book/123",
            "exported_at": datetime.now().isoformat()
        }
    
    def sync_with_education_platform(
        self,
        story_id: str,
        platform: str,
        course_id: str,
        credentials: Dict
    ) -> Dict:
        """Eğitim platformu ile senkronize eder."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        return {
            "story_id": story_id,
            "platform": platform,
            "course_id": course_id,
            "synced": True,
            "synced_at": datetime.now().isoformat()
        }
    
    def publish_to_blog(
        self,
        story_id: str,
        blog_url: str,
        api_key: str
    ) -> Dict:
        """Blog'a yayınlar."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Placeholder - gerçek implementasyon için blog API'si gerekli
        return {
            "story_id": story_id,
            "blog_url": blog_url,
            "published": True,
            "post_url": f"{blog_url}/post/123",
            "published_at": datetime.now().isoformat()
        }
    
    def save_integration_settings(
        self,
        user_id: str,
        platform: str,
        settings: Dict
    ):
        """Entegrasyon ayarlarını kaydeder."""
        with open(self.integrations_file, 'r', encoding='utf-8') as f:
            integrations = json.load(f)
        
        if user_id not in integrations:
            integrations[user_id] = {}
        
        integrations[user_id][platform] = settings
        
        with open(self.integrations_file, 'w', encoding='utf-8') as f:
            json.dump(integrations, f, ensure_ascii=False, indent=2)
    
    def get_user_integrations(self, user_id: str) -> Dict:
        """Kullanıcı entegrasyonlarını getirir."""
        with open(self.integrations_file, 'r', encoding='utf-8') as f:
            integrations = json.load(f)
        return integrations.get(user_id, {})

