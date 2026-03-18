from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryRepetitionOptimizerService:
    """Hikaye tekrar optimizasyonu servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.repetitions_file = os.path.join(settings.STORAGE_PATH, "repetitions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.repetitions_file):
            with open(self.repetitions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def optimize_repetition(self, story_id: str, story_text: str) -> Dict:
        rep_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayedeki gereksiz tekrarları azalt, gerekli tekrarları koru:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir tekrar optimizasyon uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.6, max_tokens=2000
        )
        optimized = response.choices[0].message.content
        return {"rep_id": rep_id, "optimized_text": optimized}
    
    def _load_repetitions(self) -> List[Dict]:
        try:
            with open(self.repetitions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_repetitions(self, repetitions: List[Dict]):
        with open(self.repetitions_file, 'w', encoding='utf-8') as f:
            json.dump(repetitions, f, ensure_ascii=False, indent=2)

