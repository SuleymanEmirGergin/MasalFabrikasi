from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryCharacterReplacerService:
    """Hikaye içerik karakter değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.character_replacements_file = os.path.join(settings.STORAGE_PATH, "character_replacements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.character_replacements_file):
            with open(self.character_replacements_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def replace_character(
        self,
        story_id: str,
        story_text: str,
        old_character: str,
        new_character: str
    ) -> Dict:
        """Karakteri değiştirir."""
        replacement_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayede '{old_character}' karakterini '{new_character}' ile değiştir.
Karakterin özelliklerini ve rollerini yeni karaktere uyarla:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir karakter değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        replaced_text = response.choices[0].message.content
        
        return {
            "replacement_id": replacement_id,
            "replaced_text": replaced_text,
            "old_character": old_character,
            "new_character": new_character
        }
    
    def _load_replacements(self) -> List[Dict]:
        """Değiştirmeleri yükler."""
        try:
            with open(self.character_replacements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_replacements(self, replacements: List[Dict]):
        """Değiştirmeleri kaydeder."""
        with open(self.character_replacements_file, 'w', encoding='utf-8') as f:
            json.dump(replacements, f, ensure_ascii=False, indent=2)

