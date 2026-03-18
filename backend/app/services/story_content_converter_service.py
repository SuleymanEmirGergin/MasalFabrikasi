from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentConverterService:
    """Hikaye içerik dönüştürme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.conversions_file = os.path.join(settings.STORAGE_PATH, "content_conversions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.conversions_file):
            with open(self.conversions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def convert_format(
        self,
        story_id: str,
        story_text: str,
        target_format: str  # "poem", "script", "letter", "diary", "news"
    ) -> Dict:
        """Hikayeyi farklı formata dönüştürür."""
        conversion_id = str(uuid.uuid4())
        
        format_instructions = {
            "poem": "Şiir formatına dönüştür",
            "script": "Senaryo formatına dönüştür",
            "letter": "Mektup formatına dönüştür",
            "diary": "Günlük formatına dönüştür",
            "news": "Haber formatına dönüştür"
        }
        
        prompt = f"""Aşağıdaki hikayeyi {format_instructions.get(target_format, 'farklı formata')} dönüştür:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir format dönüştürme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        converted_text = response.choices[0].message.content
        
        conversion = {
            "conversion_id": conversion_id,
            "story_id": story_id,
            "target_format": target_format,
            "original_text": story_text,
            "converted_text": converted_text,
            "created_at": datetime.now().isoformat()
        }
        
        conversions = self._load_conversions()
        conversions.append(conversion)
        self._save_conversions(conversions)
        
        return {
            "conversion_id": conversion_id,
            "converted_text": converted_text,
            "target_format": target_format
        }
    
    def _load_conversions(self) -> List[Dict]:
        """Dönüştürmeleri yükler."""
        try:
            with open(self.conversions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_conversions(self, conversions: List[Dict]):
        """Dönüştürmeleri kaydeder."""
        with open(self.conversions_file, 'w', encoding='utf-8') as f:
            json.dump(conversions, f, ensure_ascii=False, indent=2)

