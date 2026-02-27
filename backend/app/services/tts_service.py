import os
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None
import uuid
from pathlib import Path
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None
from typing import Optional, Dict, List
from app.core.config import settings
from openai import OpenAI
from app.services.cloud_storage_service import cloud_storage_service


class TTSService:
    def __init__(self):
        self.supported_languages = {
            "tr": "tr",
            "en": "en",
            "es": "es",
            "fr": "fr",
            "de": "de"
        }
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        
        # Ses seçenekleri
        self.voice_options = {
            "alloy": "Nötr, çok amaçlı",
            "echo": "Erkek, sıcak",
            "fable": "İngiliz aksanı, hikâye anlatıcısı",
            "onyx": "Erkek, derin",
            "nova": "Kadın, genç",
            "shimmer": "Kadın, yumuşak"
        }
        
        # Duygu tonları için prompt eklemeleri
        self.emotion_prompts = {
            "happy": "mutlu ve neşeli bir tonla",
            "sad": "üzgün ve hüzünlü bir tonla",
            "excited": "heyecanlı ve enerjik bir tonla",
            "scared": "korkulu ve endişeli bir tonla",
            "calm": "sakin ve huzurlu bir tonla",
            "mysterious": "gizemli ve esrarengiz bir tonla",
            "neutral": "nötr bir tonla"
        }
    
    async def generate_speech(
        self, 
        text: str, 
        language: str, 
        story_id: str,
        audio_speed: float = 1.0,
        audio_slow: bool = False,
        voice: Optional[str] = None,
        emotion: Optional[str] = None,
        character_id: Optional[str] = None
    ) -> str:
        """
        Metni sese dönüştürür.
        
        Args:
            text: Seslendirilecek metin
            language: Dil kodu
            story_id: Hikâye ID'si
            audio_speed: Ses hızı (0.5 - 2.0)
            audio_slow: Yavaş konuşma modu (gTTS için)
            voice: Ses seçeneği (alloy, echo, fable, onyx, nova, shimmer)
            emotion: Duygu tonu (happy, sad, excited, scared, calm, mysterious, neutral)
            character_id: Karakter ID'si (karakter özelliklerine göre ses seçimi için)
        """
        try:
            # OpenAI TTS kullanılabilirse ve ses OpenAI sesi ise onu kullan
            is_openai_voice = voice in self.voice_options
            
            if self.openai_client and is_openai_voice:
                return await self._generate_with_openai_tts(
                    text, language, story_id, voice, emotion, audio_speed
                )
            
            # ElevenLabs entegrasyonu (Wiro veya Direct)
            is_wiro_tts = "elevenlabs" in settings.TTS_MODEL.lower() and "wiro" in settings.GPT_BASE_URL
            
            if (is_wiro_tts or settings.ELEVENLABS_API_KEY) and voice and not is_openai_voice:
                 return await self._generate_with_elevenlabs(
                    text, voice, story_id
                 )
            
            # Karakter bazlı ses seçimi (eğer voice None ise)
            selected_voice = voice or self._select_voice_for_character(character_id)
            
            # Eğer seçilen ses OpenAI sesi ise tekrar dene
            if self.openai_client and selected_voice in self.voice_options:
                 return await self._generate_with_openai_tts(
                    text, language, story_id, selected_voice, emotion, audio_speed
                )

            # Duygu tonunu metne ekle (eğer belirtilmişse)
            processed_text = self._add_emotion_to_text(text, emotion)
            
            # Dil kodunu kontrol et
            lang_code = self.supported_languages.get(language, "tr")
            
            # Hızı sınırla
            audio_speed = max(0.5, min(2.0, audio_speed))
            
            # gTTS ile ses üret
            tts = gTTS(text=processed_text, lang=lang_code, slow=audio_slow)
            
            # Geçici dosya
            temp_audio_id = str(uuid.uuid4())
            temp_audio_path = f"{settings.STORAGE_PATH}/audio/{temp_audio_id}.mp3"
            
            tts.save(temp_audio_path)
            
            # Ses hızını ayarla (eğer 1.0 değilse)
            if audio_speed != 1.0:
                audio = AudioSegment.from_mp3(temp_audio_path)
                # Hızı değiştir (frame_rate değiştirerek)
                new_frame_rate = int(audio.frame_rate * audio_speed)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
                audio = audio.set_frame_rate(audio.frame_rate)
                
                # Final dosya
                audio_id = story_id or str(uuid.uuid4())
                audio_path = f"{settings.STORAGE_PATH}/audio/{audio_id}.mp3"
                audio.export(audio_path, format="mp3")
                
                # Geçici dosyayı sil
                try:
                    os.remove(temp_audio_path)
                except:
                    pass
            else:
                # Hız değişikliği yoksa sadece ismi değiştir
                audio_id = story_id or str(uuid.uuid4())
                audio_path = f"{settings.STORAGE_PATH}/audio/{audio_id}.mp3"
                os.rename(temp_audio_path, audio_path)
            
            # URL döndür
            # Cloudinary upload (Supabase Storage)
            cloudinary_url = await cloud_storage_service.upload_audio(
                audio_path,
                folder="audio",
                public_id=f"story_audio_{audio_id}"
            )
            return cloudinary_url
        
        except Exception as e:
            print(f"TTS hatası: {e}")
            # Hata durumunda boş bir ses dosyası oluştur
            return self._create_empty_audio(story_id)
    
    async def _generate_with_elevenlabs(self, text: str, voice_id: str, story_id: str) -> str:
        """ElevenLabs ile ses üretir."""
        from app.services.voice_cloning_service import voice_cloning_service
        try:
            audio_bytes = await voice_cloning_service.generate_speech(text, voice_id)
            
            # Ses dosyasını kaydet
            audio_id = story_id or str(uuid.uuid4())
            audio_path = f"{settings.STORAGE_PATH}/audio/{audio_id}.mp3"
            
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            
            # Upload to Cloudinary (will delete local file if successful)
            cloudinary_url = await cloud_storage_service.upload_audio(
                audio_path,
                folder="audio",
                public_id=f"story_audio_{audio_id}"
            )
            
            return cloudinary_url
        except Exception as e:
            print(f"ElevenLabs TTS hatası: {e}")
            raise

    async def _generate_with_openai_tts(
        self,
        text: str,
        language: str,
        story_id: str,
        voice: str,
        emotion: Optional[str],
        audio_speed: float
    ) -> str:
        """OpenAI TTS API ile ses üretir."""
        try:
            # Duygu tonunu metne ekle
            processed_text = self._add_emotion_to_text(text, emotion)
            
            # OpenAI TTS API
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice if voice in self.voice_options else "alloy",
                input=processed_text,
                speed=audio_speed
            )
            
            # Ses dosyasını kaydet
            audio_id = story_id or str(uuid.uuid4())
            audio_path = f"{settings.STORAGE_PATH}/audio/{audio_id}.mp3"
            
            with open(audio_path, "wb") as f:
                f.write(response.content)
            
            # Upload to Cloudinary (will delete local file if successful)
            cloudinary_url = await cloud_storage_service.upload_audio(
                audio_path,
                folder="audio",
                public_id=f"story_audio_{audio_id}"
            )
            
            return cloudinary_url
        except Exception as e:
            print(f"OpenAI TTS hatası: {e}")
            raise
    
    def _select_voice_for_character(self, character_id: Optional[str]) -> str:
        """Karakter özelliklerine göre ses seçer."""
        if not character_id:
            return "alloy"  # Varsayılan
        
        # Karakter bilgilerini yükle (basit bir eşleme)
        # Gerçek uygulamada character_service'ten alınabilir
        character_type_voice_map = {
            "hero": "echo",
            "villain": "onyx",
            "sidekick": "nova",
            "mentor": "fable",
            "neutral": "alloy"
        }
        
        # Şimdilik basit bir eşleme, gerçek uygulamada character_service kullanılabilir
        return "alloy"
    
    def _add_emotion_to_text(self, text: str, emotion: Optional[str]) -> str:
        """Metne duygu tonu ekler (TTS için ipucu)."""
        if not emotion or emotion == "neutral":
            return text
        
        # Duygu prompt'unu ekle (bazı TTS sistemleri için)
        emotion_hint = self.emotion_prompts.get(emotion, "")
        if emotion_hint:
            # Metnin başına veya sonuna duygu ipucu eklenebilir
            # gTTS bunu desteklemez ama OpenAI TTS için hazırlık
            return text
    
    def get_available_voices(self) -> List[Dict]:
        """Kullanılabilir ses seçeneklerini döndürür."""
        return [
            {"id": voice_id, "name": voice_id.capitalize(), "description": desc}
            for voice_id, desc in self.voice_options.items()
        ]
    
    def get_available_emotions(self) -> List[Dict]:
        """Kullanılabilir duygu tonlarını döndürür."""
        emotion_names = {
            "happy": "Mutlu",
            "sad": "Üzgün",
            "excited": "Heyecanlı",
            "scared": "Korkulu",
            "calm": "Sakin",
            "mysterious": "Gizemli",
            "neutral": "Nötr"
        }
        return [
            {"id": emotion_id, "name": emotion_names.get(emotion_id, emotion_id)}
            for emotion_id in self.emotion_prompts.keys()
        ]
    
    def _create_empty_audio(self, story_id: str) -> str:
        """Boş bir ses dosyası oluşturur (fallback)."""
        audio_id = story_id or str(uuid.uuid4())
        audio_path = f"{settings.STORAGE_PATH}/audio/{audio_id}.mp3"
        
        # Basit bir placeholder ses dosyası oluştur
        Path(audio_path).touch()
        
        return f"/storage/audio/{audio_id}.mp3"

