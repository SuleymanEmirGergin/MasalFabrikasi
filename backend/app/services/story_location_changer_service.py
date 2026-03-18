from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryLocationChangerService:
    """Hikaye içerik mekan değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.location_changes_file = os.path.join(settings.STORAGE_PATH, "location_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.location_changes_file):
            with open(self.location_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_location(
        self,
        story_id: str,
        story_text: str,
        new_location: str
    ) -> Dict:
        """Hikaye mekanını değiştirir."""
        location_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayenin mekanını '{new_location}' olarak değiştir:

{story_text}

Yeni mekana uygun detaylar ekle."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir mekan değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        location_changed_text = response.choices[0].message.content
        
        return {
            "location_id": location_id,
            "location_changed_text": location_changed_text,
            "new_location": new_location
        }
    
    def _load_location_changes(self) -> List[Dict]:
        """Mekan değişikliklerini yükler."""
        try:
            with open(self.location_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_location_changes(self, location_changes: List[Dict]):
        """Mekan değişikliklerini kaydeder."""
        with open(self.location_changes_file, 'w', encoding='utf-8') as f:
            json.dump(location_changes, f, ensure_ascii=False, indent=2)

