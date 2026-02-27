from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryVocabularyEnhancerService:
    """Hikaye kelime hazinesi geliştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.enhancements_file = os.path.join(settings.STORAGE_PATH, "vocabulary_enhancements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.enhancements_file):
            with open(self.enhancements_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def enhance_vocabulary(self, story_id: str, story_text: str, enhancement_level: str = "moderate") -> Dict:
        enh_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayenin kelime hazinesini {enhancement_level} seviyede geliştir:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir kelime hazinesi uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=2000
        )
        enhanced = response.choices[0].message.content
        return {"enh_id": enh_id, "enhanced_text": enhanced, "level": enhancement_level}
    
    def _load_enhancements(self) -> List[Dict]:
        try:
            with open(self.enhancements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_enhancements(self, enhancements: List[Dict]):
        with open(self.enhancements_file, 'w', encoding='utf-8') as f:
            json.dump(enhancements, f, ensure_ascii=False, indent=2)

