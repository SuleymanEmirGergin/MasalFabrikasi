from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryMoralAdderService:
    """Hikaye içerik ders ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.morals_file = os.path.join(settings.STORAGE_PATH, "story_morals.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.morals_file):
            with open(self.morals_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_moral(
        self,
        story_id: str,
        story_text: str,
        moral_theme: Optional[str] = None
    ) -> Dict:
        """Hikayeye ahlaki ders ekler."""
        moral_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeye ahlaki bir ders ekle.
{f"Tema: {moral_theme}" if moral_theme else "Hikayeden uygun bir ders çıkar"}:

{story_text}

Dersi hikayeye doğal bir şekilde entegre et."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir ahlaki ders uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        moral_text = response.choices[0].message.content
        
        return {
            "moral_id": moral_id,
            "moral_text": moral_text,
            "moral_theme": moral_theme or "genel"
        }
    
    def _load_morals(self) -> List[Dict]:
        """Dersleri yükler."""
        try:
            with open(self.morals_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_morals(self, morals: List[Dict]):
        """Dersleri kaydeder."""
        with open(self.morals_file, 'w', encoding='utf-8') as f:
            json.dump(morals, f, ensure_ascii=False, indent=2)

