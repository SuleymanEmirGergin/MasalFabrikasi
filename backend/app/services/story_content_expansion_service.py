from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentExpansionService:
    """Hikaye içerik genişletme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.expansions_file = os.path.join(settings.STORAGE_PATH, "content_expansions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.expansions_file):
            with open(self.expansions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def expand_story(
        self,
        story_id: str,
        story_text: str,
        expansion_type: str = "general",
        target_length: Optional[int] = None
    ) -> Dict:
        """Hikayeyi genişletir."""
        expansion_id = str(uuid.uuid4())
        
        expansion_prompts = {
            "general": "Hikayeyi genişlet, daha fazla detay ekle",
            "beginning": "Başlangıcı genişlet, daha fazla arka plan ekle",
            "middle": "Orta kısmı genişlet, daha fazla olay ekle",
            "ending": "Sonu genişlet, daha detaylı bir kapanış yap",
            "characters": "Karakterleri genişlet, daha fazla karakter gelişimi ekle"
        }
        
        prompt = f"""Aşağıdaki hikayeyi genişlet. 
{expansion_prompts.get(expansion_type, 'Genel olarak genişlet')}:

{story_text}

{f"Hedef uzunluk: {target_length} kelime" if target_length else ""}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye genişletme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )
        
        expanded_text = response.choices[0].message.content
        
        expansion = {
            "expansion_id": expansion_id,
            "story_id": story_id,
            "expansion_type": expansion_type,
            "original_length": len(story_text.split()),
            "expanded_length": len(expanded_text.split()),
            "expanded_text": expanded_text,
            "created_at": datetime.now().isoformat()
        }
        
        expansions = self._load_expansions()
        expansions.append(expansion)
        self._save_expansions(expansions)
        
        return {
            "expansion_id": expansion_id,
            "expanded_text": expanded_text,
            "length_increase": expansion["expanded_length"] - expansion["original_length"],
            "percentage_increase": round(
                ((expansion["expanded_length"] - expansion["original_length"]) / expansion["original_length"]) * 100, 2
            ) if expansion["original_length"] > 0 else 0
        }
    
    async def add_chapter(
        self,
        story_id: str,
        story_text: str,
        chapter_theme: str
    ) -> Dict:
        """Yeni bölüm ekler."""
        prompt = f"""Aşağıdaki hikayeye '{chapter_theme}' temalı yeni bir bölüm ekle:

{story_text}

Yeni bölüm hikayenin devamı olmalı."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        new_chapter = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "new_chapter": new_chapter,
            "chapter_theme": chapter_theme,
            "message": "Yeni bölüm eklendi"
        }
    
    def _load_expansions(self) -> List[Dict]:
        """Genişletmeleri yükler."""
        try:
            with open(self.expansions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_expansions(self, expansions: List[Dict]):
        """Genişletmeleri kaydeder."""
        with open(self.expansions_file, 'w', encoding='utf-8') as f:
            json.dump(expansions, f, ensure_ascii=False, indent=2)

