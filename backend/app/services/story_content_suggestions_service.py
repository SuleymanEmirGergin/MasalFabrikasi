from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentSuggestionsService:
    """Hikaye içerik önerileri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.suggestions_file = os.path.join(settings.STORAGE_PATH, "content_suggestions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.suggestions_file):
            with open(self.suggestions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def suggest_next_content(
        self,
        story_id: str,
        current_text: str,
        suggestion_type: str = "continuation"
    ) -> Dict:
        """Sonraki içerik önerileri."""
        suggestion_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeye devam etmek için 3 farklı öneri sun:

{current_text}

Her öneri farklı bir yöne gitsin."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye yazım asistanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=600
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Önerileri parse et
        suggestions = self._parse_suggestions(suggestions_text)
        
        suggestion = {
            "suggestion_id": suggestion_id,
            "story_id": story_id,
            "suggestion_type": suggestion_type,
            "suggestions": suggestions,
            "created_at": datetime.now().isoformat()
        }
        
        suggestions_list = self._load_suggestions()
        suggestions_list.append(suggestion)
        self._save_suggestions(suggestions_list)
        
        return {
            "suggestion_id": suggestion_id,
            "suggestions": suggestions,
            "suggestions_count": len(suggestions)
        }
    
    async def suggest_improvements(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """İyileştirme önerileri."""
        prompt = f"""Aşağıdaki hikayeyi analiz et ve iyileştirme önerileri sun:

{story_text}

5 farklı iyileştirme önerisi ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=800
        )
        
        improvements_text = response.choices[0].message.content
        
        improvements = self._parse_suggestions(improvements_text)
        
        return {
            "story_id": story_id,
            "improvements": improvements,
            "improvements_count": len(improvements)
        }
    
    async def suggest_characters(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Karakter önerileri."""
        prompt = f"""Aşağıdaki hikayeye uygun yeni karakterler öner:

{story_text}

Her karakter için kısa bir açıklama ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir karakter yaratma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        characters_text = response.choices[0].message.content
        
        characters = self._parse_suggestions(characters_text)
        
        return {
            "story_id": story_id,
            "characters": characters,
            "characters_count": len(characters)
        }
    
    def _parse_suggestions(self, text: str) -> List[str]:
        """Önerileri parse eder."""
        suggestions = []
        lines = text.split('\n')
        
        for line in lines:
            if line.strip() and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                suggestion = line.strip().lstrip('1234567890.-• ').strip()
                if suggestion and len(suggestion) > 10:
                    suggestions.append(suggestion)
        
        return suggestions[:10] if suggestions else [text[:200]]
    
    def _load_suggestions(self) -> List[Dict]:
        """Önerileri yükler."""
        try:
            with open(self.suggestions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_suggestions(self, suggestions: List[Dict]):
        """Önerileri kaydeder."""
        with open(self.suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=2)

