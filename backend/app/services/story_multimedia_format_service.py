from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
from app.services.tts_service import TTSService
import json
import os
import uuid
from datetime import datetime


class StoryMultimediaFormatService:
    """Hikaye çoklu medya formatları servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.tts_service = TTSService()
        self.multimedia_file = os.path.join(settings.STORAGE_PATH, "multimedia_stories.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.multimedia_file):
            with open(self.multimedia_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_multimedia_story(
        self,
        story_id: str,
        story_text: str,
        media_types: List[str] = ["text", "image", "audio"]
    ) -> Dict:
        """Çoklu medya hikayesi oluşturur."""
        multimedia_id = str(uuid.uuid4())
        
        # Hikayeyi bölümlere ayır
        sections = self._split_into_sections(story_text)
        
        multimedia_sections = []
        for i, section_text in enumerate(sections):
            section_data = {
                "section_number": i + 1,
                "text": section_text,
                "media": {}
            }
            
            # Görsel ekle
            if "image" in media_types:
                section_data["media"]["image_url"] = await self.image_service.generate_image(
                    story_text=section_text,
                    theme="multimedia",
                    image_style="illustration"
                )
            
            # Ses ekle
            if "audio" in media_types:
                section_data["media"]["audio_url"] = await self.tts_service.generate_speech(
                    text=section_text,
                    language="tr",
                    story_id=story_id,
                    voice="alloy"
                )
            
            # Video metadata (gelecekte video eklenebilir)
            if "video" in media_types:
                section_data["media"]["video_metadata"] = {
                    "duration": len(section_text.split()) * 0.5,
                    "format": "mp4"
                }
            
            multimedia_sections.append(section_data)
        
        multimedia_story = {
            "multimedia_id": multimedia_id,
            "story_id": story_id,
            "media_types": media_types,
            "sections": multimedia_sections,
            "created_at": datetime.now().isoformat()
        }
        
        stories = self._load_stories()
        stories.append(multimedia_story)
        self._save_stories(stories)
        
        return {
            "multimedia_id": multimedia_id,
            "sections_count": len(multimedia_sections),
            "media_types": media_types
        }
    
    async def create_rich_media_presentation(
        self,
        story_id: str,
        story_text: str,
        presentation_style: str = "modern"
    ) -> Dict:
        """Zengin medya sunumu oluşturur."""
        presentation_id = str(uuid.uuid4())
        
        # Sunum slideları oluştur
        slides = self._create_presentation_slides(story_text)
        
        presentation_slides = []
        for i, slide_content in enumerate(slides):
            slide = {
                "slide_number": i + 1,
                "title": slide_content.get("title", f"Slide {i+1}"),
                "content": slide_content.get("content", ""),
                "image_url": None,
                "audio_url": None
            }
            
            # Her slide için görsel
            slide["image_url"] = await self.image_service.generate_image(
                story_text=slide["content"],
                theme="presentation",
                image_style=presentation_style
            )
            
            # Ses ekle
            slide["audio_url"] = await self.tts_service.generate_speech(
                text=slide["content"],
                language="tr",
                story_id=story_id,
                voice="alloy"
            )
            
            presentation_slides.append(slide)
        
        presentation = {
            "presentation_id": presentation_id,
            "story_id": story_id,
            "style": presentation_style,
            "slides": presentation_slides,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "presentation_id": presentation_id,
            "slides_count": len(presentation_slides),
            "style": presentation_style
        }
    
    def _split_into_sections(self, text: str, max_length: int = 300) -> List[str]:
        """Metni bölümlere ayırır."""
        sentences = text.split('.')
        sections = []
        current_section = ""
        
        for sentence in sentences:
            if len(current_section) + len(sentence) < max_length:
                current_section += sentence + "."
            else:
                if current_section:
                    sections.append(current_section.strip())
                current_section = sentence + "."
        
        if current_section:
            sections.append(current_section.strip())
        
        return sections if sections else [text]
    
    def _create_presentation_slides(self, text: str) -> List[Dict]:
        """Sunum slideları oluşturur."""
        sections = self._split_into_sections(text, max_length=200)
        slides = []
        
        for section in sections:
            # İlk cümleyi başlık olarak kullan
            sentences = section.split('.')
            title = sentences[0].strip() if sentences else "Slide"
            content = '. '.join(sentences[1:]) if len(sentences) > 1 else section
            
            slides.append({
                "title": title[:50],  # Maksimum 50 karakter
                "content": content
            })
        
        return slides
    
    def _load_stories(self) -> List[Dict]:
        """Hikayeleri yükler."""
        try:
            with open(self.multimedia_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_stories(self, stories: List[Dict]):
        """Hikayeleri kaydeder."""
        with open(self.multimedia_file, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)

