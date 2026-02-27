from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryThemeEnhancerService:
    """Hikaye tema geliştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.themes_file = os.path.join(settings.STORAGE_PATH, "theme_enhancements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.themes_file):
            with open(self.themes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def enhance_theme(self, story_id: str, story_text: str, theme: Optional[str] = None) -> Dict:
        theme_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayenin temasını güçlendir{f': {theme}' if theme else ''}:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir tema uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=2000
        )
        enhanced = response.choices[0].message.content
        return {"theme_id": theme_id, "enhanced_text": enhanced, "theme": theme}
    
    def _load_themes(self) -> List[Dict]:
        try:
            with open(self.themes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_themes(self, themes: List[Dict]):
        with open(self.themes_file, 'w', encoding='utf-8') as f:
            json.dump(themes, f, ensure_ascii=False, indent=2)

