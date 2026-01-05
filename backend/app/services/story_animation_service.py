from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryAnimationService:
    """Hikaye animasyon ve video oluşturma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.animations_file = os.path.join(settings.STORAGE_PATH, "story_animations.json")
        self.animations_path = os.path.join(settings.STORAGE_PATH, "animations")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.animations_path, exist_ok=True)
        if not os.path.exists(self.animations_file):
            with open(self.animations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_animation_storyboard(
        self,
        story_id: str,
        story_text: str,
        style: str = "cartoon"
    ) -> Dict:
        """Hikaye için storyboard oluşturur."""
        animation_id = str(uuid.uuid4())
        
        # Hikayeyi sahnelerine ayır
        scenes = self._extract_scenes(story_text)
        
        # Her sahne için görsel oluştur
        storyboard = []
        for i, scene in enumerate(scenes):
            image_url = await self.image_service.generate_image(
                story_text=scene,
                theme="animation",
                image_style=style
            )
            storyboard.append({
                "scene_number": i + 1,
                "description": scene,
                "image_url": image_url,
                "duration": 3.0  # Saniye
            })
        
        animation = {
            "animation_id": animation_id,
            "story_id": story_id,
            "style": style,
            "storyboard": storyboard,
            "total_duration": sum(s["duration"] for s in storyboard),
            "created_at": datetime.now().isoformat()
        }
        
        animations = self._load_animations()
        animations.append(animation)
        self._save_animations(animations)
        
        return {
            "animation_id": animation_id,
            "scenes_count": len(storyboard),
            "total_duration": animation["total_duration"]
        }
    
    async def create_slide_show(
        self,
        story_id: str,
        story_text: str,
        transition_effect: str = "fade"
    ) -> Dict:
        """Slideshow video oluşturur."""
        slideshow_id = str(uuid.uuid4())
        
        # Hikayeyi slidelara böl
        slides = self._split_into_slides(story_text)
        
        slide_images = []
        for i, slide_text in enumerate(slides):
            image_url = await self.image_service.generate_image(
                story_text=slide_text,
                theme="story",
                image_style="illustration"
            )
            slide_images.append({
                "slide_number": i + 1,
                "text": slide_text,
                "image_url": image_url,
                "transition": transition_effect
            })
        
        slideshow = {
            "slideshow_id": slideshow_id,
            "story_id": story_id,
            "slides": slide_images,
            "transition_effect": transition_effect,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "slideshow_id": slideshow_id,
            "slides_count": len(slides),
            "message": "Slideshow oluşturuldu"
        }
    
    def _extract_scenes(self, text: str) -> List[str]:
        """Metni sahnelerine ayırır."""
        # Basit bölme - gerçek uygulamada daha gelişmiş olmalı
        paragraphs = text.split('\n\n')
        scenes = [p.strip() for p in paragraphs if p.strip()]
        
        if not scenes:
            # Paragraf yoksa cümlelere böl
            sentences = text.split('.')
            scenes = [s.strip() + '.' for s in sentences if s.strip()][:10]
        
        return scenes
    
    def _split_into_slides(self, text: str, max_slides: int = 10) -> List[str]:
        """Metni slidelara böl."""
        sentences = text.split('.')
        slides = []
        current_slide = ""
        
        for sentence in sentences:
            if len(current_slide) + len(sentence) < 200:
                current_slide += sentence + "."
            else:
                if current_slide:
                    slides.append(current_slide.strip())
                current_slide = sentence + "."
                if len(slides) >= max_slides:
                    break
        
        if current_slide and len(slides) < max_slides:
            slides.append(current_slide.strip())
        
        return slides
    
    async def get_animation(self, animation_id: str) -> Optional[Dict]:
        """Animasyonu getirir."""
        animations = self._load_animations()
        return next((a for a in animations if a["animation_id"] == animation_id), None)
    
    def _load_animations(self) -> List[Dict]:
        """Animasyonları yükler."""
        try:
            with open(self.animations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_animations(self, animations: List[Dict]):
        """Animasyonları kaydeder."""
        with open(self.animations_file, 'w', encoding='utf-8') as f:
            json.dump(animations, f, ensure_ascii=False, indent=2)

