from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryToneAdjusterService:
    """Hikaye içerik ton ayarlama servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.tone_adjustments_file = os.path.join(settings.STORAGE_PATH, "tone_adjustments.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.tone_adjustments_file):
            with open(self.tone_adjustments_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def adjust_tone(
        self,
        story_id: str,
        story_text: str,
        target_tone: str  # "light", "serious", "playful", "mysterious", "warm"
    ) -> Dict:
        """Hikaye tonunu ayarlar."""
        tone_id = str(uuid.uuid4())
        
        tone_descriptions = {
            "light": "Hafif ve neşeli bir ton",
            "serious": "Ciddi ve ağırbaşlı bir ton",
            "playful": "Oyunbaz ve eğlenceli bir ton",
            "mysterious": "Gizemli ve esrarengiz bir ton",
            "warm": "Sıcak ve samimi bir ton"
        }
        
        prompt = f"""Aşağıdaki hikayenin tonunu {tone_descriptions.get(target_tone, 'farklı bir tona')} ayarla:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir ton ayarlama uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        adjusted_text = response.choices[0].message.content
        
        return {
            "tone_id": tone_id,
            "adjusted_text": adjusted_text,
            "target_tone": target_tone
        }
    
    def _load_tone_adjustments(self) -> List[Dict]:
        """Ton ayarlamalarını yükler."""
        try:
            with open(self.tone_adjustments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_tone_adjustments(self, tone_adjustments: List[Dict]):
        """Ton ayarlamalarını kaydeder."""
        with open(self.tone_adjustments_file, 'w', encoding='utf-8') as f:
            json.dump(tone_adjustments, f, ensure_ascii=False, indent=2)

