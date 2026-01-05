from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryLanguageSimplifierService:
    """Hikaye dil basitleştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.simplifications_file = os.path.join(settings.STORAGE_PATH, "language_simplifications.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.simplifications_file):
            with open(self.simplifications_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def simplify_language(self, story_id: str, story_text: str, target_age: int = 7) -> Dict:
        simp_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeyi {target_age} yaşındaki çocuklar için basitleştir:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir dil basitleştirme uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.6, max_tokens=2000
        )
        simplified = response.choices[0].message.content
        return {"simp_id": simp_id, "simplified_text": simplified, "target_age": target_age}
    
    def _load_simplifications(self) -> List[Dict]:
        try:
            with open(self.simplifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_simplifications(self, simplifications: List[Dict]):
        with open(self.simplifications_file, 'w', encoding='utf-8') as f:
            json.dump(simplifications, f, ensure_ascii=False, indent=2)

