from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class AudioMusicAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.character_voices_dir = os.path.join(settings.STORAGE_PATH, "character_voices")
        self.music_dir = os.path.join(settings.STORAGE_PATH, "music")
        self.sound_effects_dir = os.path.join(settings.STORAGE_PATH, "sound_effects")
        self.voice_library_file = os.path.join(settings.STORAGE_PATH, "voice_library.json")
        self._ensure_directories()
        self._ensure_files()
    
    def _ensure_directories(self):
        for directory in [self.character_voices_dir, self.music_dir, self.sound_effects_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def _ensure_files(self):
        if not os.path.exists(self.voice_library_file):
            with open(self.voice_library_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_character_voice(
        self,
        character_id: str,
        audio_file_path: str,
        voice_name: str,
        description: Optional[str] = None
    ) -> Dict:
        """Karakter sesini kaydeder."""
        voice_id = str(uuid.uuid4())
        voice_entry = {
            "voice_id": voice_id,
            "character_id": character_id,
            "voice_name": voice_name,
            "audio_file_path": audio_file_path,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.voice_library_file, 'r', encoding='utf-8') as f:
            voices = json.load(f)
        voices.append(voice_entry)
        with open(self.voice_library_file, 'w', encoding='utf-8') as f:
            json.dump(voices, f, ensure_ascii=False, indent=2)
        
        return voice_entry
    
    def get_character_voices(self, character_id: str) -> List[Dict]:
        """Karakter seslerini getirir."""
        with open(self.voice_library_file, 'r', encoding='utf-8') as f:
            voices = json.load(f)
        return [v for v in voices if v.get('character_id') == character_id]
    
    async def generate_music(
        self,
        description: str,
        mood: str = "calm",
        duration: int = 30
    ) -> Dict:
        """Müzik oluşturur."""
        # OpenAI Audio API ile müzik oluşturma (örnek)
        prompt = f"""
{description} temalı, {mood} ruh halinde, {duration} saniyelik bir müzik parçası oluştur.
"""
        try:
            # Not: OpenAI'nin gerçek müzik oluşturma API'si yok, bu bir placeholder
            # Gerçek uygulamada başka bir servis kullanılabilir
            music_id = str(uuid.uuid4())
            music_path = os.path.join(self.music_dir, f"{music_id}.mp3")
            
            # Placeholder - gerçek implementasyon için müzik oluşturma servisi gerekli
            return {
                "music_id": music_id,
                "description": description,
                "mood": mood,
                "duration": duration,
                "file_path": music_path,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_sound_effect_suggestions(
        self,
        story_text: str,
        scene_description: Optional[str] = None
    ) -> List[str]:
        """Ses efekti önerileri getirir."""
        # Basit keyword-based öneriler
        suggestions = []
        text_lower = story_text.lower()
        
        if "yağmur" in text_lower or "rain" in text_lower:
            suggestions.append("rain_ambience")
        if "rüzgar" in text_lower or "wind" in text_lower:
            suggestions.append("wind_sound")
        if "ateş" in text_lower or "fire" in text_lower:
            suggestions.append("fire_crackling")
        if "deniz" in text_lower or "ocean" in text_lower:
            suggestions.append("ocean_waves")
        if "orman" in text_lower or "forest" in text_lower:
            suggestions.append("forest_ambience")
        if "şehir" in text_lower or "city" in text_lower:
            suggestions.append("city_ambience")
        if "kapı" in text_lower or "door" in text_lower:
            suggestions.append("door_creak")
        if "adım" in text_lower or "footstep" in text_lower:
            suggestions.append("footsteps")
        
        return suggestions[:5]  # En fazla 5 öneri
    
    async def add_background_music(
        self,
        story_id: str,
        music_description: str,
        volume: float = 0.5
    ) -> Dict:
        """Hikâyeye arka plan müziği ekler."""
        music = await self.generate_music(music_description)
        
        return {
            "story_id": story_id,
            "music_id": music.get("music_id"),
            "music_path": music.get("file_path"),
            "volume": volume,
            "added_at": datetime.now().isoformat()
        }
    
    def create_sound_effect_library(self) -> Dict:
        """Ses efekti kütüphanesi oluşturur."""
        library = {
            "categories": {
                "nature": ["rain", "wind", "thunder", "ocean", "forest", "birds"],
                "urban": ["city", "traffic", "door", "footsteps", "bell"],
                "fantasy": ["magic", "spell", "dragon", "castle", "sword"],
                "emotions": ["happy", "sad", "excited", "calm", "mysterious"]
            },
            "total_effects": 0
        }
        
        for category, effects in library["categories"].items():
            library["total_effects"] += len(effects)
        
        return library

