from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryResolutionAdderService:
    """Hikaye içerik çözüm ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.resolutions_file = os.path.join(settings.STORAGE_PATH, "story_resolutions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.resolutions_file):
            with open(self.resolutions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_resolution(
        self,
        story_id: str,
        story_text: str,
        resolution_type: str  # "happy", "bittersweet", "open", "redemption", "growth"
    ) -> Dict:
        """Hikayeye çözüm ekler."""
        resolution_id = str(uuid.uuid4())
        
        resolution_descriptions = {
            "happy": "Mutlu çözüm",
            "bittersweet": "Acı-tatlı çözüm",
            "open": "Açık uçlu çözüm",
            "redemption": "Kefaret çözümü",
            "growth": "Gelişim çözümü"
        }
        
        prompt = f"""Aşağıdaki hikayeye {resolution_descriptions.get(resolution_type, 'çözüm')} ekle:

{story_text}

Çözümü hikayenin çatışmalarını çözecek şekilde yaz."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye çözüm uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        resolution_text = response.choices[0].message.content
        
        return {
            "resolution_id": resolution_id,
            "resolution_text": resolution_text,
            "resolution_type": resolution_type
        }
    
    def _load_resolutions(self) -> List[Dict]:
        """Çözümleri yükler."""
        try:
            with open(self.resolutions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_resolutions(self, resolutions: List[Dict]):
        """Çözümleri kaydeder."""
        with open(self.resolutions_file, 'w', encoding='utf-8') as f:
            json.dump(resolutions, f, ensure_ascii=False, indent=2)

