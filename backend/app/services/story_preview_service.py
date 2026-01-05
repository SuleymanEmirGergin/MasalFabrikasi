from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryPreviewService:
    """Hikaye önizleme ve canlı düzenleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.previews_file = os.path.join(settings.STORAGE_PATH, "story_previews.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.previews_file):
            with open(self.previews_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_preview(
        self,
        story_id: str,
        story_text: str,
        user_id: str
    ) -> Dict:
        """Hikaye önizlemesi oluşturur."""
        preview_id = str(uuid.uuid4())
        preview = {
            "preview_id": preview_id,
            "story_id": story_id,
            "user_id": user_id,
            "original_text": story_text,
            "preview_text": story_text,
            "changes": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        previews = self._load_previews()
        previews.append(preview)
        self._save_previews(previews)
        
        return {
            "preview_id": preview_id,
            "story_id": story_id,
            "preview_text": story_text
        }
    
    async def update_preview(
        self,
        preview_id: str,
        new_text: str
    ) -> Dict:
        """Önizlemeyi günceller."""
        previews = self._load_previews()
        preview = next((p for p in previews if p["preview_id"] == preview_id), None)
        
        if not preview:
            raise ValueError("Önizleme bulunamadı")
        
        change = {
            "timestamp": datetime.now().isoformat(),
            "old_text": preview["preview_text"],
            "new_text": new_text
        }
        
        preview["preview_text"] = new_text
        preview["changes"].append(change)
        preview["updated_at"] = datetime.now().isoformat()
        
        self._save_previews(previews)
        
        return {
            "preview_id": preview_id,
            "preview_text": new_text,
            "changes_count": len(preview["changes"])
        }
    
    async def apply_preview_to_story(
        self,
        preview_id: str
    ) -> Dict:
        """Önizlemeyi hikayeye uygular."""
        previews = self._load_previews()
        preview = next((p for p in previews if p["preview_id"] == preview_id), None)
        
        if not preview:
            raise ValueError("Önizleme bulunamadı")
        
        return {
            "story_id": preview["story_id"],
            "new_text": preview["preview_text"],
            "message": "Önizleme hikayeye uygulandı"
        }
    
    async def get_preview_suggestions(
        self,
        preview_id: str,
        suggestion_type: str = "improvement"
    ) -> List[Dict]:
        """AI ile önizleme önerileri alır."""
        previews = self._load_previews()
        preview = next((p for p in previews if p["preview_id"] == preview_id), None)
        
        if not preview:
            raise ValueError("Önizleme bulunamadı")
        
        prompt = f"""Aşağıdaki hikayeyi analiz et ve {suggestion_type} için öneriler sun:

{preview["preview_text"]}

Önerileri liste halinde ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye editörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        suggestions_text = response.choices[0].message.content
        suggestions = [
            {
                "id": str(uuid.uuid4()),
                "type": suggestion_type,
                "text": line.strip(),
                "created_at": datetime.now().isoformat()
            }
            for line in suggestions_text.split("\n") if line.strip()
        ]
        
        return suggestions
    
    def _load_previews(self) -> List[Dict]:
        """Önizlemeleri yükler."""
        try:
            with open(self.previews_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_previews(self, previews: List[Dict]):
        """Önizlemeleri kaydeder."""
        with open(self.previews_file, 'w', encoding='utf-8') as f:
            json.dump(previews, f, ensure_ascii=False, indent=2)
    
    async def get_preview(self, preview_id: str) -> Optional[Dict]:
        """Önizlemeyi getirir."""
        previews = self._load_previews()
        return next((p for p in previews if p["preview_id"] == preview_id), None)

