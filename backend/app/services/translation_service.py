from typing import Dict, Optional
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    Translator = None
from app.services.story_service import StoryService


class TranslationService:
    def __init__(self):
        if GOOGLETRANS_AVAILABLE and Translator:
            self.translator = Translator()
        else:
            self.translator = None
        self.supported_languages = {
            "tr": "Türkçe",
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "ru": "Русский",
            "ar": "العربية",
            "ja": "日本語",
            "ko": "한국어",
            "zh": "中文",
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Desteklenen dilleri getirir."""
        return self.supported_languages
    
    async def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> str:
        """
        Metni çevirir.
        
        Args:
            text: Çevrilecek metin
            target_language: Hedef dil kodu
            source_language: Kaynak dil kodu (auto = otomatik tespit)
        """
        try:
            if source_language == "auto":
                result = self.translator.translate(text, dest=target_language)
            else:
                result = self.translator.translate(text, src=source_language, dest=target_language)
            return result.text
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            # Fallback: Orijinal metni döndür
            return text
    
    async def translate_story(self, story: Dict, target_language: str) -> Dict:
        """
        Hikâyeyi çevirir (metin, tema).
        """
        try:
            translated_story = story.copy()
            
            # Tema çevirisi
            if story.get('theme'):
                translated_story['theme'] = await self.translate_text(
                    story['theme'],
                    target_language
                )
            
            # Hikâye metni çevirisi
            if story.get('story_text'):
                translated_story['story_text'] = await self.translate_text(
                    story['story_text'],
                    target_language
                )
            
            translated_story['language'] = target_language
            
            return translated_story
        except Exception as e:
            print(f"Hikâye çeviri hatası: {e}")
            return story

