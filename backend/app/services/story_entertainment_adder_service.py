from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryEntertainmentAdderService:
    """Hikaye içerik eğlence ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.entertainments_file = os.path.join(settings.STORAGE_PATH, "story_entertainments.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.entertainments_file):
            with open(self.entertainments_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_entertainment(
        self,
        story_id: str,
        story_text: str,
        entertainment_type: str  # "humor", "jokes", "wordplay", "situations", "characters"
    ) -> Dict:
        """Hikayeye eğlence öğeleri ekler."""
        entertainment_id = str(uuid.uuid4())
        
        entertainment_descriptions = {
            "humor": "Mizah ekle",
            "jokes": "Şakalar ekle",
            "wordplay": "Kelime oyunları ekle",
            "situations": "Komik durumlar ekle",
            "characters": "Eğlenceli karakterler ekle"
        }
        
        prompt = f"""Aşağıdaki hikayeye {entertainment_descriptions.get(entertainment_type, 'eğlence')} ekle:

{story_text}

Eğlenceyi hikayeye doğal bir şekilde entegre et."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir eğlence uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=2000
        )
        
        entertainment_text = response.choices[0].message.content
        
        return {
            "entertainment_id": entertainment_id,
            "entertainment_text": entertainment_text,
            "entertainment_type": entertainment_type
        }
    
    def _load_entertainments(self) -> List[Dict]:
        """Eğlenceleri yükler."""
        try:
            with open(self.entertainments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_entertainments(self, entertainments: List[Dict]):
        """Eğlenceleri kaydeder."""
        with open(self.entertainments_file, 'w', encoding='utf-8') as f:
            json.dump(entertainments, f, ensure_ascii=False, indent=2)

