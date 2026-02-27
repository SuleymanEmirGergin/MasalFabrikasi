from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.music_service import MusicService
import json
import os
import uuid
from datetime import datetime


class StoryMusicIntegrationService:
    """Hikaye müzik ve şarkı entegrasyonu servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.music_service = MusicService()
        self.music_integrations_file = os.path.join(settings.STORAGE_PATH, "music_integrations.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.music_integrations_file):
            with open(self.music_integrations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_story_song(
        self,
        story_id: str,
        story_text: str,
        melody_style: str = "children"
    ) -> Dict:
        """Hikayeden şarkı oluşturur."""
        song_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeden çocuklar için bir şarkı sözü oluştur. 
Melodik, eğlenceli ve akılda kalıcı olsun:

{story_text}

Şarkı sözlerini verse-chorus formatında ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir şarkı sözü yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        lyrics = response.choices[0].message.content
        
        song = {
            "song_id": song_id,
            "story_id": story_id,
            "lyrics": lyrics,
            "melody_style": melody_style,
            "created_at": datetime.now().isoformat()
        }
        
        integrations = self._load_integrations()
        integrations.append(song)
        self._save_integrations(integrations)
        
        return {
            "song_id": song_id,
            "lyrics": lyrics,
            "message": "Şarkı oluşturuldu"
        }
    
    async def add_music_to_story(
        self,
        story_id: str,
        music_type: str,
        emotion: str = "neutral",
        volume: float = 0.3
    ) -> Dict:
        """Hikayeye müzik ekler."""
        integration_id = str(uuid.uuid4())
        
        # Duyguya göre müzik seç
        music_mapping = {
            "happy": "happy",
            "sad": "emotional",
            "exciting": "adventure",
            "calm": "ambient",
            "mysterious": "fantasy"
        }
        
        music_category = music_mapping.get(emotion, "ambient")
        
        integration = {
            "integration_id": integration_id,
            "story_id": story_id,
            "music_type": music_type,
            "music_category": music_category,
            "emotion": emotion,
            "volume": volume,
            "created_at": datetime.now().isoformat()
        }
        
        integrations = self._load_integrations()
        integrations.append(integration)
        self._save_integrations(integrations)
        
        return {
            "integration_id": integration_id,
            "message": "Müzik eklendi"
        }
    
    async def create_rhythm_story(
        self,
        story_id: str,
        story_text: str,
        tempo: str = "moderate"
    ) -> Dict:
        """Ritmik hikaye oluşturur."""
        rhythm_id = str(uuid.uuid4())
        
        # Metni ritmik parçalara ayır
        sentences = story_text.split('.')
        rhythm_segments = []
        
        for sentence in sentences:
            if sentence.strip():
                words = sentence.strip().split()
                rhythm_segments.append({
                    "text": sentence.strip(),
                    "word_count": len(words),
                    "rhythm_pattern": self._generate_rhythm_pattern(len(words), tempo)
                })
        
        rhythm_story = {
            "rhythm_id": rhythm_id,
            "story_id": story_id,
            "tempo": tempo,
            "segments": rhythm_segments,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "rhythm_id": rhythm_id,
            "segments_count": len(rhythm_segments),
            "message": "Ritmik hikaye oluşturuldu"
        }
    
    def _generate_rhythm_pattern(self, word_count: int, tempo: str) -> str:
        """Ritim deseni oluşturur."""
        if tempo == "fast":
            beats = word_count // 2
        elif tempo == "slow":
            beats = word_count * 2
        else:
            beats = word_count
        
        pattern = "|".join(["X" for _ in range(beats)])
        return pattern
    
    def _load_integrations(self) -> List[Dict]:
        """Entegrasyonları yükler."""
        try:
            with open(self.music_integrations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_integrations(self, integrations: List[Dict]):
        """Entegrasyonları kaydeder."""
        with open(self.music_integrations_file, 'w', encoding='utf-8') as f:
            json.dump(integrations, f, ensure_ascii=False, indent=2)

