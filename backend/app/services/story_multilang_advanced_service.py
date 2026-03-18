from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryMultilangAdvancedService:
    """Hikaye çeviri ve çoklu dil geliştirmeleri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.translations_file = os.path.join(settings.STORAGE_PATH, "story_translations.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.translations_file):
            with open(self.translations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def translate_story(
        self,
        story_id: str,
        story_text: str,
        target_language: str,
        preserve_cultural_context: bool = True
    ) -> Dict:
        """Hikayeyi çevirir."""
        translation_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi {target_language} diline çevir.
{f"Kültürel bağlamı koru ve yerel ifadeleri uyarla." if preserve_cultural_context else "Kelime kelime çevir."}

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Sen bir {target_language} çevirmenisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        translated_text = response.choices[0].message.content
        
        translation = {
            "translation_id": translation_id,
            "story_id": story_id,
            "original_language": "tr",
            "target_language": target_language,
            "original_text": story_text,
            "translated_text": translated_text,
            "preserve_cultural_context": preserve_cultural_context,
            "created_at": datetime.now().isoformat()
        }
        
        translations = self._load_translations()
        translations.append(translation)
        self._save_translations(translations)
        
        return {
            "translation_id": translation_id,
            "target_language": target_language,
            "translated_text": translated_text
        }
    
    async def create_multilingual_story(
        self,
        story_id: str,
        story_text: str,
        languages: List[str]
    ) -> Dict:
        """Çoklu dil versiyonu oluşturur."""
        multilingual_id = str(uuid.uuid4())
        
        translations = {}
        for language in languages:
            translation = await self.translate_story(
                story_id, story_text, language, preserve_cultural_context=True
            )
            translations[language] = translation["translated_text"]
        
        multilingual = {
            "multilingual_id": multilingual_id,
            "story_id": story_id,
            "original_text": story_text,
            "translations": translations,
            "languages": languages,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "multilingual_id": multilingual_id,
            "languages": languages,
            "translations_count": len(translations)
        }
    
    async def compare_translations(
        self,
        story_id: str,
        language1: str,
        language2: str
    ) -> Dict:
        """Çevirileri karşılaştırır."""
        translations = self._load_translations()
        story_translations = [
            t for t in translations
            if t["story_id"] == story_id and t["target_language"] in [language1, language2]
        ]
        
        trans1 = next((t for t in story_translations if t["target_language"] == language1), None)
        trans2 = next((t for t in story_translations if t["target_language"] == language2), None)
        
        if not trans1 or not trans2:
            raise ValueError("Çeviriler bulunamadı")
        
        return {
            "language1": {
                "language": language1,
                "text": trans1["translated_text"][:200]
            },
            "language2": {
                "language": language2,
                "text": trans2["translated_text"][:200]
            },
            "similarity": self._calculate_similarity(
                trans1["translated_text"],
                trans2["translated_text"]
            )
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Metin benzerliğini hesaplar."""
        # Basit benzerlik hesaplama
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
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

