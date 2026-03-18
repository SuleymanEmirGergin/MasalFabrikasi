from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryVoiceEnhancerService:
    """Hikaye ses geliştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.voices_file = os.path.join(settings.STORAGE_PATH, "voice_enhancements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.voices_file):
            with open(self.voices_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def enhance_voice(self, story_id: str, story_text: str, voice_style: str = "distinctive") -> Dict:
        voice_id = str(uuid.uuid4())
        prompt = f"Aşağıdaki hikayenin anlatım sesini {voice_style} şekilde geliştir:\n\n{story_text}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "system", "content": "Sen bir anlatım sesi uzmanısın."}, {"role": "user", "content": prompt}],
            temperature=0.8, max_tokens=2000
        )
        enhanced = response.choices[0].message.content
        return {"voice_id": voice_id, "enhanced_text": enhanced, "voice_style": voice_style}
    
    def _load_voices(self) -> List[Dict]:
        try:
            with open(self.voices_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    
    def _save_voices(self, voices: List[Dict]):
        with open(self.voices_file, 'w', encoding='utf-8') as f:
            json.dump(voices, f, ensure_ascii=False, indent=2)

