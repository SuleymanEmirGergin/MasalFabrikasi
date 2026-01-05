from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.sound_effect_service import SoundEffectService
import json
import os
import uuid
from datetime import datetime


class StoryAtmosphereService:
    """Hikaye ses efektleri ve atmosfer servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.sound_effect_service = SoundEffectService()
        self.atmospheres_file = os.path.join(settings.STORAGE_PATH, "story_atmospheres.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.atmospheres_file):
            with open(self.atmospheres_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_atmosphere(
        self,
        story_id: str,
        story_text: str,
        atmosphere_type: str = "ambient"
    ) -> Dict:
        """Hikaye atmosferi oluşturur."""
        atmosphere_id = str(uuid.uuid4())
        
        # Hikayedeki duyguları ve sahneleri analiz et
        emotions = self._extract_emotions(story_text)
        scenes = self._split_into_scenes(story_text)
        
        # Her sahne için uygun ses efektleri seç
        atmosphere_layers = []
        for i, scene in enumerate(scenes):
            scene_emotion = emotions[i] if i < len(emotions) else "neutral"
            sound_effects = self._select_sound_effects(scene_emotion, atmosphere_type)
            
            atmosphere_layers.append({
                "layer_id": str(uuid.uuid4()),
                "scene_number": i + 1,
                "scene_text": scene,
                "emotion": scene_emotion,
                "sound_effects": sound_effects,
                "volume": 0.5
            })
        
        atmosphere = {
            "atmosphere_id": atmosphere_id,
            "story_id": story_id,
            "atmosphere_type": atmosphere_type,
            "layers": atmosphere_layers,
            "created_at": datetime.now().isoformat()
        }
        
        atmospheres = self._load_atmospheres()
        atmospheres.append(atmosphere)
        self._save_atmospheres(atmospheres)
        
        return {
            "atmosphere_id": atmosphere_id,
            "layers_count": len(atmosphere_layers),
            "message": "Atmosfer oluşturuldu"
        }
    
    async def add_background_ambience(
        self,
        atmosphere_id: str,
        ambience_type: str,
        volume: float = 0.3
    ) -> Dict:
        """Arka plan atmosferi ekler."""
        atmospheres = self._load_atmospheres()
        atmosphere = next((a for a in atmospheres if a["atmosphere_id"] == atmosphere_id), None)
        
        if not atmosphere:
            raise ValueError("Atmosfer bulunamadı")
        
        ambience_mapping = {
            "forest": ["wind", "birds", "leaves"],
            "ocean": ["waves", "seagulls", "wind"],
            "city": ["traffic", "people", "horns"],
            "quiet": ["silence", "breathing"],
            "mysterious": ["wind", "creaking", "distant_voices"]
        }
        
        sounds = ambience_mapping.get(ambience_type, ["ambient"])
        
        atmosphere["background_ambience"] = {
            "type": ambience_type,
            "sounds": sounds,
            "volume": volume
        }
        
        self._save_atmospheres(atmospheres)
        
        return {
            "message": "Arka plan atmosferi eklendi",
            "sounds": sounds
        }
    
    def _extract_emotions(self, text: str) -> List[str]:
        """Duyguları çıkarır."""
        emotions = []
        emotion_keywords = {
            "happy": ["mutlu", "neşeli", "sevinç"],
            "sad": ["üzgün", "hüzün", "keder"],
            "scary": ["korku", "korkulu", "ürkütücü"],
            "exciting": ["heyecan", "coşku", "enerji"],
            "calm": ["sakin", "huzur", "rahat"]
        }
        
        sentences = text.split('.')
        for sentence in sentences:
            detected = "neutral"
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in sentence.lower() for keyword in keywords):
                    detected = emotion
                    break
            emotions.append(detected)
        
        return emotions
    
    def _split_into_scenes(self, text: str) -> List[str]:
        """Metni sahnelerine ayırır."""
        paragraphs = text.split('\n\n')
        scenes = [p.strip() for p in paragraphs if p.strip()]
        
        if not scenes:
            sentences = text.split('.')
            scenes = [s.strip() + '.' for s in sentences if s.strip()][:10]
        
        return scenes
    
    def _select_sound_effects(
        self,
        emotion: str,
        atmosphere_type: str
    ) -> List[str]:
        """Ses efektleri seçer."""
        effect_mapping = {
            "happy": ["happy_music", "laughter", "celebration"],
            "sad": ["sad_music", "rain", "wind"],
            "scary": ["thunder", "door_creak", "suspense"],
            "exciting": ["footsteps", "sword_clash", "victory"],
            "calm": ["forest", "ocean", "wind"],
            "neutral": ["ambient", "wind"]
        }
        
        return effect_mapping.get(emotion, ["ambient"])
    
    def _load_atmospheres(self) -> List[Dict]:
        """Atmosferleri yükler."""
        try:
            with open(self.atmospheres_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_atmospheres(self, atmospheres: List[Dict]):
        """Atmosferleri kaydeder."""
        with open(self.atmospheres_file, 'w', encoding='utf-8') as f:
            json.dump(atmospheres, f, ensure_ascii=False, indent=2)

