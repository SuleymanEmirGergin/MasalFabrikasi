from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryImageryEnhancerService:
    """Hikaye görsel betimleme geliştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.imageries_file = os.path.join(settings.STORAGE_PATH, "imageries.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.imageries_file):
            with open(self.imageries_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def enhance_imagery(self, story_id: str, story_text: str) -> Dict:
        imagery_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeye görsel betimlemeler ekle:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir görsel betimleme uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.8, max_tokens=2000
        )
        enhanced = response.choices[0].message.content
        return {"imagery_id": imagery_id, "enhanced_text": enhanced}
    
    def _load_imageries(self) -> List[Dict]:
        try:
            with open(self.imageries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_imageries(self, imageries: List[Dict]):
        with open(self.imageries_file, 'w', encoding='utf-8') as f:
            json.dump(imageries, f, ensure_ascii=False, indent=2)

