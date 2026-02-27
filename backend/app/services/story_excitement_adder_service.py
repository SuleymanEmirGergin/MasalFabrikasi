from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryExcitementAdderService:
    """Hikaye içerik heyecan ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.excitements_file = os.path.join(settings.STORAGE_PATH, "story_excitements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.excitements_file):
            with open(self.excitements_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_excitement(
        self,
        story_id: str,
        story_text: str,
        excitement_level: str  # "mild", "moderate", "high", "extreme"
    ) -> Dict:
        """Hikayeye heyecan ekler."""
        excitement_id = str(uuid.uuid4())
        
        level_descriptions = {
            "mild": "Hafif heyecan",
            "moderate": "Orta seviye heyecan",
            "high": "Yüksek heyecan",
            "extreme": "Aşırı heyecan"
        }
        
        prompt = f"""Aşağıdaki hikayeye {level_descriptions.get(excitement_level, 'heyecan')} ekle:

{story_text}

Heyecanı hikayeye doğal bir şekilde entegre et."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir heyecan yaratma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        excitement_text = response.choices[0].message.content
        
        return {
            "excitement_id": excitement_id,
            "excitement_text": excitement_text,
            "excitement_level": excitement_level
        }
    
    def _load_excitements(self) -> List[Dict]:
        """Heyecanları yükler."""
        try:
            with open(self.excitements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_excitements(self, excitements: List[Dict]):
        """Heyecanları kaydeder."""
        with open(self.excitements_file, 'w', encoding='utf-8') as f:
            json.dump(excitements, f, ensure_ascii=False, indent=2)

