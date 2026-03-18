from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryTranslationAdvancedService:
    """Hikaye içerik çevirisi geliştirmeleri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.translations_file = os.path.join(settings.STORAGE_PATH, "advanced_translations.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.translations_file):
            with open(self.translations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def translate_with_context(
        self,
        story_id: str,
        story_text: str,
        target_language: str,
        cultural_adaptation: bool = True,
        preserve_style: bool = True
    ) -> Dict:
        """Bağlam koruyarak çeviri yapar."""
        translation_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi {target_language} diline çevir.
{f"Kültürel bağlamı uyarla ve yerel ifadeler kullan." if cultural_adaptation else "Kelime kelime çevir."}
{f"Yazım stilini koru." if preserve_style else ""}

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Sen bir {target_language} çevirmenisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=2000
        )
        
        translated_text = response.choices[0].message.content
        
        translation = {
            "translation_id": translation_id,
            "story_id": story_id,
            "source_language": "tr",
            "target_language": target_language,
            "original_text": story_text,
            "translated_text": translated_text,
            "cultural_adaptation": cultural_adaptation,
            "preserve_style": preserve_style,
            "created_at": datetime.now().isoformat()
        }
        
        translations = self._load_translations()
        translations.append(translation)
        self._save_translations(translations)
        
        return {
            "translation_id": translation_id,
            "translated_text": translated_text,
            "target_language": target_language
        }
    
    async def back_translate(
        self,
        story_id: str,
        translated_text: str,
        original_language: str = "tr"
    ) -> Dict:
        """Geri çeviri yapar (kalite kontrolü için)."""
        prompt = f"""Aşağıdaki metni {original_language} diline geri çevir:

{translated_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Sen bir {original_language} çevirmenisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        back_translated = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "back_translated_text": back_translated,
            "message": "Geri çeviri tamamlandı"
        }
    
    def _load_translations(self) -> List[Dict]:
        """Çevirileri yükler."""
        try:
            with open(self.translations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_translations(self, translations: List[Dict]):
        """Çevirileri kaydeder."""
        with open(self.translations_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)

