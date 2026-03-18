from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryEndingChangerService:
    """Hikaye içerik son değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.ending_changes_file = os.path.join(settings.STORAGE_PATH, "ending_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.ending_changes_file):
            with open(self.ending_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_ending(
        self,
        story_id: str,
        story_text: str,
        ending_type: str  # "happy", "sad", "open", "twist", "moral"
    ) -> Dict:
        """Hikaye sonunu değiştirir."""
        ending_id = str(uuid.uuid4())
        
        ending_descriptions = {
            "happy": "Mutlu bir son",
            "sad": "Hüzünlü bir son",
            "open": "Açık uçlu bir son",
            "twist": "Sürprizli bir son",
            "moral": "Ahlaki ders veren bir son"
        }
        
        prompt = f"""Aşağıdaki hikayenin sonunu {ending_descriptions.get(ending_type, 'farklı bir sona')} değiştir:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye sonu değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        new_ending_text = response.choices[0].message.content
        
        return {
            "ending_id": ending_id,
            "new_ending": new_ending_text,
            "ending_type": ending_type
        }
    
    def _load_ending_changes(self) -> List[Dict]:
        """Son değişikliklerini yükler."""
        try:
            with open(self.ending_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_ending_changes(self, ending_changes: List[Dict]):
        """Son değişikliklerini kaydeder."""
        with open(self.ending_changes_file, 'w', encoding='utf-8') as f:
            json.dump(ending_changes, f, ensure_ascii=False, indent=2)

