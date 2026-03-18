from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryClimaxEnhancerService:
    """Hikaye doruk noktası geliştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.climaxes_file = os.path.join(settings.STORAGE_PATH, "climax_enhancements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.climaxes_file):
            with open(self.climaxes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def enhance_climax(self, story_id: str, story_text: str) -> Dict:
        climax_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayenin doruk noktasını güçlendir:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir doruk noktası uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.8, max_tokens=2000
        )
        enhanced = response.choices[0].message.content
        return {"climax_id": climax_id, "enhanced_text": enhanced}
    
    def _load_climaxes(self) -> List[Dict]:
        try:
            with open(self.climaxes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_climaxes(self, climaxes: List[Dict]):
        with open(self.climaxes_file, 'w', encoding='utf-8') as f:
            json.dump(climaxes, f, ensure_ascii=False, indent=2)

