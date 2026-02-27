from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryPerspectiveChangerService:
    """Hikaye içerik perspektif değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.perspective_changes_file = os.path.join(settings.STORAGE_PATH, "perspective_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.perspective_changes_file):
            with open(self.perspective_changes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def change_perspective(
        self,
        story_id: str,
        story_text: str,
        new_perspective: str  # "first_person", "third_person", "second_person", "omniscient"
    ) -> Dict:
        """Hikaye perspektifini değiştirir."""
        perspective_id = str(uuid.uuid4())
        
        perspective_descriptions = {
            "first_person": "Birinci tekil şahıs (ben)",
            "third_person": "Üçüncü tekil şahıs (o)",
            "second_person": "İkinci tekil şahıs (sen)",
            "omniscient": "Her şeyi bilen anlatıcı"
        }
        
        prompt = f"""Aşağıdaki hikayeyi {perspective_descriptions.get(new_perspective, 'farklı bir perspektife')} dönüştür:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir perspektif değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        perspective_text = response.choices[0].message.content
        
        return {
            "perspective_id": perspective_id,
            "perspective_text": perspective_text,
            "new_perspective": new_perspective
        }
    
    def _load_perspective_changes(self) -> List[Dict]:
        """Perspektif değişikliklerini yükler."""
        try:
            with open(self.perspective_changes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_perspective_changes(self, perspective_changes: List[Dict]):
        """Perspektif değişikliklerini kaydeder."""
        with open(self.perspective_changes_file, 'w', encoding='utf-8') as f:
            json.dump(perspective_changes, f, ensure_ascii=False, indent=2)

