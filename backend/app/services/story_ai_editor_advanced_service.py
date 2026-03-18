from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryAiEditorAdvancedService:
    """Hikaye AI editör servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.edits_file = os.path.join(settings.STORAGE_PATH, "ai_edits.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.edits_file):
            with open(self.edits_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def edit_story(
        self,
        story_id: str,
        story_text: str,
        edit_instruction: str,
        edit_type: str = "general"
    ) -> Dict:
        """Hikayeyi düzenler."""
        edit_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi şu talimata göre düzenle:
{edit_instruction}

Hikaye:
{story_text}

Düzenlenmiş versiyonu ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye editörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        edited_text = response.choices[0].message.content
        
        edit_record = {
            "edit_id": edit_id,
            "story_id": story_id,
            "edit_type": edit_type,
            "edit_instruction": edit_instruction,
            "original_text": story_text,
            "edited_text": edited_text,
            "created_at": datetime.now().isoformat()
        }
        
        edits = self._load_edits()
        edits.append(edit_record)
        self._save_edits(edits)
        
        return {
            "edit_id": edit_id,
            "edited_text": edited_text,
            "changes": self._identify_changes(story_text, edited_text)
        }
    
    async def improve_flow(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikaye akışını iyileştirir."""
        prompt = f"""Aşağıdaki hikayenin akışını iyileştir. 
Geçişleri daha yumuşak, olay örgüsünü daha tutarlı yap:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye akış uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        improved_text = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "improved_text": improved_text,
            "improvement_type": "flow"
        }
    
    async def enhance_dialogue(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Diyalogları geliştirir."""
        prompt = f"""Aşağıdaki hikayedeki diyalogları daha doğal ve karakteristik hale getir:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir diyalog uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        enhanced_text = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "enhanced_text": enhanced_text,
            "improvement_type": "dialogue"
        }
    
    def _identify_changes(self, original: str, edited: str) -> List[str]:
        """Değişiklikleri belirler."""
        changes = []
        
        if len(edited) > len(original) * 1.1:
            changes.append("Metin genişletildi")
        elif len(edited) < len(original) * 0.9:
            changes.append("Metin kısaltıldı")
        
        original_words = set(original.lower().split())
        edited_words = set(edited.lower().split())
        
        new_words = edited_words - original_words
        if len(new_words) > 10:
            changes.append("Yeni kelimeler eklendi")
        
        return changes if changes else ["Metin düzenlendi"]
    
    def _load_edits(self) -> List[Dict]:
        """Düzenlemeleri yükler."""
        try:
            with open(self.edits_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_edits(self, edits: List[Dict]):
        """Düzenlemeleri kaydeder."""
        with open(self.edits_file, 'w', encoding='utf-8') as f:
            json.dump(edits, f, ensure_ascii=False, indent=2)

