from typing import Dict, List, Optional
from app.services.advanced_translation_service import AdvancedTranslationService
from app.services.story_storage import StoryStorage
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class MultilangEnhancedService:
    def __init__(self):
        self.translation_service = AdvancedTranslationService()
        self.story_storage = StoryStorage()
        self.multilang_file = os.path.join(settings.STORAGE_PATH, "multilang_stories.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.multilang_file):
            with open(self.multilang_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_multilingual_story(
        self,
        story_id: str,
        target_languages: List[str]
    ) -> Dict:
        """Çoklu dilde hikâye oluşturur."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        original_text = story.get('story_text', '')
        translations = {}
        
        for lang in target_languages:
            try:
                translation = self.translation_service.translate_text(original_text, lang, story.get('language', 'tr'))
                translations[lang] = translation.get('translated_text', '')
            except:
                translations[lang] = original_text
        
        multilang_entry = {
            "multilang_id": str(uuid.uuid4()),
            "original_story_id": story_id,
            "original_language": story.get('language', 'tr'),
            "translations": translations,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.multilang_file, 'r', encoding='utf-8') as f:
            multilang_stories = json.load(f)
        multilang_stories[story_id] = multilang_entry
        with open(self.multilang_file, 'w', encoding='utf-8') as f:
            json.dump(multilang_stories, f, ensure_ascii=False, indent=2)
        
        return multilang_entry
    
    def get_comparison_mode(
        self,
        story_id: str,
        languages: List[str]
    ) -> Dict:
        """Dil karşılaştırma modu getirir."""
        with open(self.multilang_file, 'r', encoding='utf-8') as f:
            multilang_stories = json.load(f)
        
        multilang_entry = multilang_stories.get(story_id)
        if not multilang_entry:
            raise ValueError("Çoklu dil hikâyesi bulunamadı")
        
        comparison = {}
        for lang in languages:
            if lang in multilang_entry.get('translations', {}):
                comparison[lang] = multilang_entry['translations'][lang]
        
        return {
            "story_id": story_id,
            "languages": languages,
            "comparison": comparison
        }
    
    async def assess_translation_quality(
        self,
        story_id: str,
        target_language: str
    ) -> Dict:
        """Çeviri kalitesi değerlendirir."""
        with open(self.multilang_file, 'r', encoding='utf-8') as f:
            multilang_stories = json.load(f)
        
        multilang_entry = multilang_stories.get(story_id)
        if not multilang_entry:
            raise ValueError("Çoklu dil hikâyesi bulunamadı")
        
        original = multilang_entry.get('original_language', 'tr')
        translation = multilang_entry.get('translations', {}).get(target_language, '')
        
        if not translation:
            return {"error": "Çeviri bulunamadı"}
        
        # Basit kalite değerlendirmesi
        original_words = len(original.split())
        translation_words = len(translation.split())
        
        word_ratio = translation_words / max(original_words, 1)
        
        quality_score = 100
        if word_ratio < 0.5 or word_ratio > 2.0:
            quality_score -= 20
        if word_ratio < 0.3 or word_ratio > 3.0:
            quality_score -= 30
        
        return {
            "story_id": story_id,
            "target_language": target_language,
            "quality_score": max(0, min(100, quality_score)),
            "word_ratio": round(word_ratio, 2),
            "assessment": "İyi" if quality_score >= 70 else "Orta" if quality_score >= 50 else "Düşük"
        }
    
    def auto_detect_language(self, text: str) -> str:
        """Otomatik dil algılama."""
        # Basit dil algılama (gerçek uygulamada daha gelişmiş olabilir)
        turkish_chars = ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü', 'Ç', 'Ğ', 'İ', 'Ö', 'Ş', 'Ü']
        has_turkish = any(char in text for char in turkish_chars)
        
        if has_turkish:
            return "tr"
        else:
            return "en"  # Varsayılan

