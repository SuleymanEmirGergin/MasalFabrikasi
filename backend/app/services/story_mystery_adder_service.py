from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryMysteryAdderService:
    """Hikaye içerik gizem ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.mysteries_file = os.path.join(settings.STORAGE_PATH, "story_mysteries.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.mysteries_file):
            with open(self.mysteries_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_mystery(
        self,
        story_id: str,
        story_text: str,
        mystery_type: str  # "puzzle", "secret", "riddle", "clue", "enigma"
    ) -> Dict:
        """Hikayeye gizem ekler."""
        mystery_id = str(uuid.uuid4())
        
        mystery_descriptions = {
            "puzzle": "Bulmaca ekle",
            "secret": "Gizem ekle",
            "riddle": "Bilmece ekle",
            "clue": "İpucu ekle",
            "enigma": "Esrarengiz öğe ekle"
        }
        
        prompt = f"""Aşağıdaki hikayeye {mystery_descriptions.get(mystery_type, 'gizem')} ekle:

{story_text}

Gizemi hikayeye doğal bir şekilde entegre et."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir gizem yaratma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        mystery_text = response.choices[0].message.content
        
        return {
            "mystery_id": mystery_id,
            "mystery_text": mystery_text,
            "mystery_type": mystery_type
        }
    
    def _load_mysteries(self) -> List[Dict]:
        """Gizemleri yükler."""
        try:
            with open(self.mysteries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_mysteries(self, mysteries: List[Dict]):
        """Gizemleri kaydeder."""
        with open(self.mysteries_file, 'w', encoding='utf-8') as f:
            json.dump(mysteries, f, ensure_ascii=False, indent=2)

