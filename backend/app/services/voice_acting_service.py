from typing import List, Dict, Optional
from app.services.tts_service import TTSService
from app.services.character_service import CharacterService
from app.services.dialogue_service import DialogueService
import uuid


class VoiceActingService:
    def __init__(self):
        self.tts_service = TTSService()
        self.character_service = CharacterService()
        self.dialogue_service = DialogueService()
    
    async def generate_character_voice(
        self,
        text: str,
        character_id: str,
        language: str = "tr",
        emotion: Optional[str] = None,
        audio_speed: float = 1.0
    ) -> str:
        """
        Belirli bir karakter için ses üretir.
        
        Args:
            text: Seslendirilecek metin
            character_id: Karakter ID'si
            language: Dil
            emotion: Duygu tonu
            audio_speed: Ses hızı
        
        Returns:
            Ses dosyası URL'i
        """
        character = self.character_service.get_character(character_id)
        if not character:
            raise ValueError("Karakter bulunamadı")
        
        # Karakter tipine göre ses seç
        voice = self._select_voice_for_character_type(character.get('character_type', 'neutral'))
        
        # Karakter kişiliğine göre duygu tonu belirle
        if not emotion:
            emotion = self._infer_emotion_from_personality(character.get('personality', ''))
        
        audio_id = f"{character_id}_{uuid.uuid4()}"
        audio_url = await self.tts_service.generate_speech(
            text,
            language,
            audio_id,
            audio_speed=audio_speed,
            audio_slow=False,
            voice=voice,
            emotion=emotion,
            character_id=character_id
        )
        
        return audio_url
    
    async def generate_dialogue_with_voices(
        self,
        dialogues: List[Dict],
        language: str = "tr",
        audio_speed: float = 1.0
    ) -> List[Dict]:
        """
        Diyalogları karakter bazlı seslerle üretir.
        
        Args:
            dialogues: Diyalog listesi [{"character": "İsim", "text": "Metin", "character_id": "id"}]
            language: Dil
            audio_speed: Ses hızı
        
        Returns:
            Ses URL'leri eklenmiş diyalog listesi
        """
        result = []
        
        for dialogue in dialogues:
            character_name = dialogue.get('character')
            text = dialogue.get('text')
            character_id = dialogue.get('character_id')
            
            if not character_id:
                # Karakter ID yoksa isme göre bul
                characters = self.character_service.get_all_characters()
                character = next(
                    (c for c in characters if c.get('name') == character_name),
                    None
                )
                if character:
                    character_id = character.get('character_id')
            
            if character_id:
                # Karakter bazlı ses üret
                audio_url = await self.generate_character_voice(
                    text,
                    character_id,
                    language,
                    None,  # emotion otomatik belirlenecek
                    audio_speed
                )
                dialogue['audio_url'] = audio_url
            
            result.append(dialogue)
        
        return result
    
    def _select_voice_for_character_type(self, character_type: str) -> str:
        """Karakter tipine göre ses seçer."""
        voice_map = {
            "hero": "echo",      # Erkek, sıcak
            "villain": "onyx",   # Erkek, derin
            "sidekick": "nova",  # Kadın, genç
            "mentor": "fable",   # Hikâye anlatıcısı
            "neutral": "alloy"   # Nötr
        }
        return voice_map.get(character_type, "alloy")
    
    def _infer_emotion_from_personality(self, personality: str) -> str:
        """Kişilik özelliklerinden duygu tonu çıkarır."""
        personality_lower = personality.lower()
        
        if any(word in personality_lower for word in ['mutlu', 'neşeli', 'happy', 'cheerful']):
            return "happy"
        elif any(word in personality_lower for word in ['üzgün', 'hüzünlü', 'sad', 'melancholic']):
            return "sad"
        elif any(word in personality_lower for word in ['heyecanlı', 'enerjik', 'excited', 'energetic']):
            return "excited"
        elif any(word in personality_lower for word in ['korkulu', 'endişeli', 'scared', 'anxious']):
            return "scared"
        elif any(word in personality_lower for word in ['gizemli', 'esrarengiz', 'mysterious']):
            return "mysterious"
        elif any(word in personality_lower for word in ['sakin', 'huzurlu', 'calm', 'peaceful']):
            return "calm"
        else:
            return "neutral"
    
    def get_voice_options(self) -> List[Dict]:
        """Kullanılabilir ses seçeneklerini döndürür."""
        return self.tts_service.get_available_voices()
    
    def get_emotion_options(self) -> List[Dict]:
        """Kullanılabilir duygu tonlarını döndürür."""
        return self.tts_service.get_available_emotions()

