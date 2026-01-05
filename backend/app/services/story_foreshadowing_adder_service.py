from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryForeshadowingAdderService:
    """Hikaye önsezi ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.foreshadowings_file = os.path.join(settings.STORAGE_PATH, "foreshadowings.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.foreshadowings_file):
            with open(self.foreshadowings_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_foreshadowing(self, story_id: str, story_text: str) -> Dict:
        foreshadow_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeye önsezi (foreshadowing) ekle:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir önsezi uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=2000
        )
        enhanced = response.choices[0].message.content
        return {"foreshadow_id": foreshadow_id, "enhanced_text": enhanced}
    
    def _load_foreshadowings(self) -> List[Dict]:
        try:
            with open(self.foreshadowings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_foreshadowings(self, foreshadowings: List[Dict]):
        with open(self.foreshadowings_file, 'w', encoding='utf-8') as f:
            json.dump(foreshadowings, f, ensure_ascii=False, indent=2)

