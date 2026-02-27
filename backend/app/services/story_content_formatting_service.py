from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentFormattingService:
    """Hikaye içerik formatlama servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.formattings_file = os.path.join(settings.STORAGE_PATH, "content_formattings.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.formattings_file):
            with open(self.formattings_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def format_story(
        self,
        story_id: str,
        story_text: str,
        format_style: str = "standard"
    ) -> Dict:
        """Hikayeyi formatlar."""
        formatting_id = str(uuid.uuid4())
        
        format_styles = {
            "standard": "Standart formatlama",
            "paragraph": "Paragraf bazlı formatlama",
            "dialogue": "Diyalog odaklı formatlama",
            "descriptive": "Betimleme odaklı formatlama"
        }
        
        prompt = f"""Aşağıdaki hikayeyi {format_styles.get(format_style, 'standart')} formatla:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir formatlama uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        formatted_text = response.choices[0].message.content
        
        return {
            "formatting_id": formatting_id,
            "formatted_text": formatted_text,
            "format_style": format_style
        }
    
    def _load_formattings(self) -> List[Dict]:
        """Formatlamaları yükler."""
        try:
            with open(self.formattings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_formattings(self, formattings: List[Dict]):
        """Formatlamaları kaydeder."""
        with open(self.formattings_file, 'w', encoding='utf-8') as f:
            json.dump(formattings, f, ensure_ascii=False, indent=2)

