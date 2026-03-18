from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.translation_service import TranslationService
import json


class AdvancedTranslationService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.translation_service = TranslationService()
    
    async def translate_story_realtime(
        self,
        story_text: str,
        target_language: str,
        source_language: str = "tr",
        preserve_tone: bool = True
    ) -> Dict:
        """
        Hikâyeyi gerçek zamanlı çevirir (daha kaliteli çeviri).
        
        Args:
            story_text: Çevrilecek metin
            target_language: Hedef dil
            source_language: Kaynak dil
            preserve_tone: Tonu koru (hikâye tonunu korur)
        
        Returns:
            Çevrilmiş metin ve çeviri bilgileri
        """
        prompt = f"""
Aşağıdaki hikâyeyi {target_language} diline çevir. Hikâye tonunu, stilini ve anlamını koru.

Kaynak Dil: {source_language}
Hedef Dil: {target_language}

Hikâye:
{story_text}

Çeviriyi döndür. Sadece çevrilmiş metni döndür, ek açıklama yapma.
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir çevirmensin. Hikâyeleri doğal ve akıcı bir şekilde çeviriyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                "original_text": story_text,
                "translated_text": translated_text,
                "source_language": source_language,
                "target_language": target_language,
                "word_count_original": len(story_text.split()),
                "word_count_translated": len(translated_text.split()),
                "preserve_tone": preserve_tone
            }
        
        except Exception as e:
            print(f"Gelişmiş çeviri hatası: {e}")
            # Fallback: Basit çeviri servisi
            return await self.translation_service.translate_text(
                story_text,
                target_language,
                source_language
            )
    
    async def translate_multiple_languages(
        self,
        story_text: str,
        target_languages: List[str],
        source_language: str = "tr"
    ) -> Dict:
        """
        Hikâyeyi birden fazla dile çevirir.
        
        Args:
            story_text: Çevrilecek metin
            target_languages: Hedef diller listesi
            source_language: Kaynak dil
        
        Returns:
            Tüm dillerde çeviriler
        """
        translations = {}
        
        for target_lang in target_languages:
            try:
                translation = await self.translate_story_realtime(
                    story_text,
                    target_lang,
                    source_language
                )
                translations[target_lang] = translation.get('translated_text', '')
            except Exception as e:
                print(f"{target_lang} çevirisi hatası: {e}")
                translations[target_lang] = None
        
        return {
            "source_language": source_language,
            "translations": translations,
            "total_languages": len(target_languages),
            "successful_translations": len([t for t in translations.values() if t])
        }
    
    async def translate_audio_transcript(
        self,
        audio_text: str,
        target_language: str,
        source_language: str = "tr"
    ) -> Dict:
        """
        Ses transkriptini çevirir (sesli çeviri için).
        """
        # Önce metni çevir
        translation = await self.translate_story_realtime(
            audio_text,
            target_language,
            source_language
        )
        
        return {
            "original_transcript": audio_text,
            "translated_transcript": translation.get('translated_text', ''),
            "source_language": source_language,
            "target_language": target_language,
            "note": "Ses dosyası için TTS servisi kullanılabilir"
        }
    
    def get_supported_languages(self) -> List[Dict]:
        """Desteklenen dilleri getirir."""
        return [
            {"code": "tr", "name": "Türkçe", "native_name": "Türkçe"},
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "fr", "name": "French", "native_name": "Français"},
            {"code": "de", "name": "German", "native_name": "Deutsch"},
            {"code": "it", "name": "Italian", "native_name": "Italiano"},
            {"code": "pt", "name": "Portuguese", "native_name": "Português"},
            {"code": "ru", "name": "Russian", "native_name": "Русский"},
            {"code": "ar", "name": "Arabic", "native_name": "العربية"},
            {"code": "zh", "name": "Chinese", "native_name": "中文"},
            {"code": "ja", "name": "Japanese", "native_name": "日本語"},
            {"code": "ko", "name": "Korean", "native_name": "한국어"}
        ]
    
    async def detect_language(self, text: str) -> Dict:
        """Metnin dilini tespit eder."""
        prompt = f"""
Aşağıdaki metnin dilini tespit et. Sadece dil kodunu döndür (örn: tr, en, es).

Metin:
{text}

Dil kodu:
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir dil tespit uzmanısın. Metinlerin dilini tespit ediyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            detected_language = response.choices[0].message.content.strip().lower()
            
            # Dil kodunu doğrula
            supported = self.get_supported_languages()
            language_codes = [lang['code'] for lang in supported]
            
            if detected_language not in language_codes:
                detected_language = "tr"  # Varsayılan
            
            return {
                "detected_language": detected_language,
                "confidence": "high",
                "text_sample": text[:100]
            }
        
        except Exception as e:
            print(f"Dil tespiti hatası: {e}")
            return {
                "detected_language": "tr",
                "confidence": "low",
                "text_sample": text[:100]
            }

