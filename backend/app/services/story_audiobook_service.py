from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.tts_service import TTSService
import json
import os
import uuid
from datetime import datetime


class StoryAudiobookService:
    """Hikaye sesli kitap formatı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.tts_service = TTSService()
        self.audiobooks_file = os.path.join(settings.STORAGE_PATH, "story_audiobooks.json")
        self.audiobooks_path = os.path.join(settings.STORAGE_PATH, "audiobooks")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.audiobooks_path, exist_ok=True)
        if not os.path.exists(self.audiobooks_file):
            with open(self.audiobooks_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_audiobook(
        self,
        story_id: str,
        story_text: str,
        title: Optional[str] = None,
        narrator_voice: str = "alloy",
        chapter_breaks: bool = True,
        background_music: bool = False
    ) -> Dict:
        """Hikayeden sesli kitap oluşturur."""
        audiobook_id = str(uuid.uuid4())
        
        # Hikayeyi bölümlere ayır
        if chapter_breaks:
            chapters = self._split_into_chapters(story_text)
        else:
            chapters = [story_text]
        
        # Her bölüm için ses oluştur
        audio_chapters = []
        for i, chapter in enumerate(chapters):
            audio_url = await self.tts_service.generate_speech(
                text=chapter,
                language="tr",
                story_id=story_id,
                voice=narrator_voice,
                emotion="neutral"
            )
            audio_chapters.append({
                "chapter_number": i + 1,
                "title": f"Bölüm {i + 1}",
                "text": chapter,
                "audio_url": audio_url,
                "duration": len(chapter) * 0.1  # Tahmini süre
            })
        
        audiobook = {
            "audiobook_id": audiobook_id,
            "story_id": story_id,
            "title": title or f"Sesli Kitap - {story_id[:8]}",
            "chapters": audio_chapters,
            "narrator_voice": narrator_voice,
            "background_music": background_music,
            "total_duration": sum(ch["duration"] for ch in audio_chapters),
            "created_at": datetime.now().isoformat()
        }
        
        audiobooks = self._load_audiobooks()
        audiobooks.append(audiobook)
        self._save_audiobooks(audiobooks)
        
        return {
            "audiobook_id": audiobook_id,
            "title": audiobook["title"],
            "chapters_count": len(chapters),
            "total_duration": audiobook["total_duration"]
        }
    
    async def create_character_audiobook(
        self,
        story_id: str,
        story_text: str,
        character_voices: Dict[str, str]
    ) -> Dict:
        """Karakter sesleriyle sesli kitap oluşturur."""
        audiobook_id = str(uuid.uuid4())
        
        # Hikayeyi diyaloglara ayır
        dialogues = self._extract_dialogues(story_text)
        
        audio_segments = []
        for dialogue in dialogues:
            character = dialogue.get("character", "narrator")
            voice = character_voices.get(character, "alloy")
            
            audio_url = await self.tts_service.generate_speech(
                text=dialogue["text"],
                language="tr",
                story_id=story_id,
                voice=voice,
                character_id=character
            )
            
            audio_segments.append({
                "character": character,
                "text": dialogue["text"],
                "audio_url": audio_url
            })
        
        audiobook = {
            "audiobook_id": audiobook_id,
            "story_id": story_id,
            "type": "character_voices",
            "segments": audio_segments,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "audiobook_id": audiobook_id,
            "segments_count": len(audio_segments),
            "message": "Karakter sesli kitap oluşturuldu"
        }
    
    def _split_into_chapters(self, text: str, max_length: int = 2000) -> List[str]:
        """Metni bölümlere ayırır."""
        paragraphs = text.split('\n\n')
        chapters = []
        current_chapter = ""
        
        for paragraph in paragraphs:
            if len(current_chapter) + len(paragraph) < max_length:
                current_chapter += "\n\n" + paragraph
            else:
                if current_chapter:
                    chapters.append(current_chapter.strip())
                current_chapter = paragraph
        
        if current_chapter:
            chapters.append(current_chapter.strip())
        
        return chapters if chapters else [text]
    
    def _extract_dialogues(self, text: str) -> List[Dict]:
        """Diyalogları çıkarır."""
        # Basit yaklaşım - gerçek uygulamada daha gelişmiş olmalı
        dialogues = []
        lines = text.split('\n')
        
        for line in lines:
            if ':' in line and len(line) < 200:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    character = parts[0].strip()
                    dialogue_text = parts[1].strip()
                    dialogues.append({
                        "character": character,
                        "text": dialogue_text
                    })
        
        return dialogues if dialogues else [{"character": "narrator", "text": text}]
    
    async def get_audiobook(self, audiobook_id: str) -> Optional[Dict]:
        """Sesli kitabı getirir."""
        audiobooks = self._load_audiobooks()
        return next((a for a in audiobooks if a["audiobook_id"] == audiobook_id), None)
    
    def _load_audiobooks(self) -> List[Dict]:
        """Sesli kitapları yükler."""
        try:
            with open(self.audiobooks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_audiobooks(self, audiobooks: List[Dict]):
        """Sesli kitapları kaydeder."""
        with open(self.audiobooks_file, 'w', encoding='utf-8') as f:
            json.dump(audiobooks, f, ensure_ascii=False, indent=2)

