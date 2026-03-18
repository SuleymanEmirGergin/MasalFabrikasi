from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryPlagiarismCheckerService:
    """Hikaye intihal kontrolü servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.checks_file = os.path.join(settings.STORAGE_PATH, "plagiarism_checks.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.checks_file):
            with open(self.checks_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def check_plagiarism(self, story_id: str, story_text: str) -> Dict:
        check_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki metinde intihal var mı kontrol et:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir intihal kontrol uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500
        )
        result = response.choices[0].message.content
        similarity = self._calculate_similarity(story_text)
        return {"check_id": check_id, "is_original": similarity < 0.7, "similarity": similarity, "result": result}
    
    def _calculate_similarity(self, text: str) -> float:
        return 0.3  # Basit implementasyon
    
    def _load_checks(self) -> List[Dict]:
        try:
            with open(self.checks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_checks(self, checks: List[Dict]):
        with open(self.checks_file, 'w', encoding='utf-8') as f:
            json.dump(checks, f, ensure_ascii=False, indent=2)

