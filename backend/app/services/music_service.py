from typing import List, Dict, Optional
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None
import os
import uuid
from app.core.config import settings


class MusicService:
    def __init__(self):
        self.music_path = os.path.join(settings.STORAGE_PATH, "music")
        
        # Müzik kategorileri
        self.music_categories = {
            "ambient": ["peaceful", "calm", "meditation"],
            "adventure": ["epic", "journey", "quest"],
            "emotional": ["sad", "happy", "romantic", "dramatic"],
            "fantasy": ["magical", "mystical", "enchanted"],
            "action": ["intense", "battle", "chase"]
        }
        
        self._ensure_music_directory()
    
    def _ensure_music_directory(self):
        """Müzik dizinini oluşturur."""
        os.makedirs(self.music_path, exist_ok=True)
        for category in self.music_categories.keys():
            os.makedirs(os.path.join(self.music_path, category), exist_ok=True)
    
    async def add_background_music(
        self,
        audio_path: str,
        music_type: str,
        music_name: str,
        volume: float = 0.3,  # Arka plan müziği için düşük ses
        fade_in: float = 2.0,
        fade_out: float = 2.0,
        loop: bool = True
    ) -> str:
        """
        Ses dosyasına arka plan müziği ekler.
        
        Args:
            audio_path: Ana ses dosyası yolu
            music_type: Müzik kategorisi
            music_name: Müzik adı
            volume: Müzik ses seviyesi (0.0 - 1.0)
            fade_in: Fade in süresi
            fade_out: Fade out süresi
            loop: Müziği döngüye al
        
        Returns:
            Yeni ses dosyası URL'i
        """
        try:
            # Ana ses dosyasını yükle
            main_audio = AudioSegment.from_file(audio_path)
            main_duration = len(main_audio)
            
            # Müzik dosyasını yükle
            music_path = os.path.join(
                self.music_path,
                music_type,
                f"{music_name}.mp3"
            )
            
            if os.path.exists(music_path):
                music_audio = AudioSegment.from_file(music_path)
                
                # Müzik ses seviyesini ayarla
                music_audio = music_audio - (20 * (1 - volume))
                
                # Fade in/out ekle
                if fade_in > 0:
                    music_audio = music_audio.fade_in(int(fade_in * 1000))
                if fade_out > 0:
                    music_audio = music_audio.fade_out(int(fade_out * 1000))
                
                # Müziği döngüye al (gerekirse)
                if loop and len(music_audio) < main_duration:
                    loops_needed = (main_duration // len(music_audio)) + 1
                    music_audio = music_audio * loops_needed
                
                # Müziği ana ses uzunluğuna kısalt
                music_audio = music_audio[:main_duration]
                
                # Müziği arka plana ekle (overlay)
                combined_audio = main_audio.overlay(music_audio)
            else:
                # Müzik dosyası yoksa sadece ana sesi döndür
                combined_audio = main_audio
            
            # Yeni dosyayı kaydet
            output_id = str(uuid.uuid4())
            output_path = os.path.join(settings.STORAGE_PATH, "audio", f"{output_id}.mp3")
            combined_audio.export(output_path, format="mp3")
            
            return f"/storage/audio/{output_id}.mp3"
        
        except Exception as e:
            print(f"Arka plan müziği eklenirken hata: {e}")
            return audio_path
    
    def get_music_suggestions(self, story_text: str, theme: str, emotion: str) -> List[Dict]:
        """
        Hikâye için müzik önerileri yapar.
        
        Args:
            story_text: Hikâye metni
            theme: Hikâye teması
            emotion: Ana duygu
        
        Returns:
            Önerilen müzikler listesi
        """
        suggestions = []
        text_lower = story_text.lower()
        theme_lower = theme.lower()
        emotion_lower = emotion.lower()
        
        # Duyguya göre müzik
        if "mutlu" in emotion_lower or "happy" in emotion_lower:
            suggestions.append({
                "type": "emotional",
                "name": "happy",
                "volume": 0.25,
                "description": "Neşeli arka plan müziği"
            })
        
        if "üzgün" in emotion_lower or "sad" in emotion_lower:
            suggestions.append({
                "type": "emotional",
                "name": "sad",
                "volume": 0.2,
                "description": "Hüzünlü arka plan müziği"
            })
        
        # Temaya göre müzik
        if "macera" in theme_lower or "adventure" in theme_lower:
            suggestions.append({
                "type": "adventure",
                "name": "journey",
                "volume": 0.3,
                "description": "Macera müziği"
            })
        
        if "fantastik" in theme_lower or "fantasy" in theme_lower or "büyü" in text_lower:
            suggestions.append({
                "type": "fantasy",
                "name": "magical",
                "volume": 0.25,
                "description": "Büyülü müzik"
            })
        
        # Varsayılan
        if not suggestions:
            suggestions.append({
                "type": "ambient",
                "name": "peaceful",
                "volume": 0.2,
                "description": "Sakin arka plan müziği"
            })
        
        return suggestions
    
    def get_available_music(self) -> Dict:
        """Kullanılabilir müzikleri döndürür."""
        return self.music_categories

