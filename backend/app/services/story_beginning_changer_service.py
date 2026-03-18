from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryBeginningChangerService:
    """Hikaye içerik başlangıç değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.beginning_changes_file = os.path.join(settings.STORAGE_PATH, "beginning_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.beginning_changes_file):
            with open(self.beginning_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_beginning(
        self,
        story_id: str,
        story_text: str,
        beginning_style: str  # "action", "mystery", "dialogue", "description", "question"
    ) -> Dict:
        """Hikaye başlangıcını değiştirir."""
        beginning_id = str(uuid.uuid4())
        
        style_descriptions = {
            "action": "Aksiyonla başlayan",
            "mystery": "Gizemle başlayan",
            "dialogue": "Diyalogla başlayan",
            "description": "Betimlemeyle başlayan",
            "question": "Sorularla başlayan"
        }
        
        prompt = f"""Aşağıdaki hikayenin başlangıcını {style_descriptions.get(beginning_style, 'farklı bir stille')} değiştir:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye başlangıcı uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        new_beginning_text = response.choices[0].message.content
        
        return {
            "beginning_id": beginning_id,
            "new_beginning": new_beginning_text,
            "beginning_style": beginning_style
        }
    
    def _load_beginning_changes(self) -> List[Dict]:
        """Başlangıç değişikliklerini yükler."""
        try:
            with open(self.beginning_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_beginning_changes(self, beginning_changes: List[Dict]):
        """Başlangıç değişikliklerini kaydeder."""
        with open(self.beginning_changes_file, 'w', encoding='utf-8') as f:
            json.dump(beginning_changes, f, ensure_ascii=False, indent=2)

