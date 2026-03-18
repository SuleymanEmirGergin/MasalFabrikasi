from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StoryVersioningService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.versions_file = os.path.join(settings.STORAGE_PATH, "story_versions.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Versiyon dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.versions_file):
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_version(
        self,
        story_id: str,
        version_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Hikâyenin yeni bir versiyonunu oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            version_name: Versiyon adı (opsiyonel)
            description: Versiyon açıklaması (opsiyonel)
        
        Returns:
            Versiyon objesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Mevcut versiyonları getir
        versions = self.get_story_versions(story_id)
        version_number = len(versions) + 1
        
        version = {
            "version_id": str(uuid.uuid4()),
            "story_id": story_id,
            "version_number": version_number,
            "version_name": version_name or f"Versiyon {version_number}",
            "description": description,
            "story_text": story.get('story_text', ''),
            "image_url": story.get('image_url'),
            "audio_url": story.get('audio_url'),
            "theme": story.get('theme'),
            "language": story.get('language'),
            "story_type": story.get('story_type'),
            "created_at": datetime.now().isoformat(),
            "created_by": story.get('user_id')
        }
        
        self._save_version(version)
        
        return version
    
    def _save_version(self, version: Dict):
        """Versiyonu kaydeder."""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        versions.append(version)
        
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
    
    def get_story_versions(self, story_id: str) -> List[Dict]:
        """Hikâyenin tüm versiyonlarını getirir."""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        return sorted(
            [v for v in versions if v.get('story_id') == story_id],
            key=lambda x: x.get('version_number', 0),
            reverse=True
        )
    
    def get_version(self, version_id: str) -> Optional[Dict]:
        """Belirli bir versiyonu getirir."""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        return next((v for v in versions if v.get('version_id') == version_id), None)
    
    def restore_version(self, version_id: str) -> Dict:
        """
        Bir versiyonu geri yükler (ana hikâyeyi bu versiyonla değiştirir).
        
        Args:
            version_id: Geri yüklenecek versiyon ID'si
        
        Returns:
            Güncellenmiş hikâye
        """
        version = self.get_version(version_id)
        if not version:
            raise ValueError("Versiyon bulunamadı")
        
        story_id = version.get('story_id')
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Hikâyeyi versiyonla güncelle
        story['story_text'] = version.get('story_text', '')
        story['image_url'] = version.get('image_url')
        story['audio_url'] = version.get('audio_url')
        story['updated_at'] = datetime.now().isoformat()
        
        # Yeni versiyon oluştur (geri yüklemeden önceki hali için)
        self.create_version(story_id, "Geri yüklemeden önce")
        
        # Hikâyeyi kaydet
        updated_story = self.story_storage.save_story(story)
        
        return updated_story
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict:
        """
        İki versiyonu karşılaştırır.
        
        Args:
            version_id_1: İlk versiyon ID'si
            version_id_2: İkinci versiyon ID'si
        
        Returns:
            Karşılaştırma sonuçları
        """
        version1 = self.get_version(version_id_1)
        version2 = self.get_version(version_id_2)
        
        if not version1 or not version2:
            raise ValueError("Versiyon bulunamadı")
        
        text1 = version1.get('story_text', '')
        text2 = version2.get('story_text', '')
        
        # Basit karşılaştırma
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        added_words = words2 - words1
        removed_words = words1 - words2
        common_words = words1 & words2
        
        return {
            "version1": {
                "version_id": version_id_1,
                "version_name": version1.get('version_name'),
                "word_count": len(text1.split()),
                "char_count": len(text1)
            },
            "version2": {
                "version_id": version_id_2,
                "version_name": version2.get('version_name'),
                "word_count": len(text2.split()),
                "char_count": len(text2)
            },
            "comparison": {
                "added_words": list(added_words),
                "removed_words": list(removed_words),
                "common_words": len(common_words),
                "similarity": len(common_words) / max(len(words1), len(words2)) if words1 or words2 else 0
            }
        }
    
    def delete_version(self, version_id: str) -> bool:
        """Versiyonu siler."""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        original_count = len(versions)
        versions = [v for v in versions if v.get('version_id') != version_id]
        
        if len(versions) < original_count:
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump(versions, f, ensure_ascii=False, indent=2)
            return True
        
        return False

