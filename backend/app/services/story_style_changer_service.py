from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryStyleChangerService:
    """Hikaye içerik stil değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.style_changes_file = os.path.join(settings.STORAGE_PATH, "style_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.style_changes_file):
            with open(self.style_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_style(
        self,
        story_id: str,
        story_text: str,
        new_style: str  # "formal", "casual", "poetic", "humorous", "dramatic"
    ) -> Dict:
        """Hikaye stilini değiştirir."""
        style_id = str(uuid.uuid4())
        
        style_descriptions = {
            "formal": "Resmi ve ciddi bir dil",
            "casual": "Günlük ve samimi bir dil",
            "poetic": "Şiirsel ve lirik bir dil",
            "humorous": "Eğlenceli ve komik bir dil",
            "dramatic": "Dramatik ve duygusal bir dil"
        }
        
        prompt = f"""Aşağıdaki hikayeyi {style_descriptions.get(new_style, 'farklı bir stile')} dönüştür:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir stil değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        styled_text = response.choices[0].message.content
        
        return {
            "style_id": style_id,
            "styled_text": styled_text,
            "new_style": new_style
        }
    
    def _load_style_changes(self) -> List[Dict]:
        """Stil değişikliklerini yükler."""
        try:
            with open(self.style_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_style_changes(self, style_changes: List[Dict]):
        """Stil değişikliklerini kaydeder."""
        with open(self.style_changes_file, 'w', encoding='utf-8') as f:
            json.dump(style_changes, f, ensure_ascii=False, indent=2)

