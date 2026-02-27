from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryConflictAdderService:
    """Hikaye içerik çatışma ekleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.conflicts_file = os.path.join(settings.STORAGE_PATH, "story_conflicts.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.conflicts_file):
            with open(self.conflicts_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_conflict(
        self,
        story_id: str,
        story_text: str,
        conflict_type: str  # "internal", "external", "character", "society", "nature"
    ) -> Dict:
        """Hikayeye çatışma ekler."""
        conflict_id = str(uuid.uuid4())
        
        conflict_descriptions = {
            "internal": "İçsel çatışma",
            "external": "Dışsal çatışma",
            "character": "Karakterler arası çatışma",
            "society": "Toplumsal çatışma",
            "nature": "Doğa ile çatışma"
        }
        
        prompt = f"""Aşağıdaki hikayeye {conflict_descriptions.get(conflict_type, 'çatışma')} ekle:

{story_text}

Çatışmayı hikayeye doğal bir şekilde entegre et."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye çatışma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        conflict_text = response.choices[0].message.content
        
        return {
            "conflict_id": conflict_id,
            "conflict_text": conflict_text,
            "conflict_type": conflict_type
        }
    
    def _load_conflicts(self) -> List[Dict]:
        """Çatışmaları yükler."""
        try:
            with open(self.conflicts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_conflicts(self, conflicts: List[Dict]):
        """Çatışmaları kaydeder."""
        with open(self.conflicts_file, 'w', encoding='utf-8') as f:
            json.dump(conflicts, f, ensure_ascii=False, indent=2)

