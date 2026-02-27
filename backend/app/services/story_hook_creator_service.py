from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryHookCreatorService:
    """Hikaye kanca (hook) oluşturma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.hooks_file = os.path.join(settings.STORAGE_PATH, "hooks.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.hooks_file):
            with open(self.hooks_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_hook(self, story_id: str, story_text: str, hook_type: str = "question") -> Dict:
        hook_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeye {hook_type} tipinde ilgi çekici bir başlangıç ekle:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir kanca yaratma uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.8, max_tokens=500
        )
        hook = response.choices[0].message.content
        return {"hook_id": hook_id, "hook": hook, "hook_type": hook_type}
    
    def _load_hooks(self) -> List[Dict]:
        try:
            with open(self.hooks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_hooks(self, hooks: List[Dict]):
        with open(self.hooks_file, 'w', encoding='utf-8') as f:
            json.dump(hooks, f, ensure_ascii=False, indent=2)

