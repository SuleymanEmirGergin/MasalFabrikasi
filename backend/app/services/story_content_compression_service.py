from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentCompressionService:
    """Hikaye içerik sıkıştırma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.compressions_file = os.path.join(settings.STORAGE_PATH, "content_compressions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.compressions_file):
            with open(self.compressions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def compress_story(
        self,
        story_id: str,
        story_text: str,
        compression_ratio: float = 0.5  # 0.5 = %50'ye indir
    ) -> Dict:
        """Hikayeyi sıkıştırır."""
        compression_id = str(uuid.uuid4())
        
        target_length = int(len(story_text.split()) * compression_ratio)
        
        prompt = f"""Aşağıdaki hikayeyi yaklaşık {target_length} kelimeye sıkıştır.
Önemli olayları ve karakterleri koru, gereksiz detayları çıkar:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik sıkıştırma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        compressed_text = response.choices[0].message.content
        
        compression = {
            "compression_id": compression_id,
            "story_id": story_id,
            "original_length": len(story_text.split()),
            "compressed_length": len(compressed_text.split()),
            "compression_ratio": compression_ratio,
            "compressed_text": compressed_text,
            "created_at": datetime.now().isoformat()
        }
        
        compressions = self._load_compressions()
        compressions.append(compression)
        self._save_compressions(compressions)
        
        return {
            "compression_id": compression_id,
            "compressed_text": compressed_text,
            "length_reduction": compression["original_length"] - compression["compressed_length"],
            "compression_percentage": round(
                ((compression["original_length"] - compression["compressed_length"]) / compression["original_length"]) * 100, 2
            ) if compression["original_length"] > 0 else 0
        }
    
    async def create_short_version(
        self,
        story_id: str,
        story_text: str,
        max_words: int = 100
    ) -> Dict:
        """Kısa versiyon oluşturur."""
        prompt = f"""Aşağıdaki hikayenin {max_words} kelimelik çok kısa bir versiyonunu oluştur:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir özet uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=200
        )
        
        short_version = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "short_version": short_version,
            "word_count": len(short_version.split()),
            "max_words": max_words
        }
    
    def _load_compressions(self) -> List[Dict]:
        """Sıkıştırmaları yükler."""
        try:
            with open(self.compressions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_compressions(self, compressions: List[Dict]):
        """Sıkıştırmaları kaydeder."""
        with open(self.compressions_file, 'w', encoding='utf-8') as f:
            json.dump(compressions, f, ensure_ascii=False, indent=2)

