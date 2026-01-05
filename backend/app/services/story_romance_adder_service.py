from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryRomanceAdderService:
    """Hikaye içerik romantizm ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.romances_file = os.path.join(settings.STORAGE_PATH, "story_romances.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.romances_file):
            with open(self.romances_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_romance(
        self,
        story_id: str,
        story_text: str,
        romance_level: str  # "subtle", "moderate", "romantic", "sweet"
    ) -> Dict:
        """Hikayeye romantizm ekler."""
        romance_id = str(uuid.uuid4())
        
        level_descriptions = {
            "subtle": "İnce romantizm",
            "moderate": "Orta seviye romantizm",
            "romantic": "Romantik öğeler",
            "sweet": "Tatlı romantizm"
        }
        
        prompt = f"""Aşağıdaki hikayeye {level_descriptions.get(romance_level, 'romantizm')} ekle.
Çocuklar için uygun ve masum bir şekilde:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir romantizm uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        romance_text = response.choices[0].message.content
        
        return {
            "romance_id": romance_id,
            "romance_text": romance_text,
            "romance_level": romance_level
        }
    
    def _load_romances(self) -> List[Dict]:
        """Romantizmleri yükler."""
        try:
            with open(self.romances_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_romances(self, romances: List[Dict]):
        """Romantizmleri kaydeder."""
        with open(self.romances_file, 'w', encoding='utf-8') as f:
            json.dump(romances, f, ensure_ascii=False, indent=2)

