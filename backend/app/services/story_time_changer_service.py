from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryTimeChangerService:
    """Hikaye içerik zaman değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.time_changes_file = os.path.join(settings.STORAGE_PATH, "time_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.time_changes_file):
            with open(self.time_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_time_period(
        self,
        story_id: str,
        story_text: str,
        new_time_period: str  # "past", "present", "future", "medieval", "modern"
    ) -> Dict:
        """Hikaye zaman periyodunu değiştirir."""
        time_id = str(uuid.uuid4())
        
        time_descriptions = {
            "past": "Geçmiş zaman",
            "present": "Şimdiki zaman",
            "future": "Gelecek zaman",
            "medieval": "Ortaçağ dönemi",
            "modern": "Modern dönem"
        }
        
        prompt = f"""Aşağıdaki hikayeyi {time_descriptions.get(new_time_period, 'farklı bir zaman periyoduna')} taşı:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir zaman değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        time_changed_text = response.choices[0].message.content
        
        return {
            "time_id": time_id,
            "time_changed_text": time_changed_text,
            "new_time_period": new_time_period
        }
    
    def _load_time_changes(self) -> List[Dict]:
        """Zaman değişikliklerini yükler."""
        try:
            with open(self.time_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_time_changes(self, time_changes: List[Dict]):
        """Zaman değişikliklerini kaydeder."""
        with open(self.time_changes_file, 'w', encoding='utf-8') as f:
            json.dump(time_changes, f, ensure_ascii=False, indent=2)

