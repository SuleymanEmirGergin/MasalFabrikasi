from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryAutoSummaryService:
    """Hikaye otomatik özetleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.summaries_file = os.path.join(settings.STORAGE_PATH, "story_summaries.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.summaries_file):
            with open(self.summaries_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_summary(
        self,
        story_id: str,
        story_text: str,
        summary_length: str = "medium"  # "short", "medium", "long"
    ) -> Dict:
        """Hikaye özeti oluşturur."""
        summary_id = str(uuid.uuid4())
        
        length_instructions = {
            "short": "1-2 cümlelik çok kısa bir özet",
            "medium": "3-5 cümlelik orta uzunlukta bir özet",
            "long": "6-10 cümlelik detaylı bir özet"
        }
        
        prompt = f"""Aşağıdaki hikayenin {length_instructions.get(summary_length, 'orta uzunlukta')} özetini oluştur:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir özet uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        summary_text = response.choices[0].message.content
        
        summary = {
            "summary_id": summary_id,
            "story_id": story_id,
            "summary_text": summary_text,
            "summary_length": summary_length,
            "word_count": len(summary_text.split()),
            "created_at": datetime.now().isoformat()
        }
        
        summaries = self._load_summaries()
        summaries.append(summary)
        self._save_summaries(summaries)
        
        return {
            "summary_id": summary_id,
            "summary_text": summary_text,
            "word_count": summary["word_count"]
        }
    
    async def create_key_points(
        self,
        story_id: str,
        story_text: str,
        num_points: int = 5
    ) -> Dict:
        """Anahtar noktaları çıkarır."""
        prompt = f"""Aşağıdaki hikayenin {num_points} anahtar noktasını liste halinde çıkar:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        key_points_text = response.choices[0].message.content
        
        # Noktaları parse et
        points = [p.strip() for p in key_points_text.split('\n') if p.strip() and (p.strip()[0].isdigit() or p.strip().startswith('-'))]
        
        return {
            "story_id": story_id,
            "key_points": points[:num_points],
            "points_count": len(points)
        }
    
    async def create_tldr(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """TL;DR (Too Long; Didn't Read) özeti oluşturur."""
        prompt = f"""Aşağıdaki hikayenin çok kısa bir TL;DR özetini yap (1-2 cümle):

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir özet uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        tldr_text = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "tldr": tldr_text,
            "message": "TL;DR oluşturuldu"
        }
    
    def _load_summaries(self) -> List[Dict]:
        """Özetleri yükler."""
        try:
            with open(self.summaries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_summaries(self, summaries: List[Dict]):
        """Özetleri kaydeder."""
        with open(self.summaries_file, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)

