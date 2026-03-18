from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryMiddleChangerService:
    """Hikaye içerik orta değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.middle_changes_file = os.path.join(settings.STORAGE_PATH, "middle_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.middle_changes_file):
            with open(self.middle_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_middle(
        self,
        story_id: str,
        story_text: str,
        middle_enhancement: str  # "add_obstacle", "add_character", "add_event", "add_dialogue"
    ) -> Dict:
        """Hikaye ortasını değiştirir."""
        middle_id = str(uuid.uuid4())
        
        enhancement_descriptions = {
            "add_obstacle": "Engel ekle",
            "add_character": "Karakter ekle",
            "add_event": "Olay ekle",
            "add_dialogue": "Diyalog ekle"
        }
        
        prompt = f"""Aşağıdaki hikayenin ortasına {enhancement_descriptions.get(middle_enhancement, 'geliştirme')} ekle:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye orta kısmı uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        enhanced_middle_text = response.choices[0].message.content
        
        return {
            "middle_id": middle_id,
            "enhanced_middle": enhanced_middle_text,
            "enhancement_type": middle_enhancement
        }
    
    def _load_middle_changes(self) -> List[Dict]:
        """Orta değişikliklerini yükler."""
        try:
            with open(self.middle_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_middle_changes(self, middle_changes: List[Dict]):
        """Orta değişikliklerini kaydeder."""
        with open(self.middle_changes_file, 'w', encoding='utf-8') as f:
            json.dump(middle_changes, f, ensure_ascii=False, indent=2)

