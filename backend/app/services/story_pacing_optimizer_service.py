from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryPacingOptimizerService:
    """Hikaye tempo optimizasyonu servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.pacings_file = os.path.join(settings.STORAGE_PATH, "pacing_optimizations.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.pacings_file):
            with open(self.pacings_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def optimize_pacing(self, story_id: str, story_text: str, pacing_type: str = "balanced") -> Dict:
        pacing_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayenin temposunu {pacing_type} şekilde optimize et:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir tempo uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=2000
        )
        optimized = response.choices[0].message.content
        return {"pacing_id": pacing_id, "optimized_text": optimized, "pacing_type": pacing_type}
    
    def _load_pacings(self) -> List[Dict]:
        try:
            with open(self.pacings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_pacings(self, pacings: List[Dict]):
        with open(self.pacings_file, 'w', encoding='utf-8') as f:
            json.dump(pacings, f, ensure_ascii=False, indent=2)

