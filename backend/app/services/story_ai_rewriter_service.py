from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryAiRewriterService:
    """Hikaye AI yeniden yazma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.rewrites_file = os.path.join(settings.STORAGE_PATH, "ai_rewrites.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.rewrites_file):
            with open(self.rewrites_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def rewrite_story(self, story_id: str, story_text: str, rewrite_style: str = "improved") -> Dict:
        rewrite_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeyi {rewrite_style} şekilde yeniden yaz:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir hikaye yazarısın."}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=2000
        )
        rewritten = response.choices[0].message.content
        return {"rewrite_id": rewrite_id, "rewritten_text": rewritten}
    
    def _load_rewrites(self) -> List[Dict]:
        try:
            with open(self.rewrites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_rewrites(self, rewrites: List[Dict]):
        with open(self.rewrites_file, 'w', encoding='utf-8') as f:
            json.dump(rewrites, f, ensure_ascii=False, indent=2)

