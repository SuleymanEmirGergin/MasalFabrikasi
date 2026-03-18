from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryQualityScorerService:
    """Hikaye kalite skorlama servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.scores_file = os.path.join(settings.STORAGE_PATH, "quality_scores.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.scores_file):
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def score_story(self, story_id: str, story_text: str) -> Dict:
        score_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayeyi 1-10 arası puanla:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir hikaye değerlendirme uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.5, max_tokens=500
        )
        score_text = response.choices[0].message.content
        score = self._extract_score(score_text)
        return {"score_id": score_id, "overall_score": score, "details": score_text}
    
    def _extract_score(self, text: str) -> float:
        import re
        numbers = re.findall(r'\d+', text)
        return float(numbers[0]) if numbers else 7.0
    
    def _load_scores(self) -> List[Dict]:
        try:
            with open(self.scores_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_scores(self, scores: List[Dict]):
        with open(self.scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)

