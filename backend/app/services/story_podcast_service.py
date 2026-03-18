from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.tts_service import TTSService
import json
import os
import uuid
from datetime import datetime


class StoryPodcastService:
    """Hikaye podcast/radyo formatı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.tts_service = TTSService()
        self.podcasts_file = os.path.join(settings.STORAGE_PATH, "story_podcasts.json")
        self.podcasts_path = os.path.join(settings.STORAGE_PATH, "podcasts")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.podcasts_path, exist_ok=True)
        if not os.path.exists(self.podcasts_file):
            with open(self.podcasts_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_podcast(
        self,
        story_id: str,
        story_text: str,
        title: Optional[str] = None,
        intro_music: bool = True,
        outro_music: bool = True,
        narrator_voice: str = "alloy",
        background_music: bool = True
    ) -> Dict:
        """Hikayeden podcast oluşturur."""
        podcast_id = str(uuid.uuid4())
        
        # Hikayeyi bölümlere ayır
        chapters = self._split_into_chapters(story_text)
        
        # Her bölüm için ses oluştur
        audio_files = []
        for i, chapter in enumerate(chapters):
            audio_url = await self.tts_service.generate_speech(
                text=chapter,
                language="tr",
                story_id=story_id,
                voice=narrator_voice
            )
            audio_files.append({
                "chapter": i + 1,
                "text": chapter,
                "audio_url": audio_url
            })
        
        podcast = {
            "podcast_id": podcast_id,
            "story_id": story_id,
            "title": title or f"Hikaye Podcast - {story_id[:8]}",
            "chapters": audio_files,
            "intro_music": intro_music,
            "outro_music": outro_music,
            "background_music": background_music,
            "duration": sum(len(ch["text"]) * 0.1 for ch in audio_files),  # Tahmini süre
            "created_at": datetime.now().isoformat()
        }
        
        podcasts = self._load_podcasts()
        podcasts.append(podcast)
        self._save_podcasts(podcasts)
        
        return {
            "podcast_id": podcast_id,
            "title": podcast["title"],
            "chapters_count": len(chapters),
            "duration": podcast["duration"]
        }
    
    async def create_radio_show(
        self,
        stories: List[Dict],
        show_title: str,
        host_name: str = "Masal Anlatıcısı"
    ) -> Dict:
        """Radyo programı oluşturur."""
        show_id = str(uuid.uuid4())
        
        # Program açılışı
        intro_text = f"Merhaba, ben {host_name}. Bugün sizlere özel hikayeler anlatacağım."
        intro_audio = await self.tts_service.generate_speech(
            text=intro_text,
            language="tr",
            story_id=show_id,
            voice="alloy"
        )
        
        # Hikayeler
        episodes = []
        for story in stories:
            story_audio = await self.tts_service.generate_speech(
                text=story.get("text", ""),
                language="tr",
                story_id=story.get("story_id", ""),
                voice="alloy"
            )
            episodes.append({
                "story_id": story.get("story_id"),
                "title": story.get("title", ""),
                "audio_url": story_audio
            })
        
        # Program kapanışı
        outro_text = "Bugünkü programımız burada sona eriyor. Bir sonraki programda görüşmek üzere!"
        outro_audio = await self.tts_service.generate_speech(
            text=outro_text,
            language="tr",
            story_id=show_id,
            voice="alloy"
        )
        
        radio_show = {
            "show_id": show_id,
            "title": show_title,
            "host_name": host_name,
            "intro_audio": intro_audio,
            "episodes": episodes,
            "outro_audio": outro_audio,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "show_id": show_id,
            "title": show_title,
            "episodes_count": len(episodes)
        }
    
    def _split_into_chapters(self, text: str, max_length: int = 1000) -> List[str]:
        """Metni bölümlere ayırır."""
        sentences = text.split('.')
        chapters = []
        current_chapter = ""
        
        for sentence in sentences:
            if len(current_chapter) + len(sentence) < max_length:
                current_chapter += sentence + "."
            else:
                if current_chapter:
                    chapters.append(current_chapter.strip())
                current_chapter = sentence + "."
        
        if current_chapter:
            chapters.append(current_chapter.strip())
        
        return chapters
    
    async def get_podcast(self, podcast_id: str) -> Optional[Dict]:
        """Podcast'i getirir."""
        podcasts = self._load_podcasts()
        return next((p for p in podcasts if p["podcast_id"] == podcast_id), None)
    
    def _load_podcasts(self) -> List[Dict]:
        """Podcast'leri yükler."""
        try:
            with open(self.podcasts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_podcasts(self, podcasts: List[Dict]):
        """Podcast'leri kaydeder."""
        with open(self.podcasts_file, 'w', encoding='utf-8') as f:
            json.dump(podcasts, f, ensure_ascii=False, indent=2)

