from typing import Dict, List, Optional
from app.services.advanced_translation_service import AdvancedTranslationService
from app.services.story_storage import StoryStorage
import json
import os
from datetime import datetime
from app.core.config import settings


class MultilangService:
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
    
    async def create_multilang_story(self, story_id: str, target_languages: List[str]) -> Dict:
        """Çoklu dilde hikâye oluşturur."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        original_text = story.get('story_text', '')
        source_language = story.get('language', 'tr')
        
        translations = {}
        for lang in target_languages:
            translation = await self.translation_service.translate_story_realtime(
                original_text,
                lang,
                source_language
            )
            translations[lang] = translation.get('translated_text', '')
        
        multilang_story = {
            "story_id": story_id,
            "languages": {source_language: original_text, **translations},
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.multilang_file, 'r', encoding='utf-8') as f:
            multilang_stories = json.load(f)
        multilang_stories[story_id] = multilang_story
        with open(self.multilang_file, 'w', encoding='utf-8') as f:
            json.dump(multilang_stories, f, ensure_ascii=False, indent=2)
        
        return multilang_story
    
    def get_multilang_story(self, story_id: str) -> Optional[Dict]:
        """Çoklu dil hikâyesini getirir."""
        with open(self.multilang_file, 'r', encoding='utf-8') as f:
            multilang_stories = json.load(f)
        return multilang_stories.get(story_id)
    
    async def compare_translations(self, story_id: str, language1: str, language2: str) -> Dict:
        """İki dildeki çevirileri karşılaştırır."""
        multilang = self.get_multilang_story(story_id)
        if not multilang:
            raise ValueError("Çoklu dil hikâyesi bulunamadı")
        
        text1 = multilang.get('languages', {}).get(language1, '')
        text2 = multilang.get('languages', {}).get(language2, '')
        
        return {
            "language1": language1,
            "language2": language2,
            "text1": text1,
            "text2": text2,
            "similarity": self._calculate_similarity(text1, text2)
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

