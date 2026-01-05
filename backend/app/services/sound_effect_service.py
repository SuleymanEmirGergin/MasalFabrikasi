from typing import List, Dict, Optional
try:
    from pydub import AudioSegment
    from pydub.effects import normalize, compress_dynamic_range
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None
    normalize = compress_dynamic_range = None
import os
import uuid
from app.core.config import settings


class SoundEffectService:
    def __init__(self):
        self.sound_effects_path = os.path.join(settings.STORAGE_PATH, "sound_effects")
        self._ensure_sound_effects_directory()
        
        # Ses efektleri kategorileri
        self.effect_categories = {
            "ambient": ["forest", "ocean", "wind", "rain", "thunder"],
            "action": ["sword_clash", "footsteps", "door_creak", "explosion"],
            "emotion": ["sad_music", "happy_music", "suspense", "victory"],
            "character": ["magic_spell", "dragon_roar", "fairy_chime"],
            "transition": ["page_turn", "chapter_start", "scene_change"]
        }
    
    def _ensure_sound_effects_directory(self):
        """Ses efektleri dizinini oluşturur."""
        os.makedirs(self.sound_effects_path, exist_ok=True)
    
    async def add_sound_effect_to_audio(
        self,
        audio_path: str,
        effect_type: str,
        effect_name: str,
        position: float = 0.0,  # Saniye cinsinden pozisyon
        volume: float = 0.5,  # 0.0 - 1.0 arası
        fade_in: float = 0.0,  # Fade in süresi (saniye)
        fade_out: float = 0.0  # Fade out süresi (saniye)
    ) -> str:
        """
        Ses dosyasına ses efekti ekler.
        
        Args:
            audio_path: Ana ses dosyası yolu
            effect_type: Efekt kategorisi (ambient, action, emotion, etc.)
            effect_name: Efekt adı
            position: Efektin ekleneceği pozisyon (saniye)
            volume: Efekt ses seviyesi (0.0 - 1.0)
            fade_in: Fade in süresi
            fade_out: Fade out süresi
        
        Returns:
            Yeni ses dosyası URL'i
        """
        try:
            # Ana ses dosyasını yükle
            main_audio = AudioSegment.from_file(audio_path)
            
            # Ses efektini yükle (eğer dosya varsa)
            effect_path = os.path.join(
                self.sound_effects_path,
                effect_type,
                f"{effect_name}.mp3"
            )
            
            if os.path.exists(effect_path):
                effect_audio = AudioSegment.from_file(effect_path)
                
                # Ses seviyesini ayarla
                effect_audio = effect_audio - (20 * (1 - volume))  # dB cinsinden
                
                # Fade in/out ekle
                if fade_in > 0:
                    effect_audio = effect_audio.fade_in(int(fade_in * 1000))
                if fade_out > 0:
                    effect_audio = effect_audio.fade_out(int(fade_out * 1000))
                
                # Pozisyonu milisaniyeye çevir
                position_ms = int(position * 1000)
                
                # Ana ses dosyasının sonuna kadar uzat (gerekirse)
                if position_ms + len(effect_audio) > len(main_audio):
                    main_audio = main_audio + AudioSegment.silent(
                        duration=(position_ms + len(effect_audio) - len(main_audio))
                    )
                
                # Ses efektini ekle (overlay)
                combined_audio = main_audio.overlay(effect_audio, position=position_ms)
            else:
                # Efekt dosyası yoksa sadece ana sesi döndür
                combined_audio = main_audio
            
            # Yeni dosyayı kaydet
            output_id = str(uuid.uuid4())
            output_path = os.path.join(settings.STORAGE_PATH, "audio", f"{output_id}.mp3")
            combined_audio.export(output_path, format="mp3")
            
            return f"/storage/audio/{output_id}.mp3"
        
        except Exception as e:
            print(f"Ses efekti eklenirken hata: {e}")
            # Hata durumunda orijinal dosyayı döndür
            return audio_path
    
    async def add_multiple_sound_effects(
        self,
        audio_path: str,
        effects: List[Dict]
    ) -> str:
        """
        Birden fazla ses efekti ekler.
        
        Args:
            audio_path: Ana ses dosyası yolu
            effects: Efekt listesi [{"type": "ambient", "name": "forest", "position": 0.0, "volume": 0.5}, ...]
        
        Returns:
            Yeni ses dosyası URL'i
        """
        try:
            current_audio = AudioSegment.from_file(audio_path)
            
            for effect in effects:
                effect_type = effect.get("type", "ambient")
                effect_name = effect.get("name", "")
                position = effect.get("position", 0.0)
                volume = effect.get("volume", 0.5)
                fade_in = effect.get("fade_in", 0.0)
                fade_out = effect.get("fade_out", 0.0)
                
                effect_path = os.path.join(
                    self.sound_effects_path,
                    effect_type,
                    f"{effect_name}.mp3"
                )
                
                if os.path.exists(effect_path):
                    effect_audio = AudioSegment.from_file(effect_path)
                    effect_audio = effect_audio - (20 * (1 - volume))
                    
                    if fade_in > 0:
                        effect_audio = effect_audio.fade_in(int(fade_in * 1000))
                    if fade_out > 0:
                        effect_audio = effect_audio.fade_out(int(fade_out * 1000))
                    
                    position_ms = int(position * 1000)
                    
                    if position_ms + len(effect_audio) > len(current_audio):
                        current_audio = current_audio + AudioSegment.silent(
                            duration=(position_ms + len(effect_audio) - len(current_audio))
                        )
                    
                    current_audio = current_audio.overlay(effect_audio, position=position_ms)
            
            # Yeni dosyayı kaydet
            output_id = str(uuid.uuid4())
            output_path = os.path.join(settings.STORAGE_PATH, "audio", f"{output_id}.mp3")
            current_audio.export(output_path, format="mp3")
            
            return f"/storage/audio/{output_id}.mp3"
        
        except Exception as e:
            print(f"Çoklu ses efekti eklenirken hata: {e}")
            return audio_path
    
    def get_available_effects(self) -> Dict:
        """Kullanılabilir ses efektlerini döndürür."""
        return self.effect_categories
    
    def get_effect_suggestions(self, story_text: str, theme: str) -> List[Dict]:
        """
        Hikâye içeriğine göre ses efekti önerileri yapar.
        
        Args:
            story_text: Hikâye metni
            theme: Hikâye teması
        
        Returns:
            Önerilen efekt listesi
        """
        suggestions = []
        text_lower = story_text.lower()
        theme_lower = theme.lower()
        
        # Temaya göre ambient efektler
        if "orman" in theme_lower or "forest" in theme_lower:
            suggestions.append({
                "type": "ambient",
                "name": "forest",
                "position": 0.0,
                "volume": 0.3,
                "fade_in": 2.0,
                "fade_out": 2.0
            })
        
        if "deniz" in theme_lower or "ocean" in theme_lower:
            suggestions.append({
                "type": "ambient",
                "name": "ocean",
                "position": 0.0,
                "volume": 0.3,
                "fade_in": 2.0,
                "fade_out": 2.0
            })
        
        # Metne göre aksiyon efektleri
        if any(word in text_lower for word in ["kılıç", "sword", "savaş", "battle"]):
            suggestions.append({
                "type": "action",
                "name": "sword_clash",
                "position": 0.0,
                "volume": 0.6
            })
        
        if any(word in text_lower for word in ["yağmur", "rain"]):
            suggestions.append({
                "type": "ambient",
                "name": "rain",
                "position": 0.0,
                "volume": 0.4,
                "fade_in": 1.0,
                "fade_out": 1.0
            })
        
        if any(word in text_lower for word in ["ejderha", "dragon"]):
            suggestions.append({
                "type": "character",
                "name": "dragon_roar",
                "position": 0.0,
                "volume": 0.7
            })
        
        return suggestions

