from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryVersionControlService:
    """Hikaye versiyon kontrolü servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.versions_file = os.path.join(settings.STORAGE_PATH, "story_versions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.versions_file):
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_version(
        self,
        story_id: str,
        story_text: str,
        version_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Yeni versiyon oluşturur."""
        versions = self._load_versions()
        
        if story_id not in versions:
            versions[story_id] = {
                "story_id": story_id,
                "versions": [],
                "current_version": None
            }
        
        version_number = len(versions[story_id]["versions"]) + 1
        version_id = str(uuid.uuid4())
        
        version = {
            "version_id": version_id,
            "version_number": version_number,
            "version_name": version_name or f"Versiyon {version_number}",
            "description": description,
            "story_text": story_text,
            "created_at": datetime.now().isoformat(),
            "created_by": None
        }
        
        versions[story_id]["versions"].append(version)
        versions[story_id]["current_version"] = version_id
        self._save_versions(versions)
        
        return {
            "version_id": version_id,
            "version_number": version_number,
            "message": "Versiyon oluşturuldu"
        }
    
    async def get_version_history(
        self,
        story_id: str
    ) -> List[Dict]:
        """Versiyon geçmişini getirir."""
        versions = self._load_versions()
        story_versions = versions.get(story_id, {})
        
        return story_versions.get("versions", [])
    
    async def restore_version(
        self,
        story_id: str,
        version_id: str
    ) -> Dict:
        """Versiyonu geri yükler."""
        versions = self._load_versions()
        story_versions = versions.get(story_id, {})
        
        version = next(
            (v for v in story_versions.get("versions", []) if v["version_id"] == version_id),
            None
        )
        
        if not version:
            raise ValueError("Versiyon bulunamadı")
        
        # Yeni versiyon olarak geri yükle
        restored = await self.create_version(
            story_id,
            version["story_text"],
            f"Geri yüklenen: {version['version_name']}",
            "Önceki versiyondan geri yüklendi"
        )
        
        return {
            "restored_version_id": restored["version_id"],
            "original_version_id": version_id,
            "message": "Versiyon geri yüklendi"
        }
    
    async def compare_versions(
        self,
        story_id: str,
        version1_id: str,
        version2_id: str
    ) -> Dict:
        """İki versiyonu karşılaştırır."""
        versions = self._load_versions()
        story_versions = versions.get(story_id, {})
        
        v1 = next((v for v in story_versions.get("versions", []) if v["version_id"] == version1_id), None)
        v2 = next((v for v in story_versions.get("versions", []) if v["version_id"] == version2_id), None)
        
        if not v1 or not v2:
            raise ValueError("Versiyon bulunamadı")
        
        # Basit karşılaştırma
        differences = {
            "text_length_diff": len(v2["story_text"]) - len(v1["story_text"]),
            "word_count_diff": len(v2["story_text"].split()) - len(v1["story_text"].split()),
            "similarity": self._calculate_similarity(v1["story_text"], v2["story_text"])
        }
        
        return {
            "version1": {
                "version_id": version1_id,
                "version_name": v1["version_name"],
                "text_length": len(v1["story_text"])
            },
            "version2": {
                "version_id": version2_id,
                "version_name": v2["version_name"],
                "text_length": len(v2["story_text"])
            },
            "differences": differences
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Benzerlik hesaplar."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _load_versions(self) -> Dict:
        """Versiyonları yükler."""
        try:
            with open(self.versions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_versions(self, versions: Dict):
        """Versiyonları kaydeder."""
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)

