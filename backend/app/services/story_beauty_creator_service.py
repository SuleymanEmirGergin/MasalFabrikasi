from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime

class StoryBeautyCreatorService:
    """Güzellik yaratma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.file = os.path.join(settings.STORAGE_PATH, "story_beauty_creator_service.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.file):
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def process(self, story_id: str, story_text: str, **kwargs) -> Dict:
        id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeyi güzellik yaratma açısından iyileştir:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir güzellik yaratma uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=2000
        )
        return {"id": id, "result": response.choices[0].message.content}
    
    def _load(self) -> List[Dict]:
        try:
            with open(self.file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save(self, data: List[Dict]):
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
