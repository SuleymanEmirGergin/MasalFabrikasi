from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryComicService:
    """Hikaye çizgi roman formatı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.comics_file = os.path.join(settings.STORAGE_PATH, "story_comics.json")
        self.comics_path = os.path.join(settings.STORAGE_PATH, "comics")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.comics_path, exist_ok=True)
        if not os.path.exists(self.comics_file):
            with open(self.comics_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_comic(
        self,
        story_id: str,
        story_text: str,
        style: str = "cartoon",
        panels_per_page: int = 4
    ) -> Dict:
        """Hikayeden çizgi roman oluşturur."""
        comic_id = str(uuid.uuid4())
        
        # Hikayeyi panellere ayır
        panels = self._split_into_panels(story_text, panels_per_page)
        
        # Her panel için görsel oluştur
        comic_panels = []
        for i, panel_text in enumerate(panels):
            image_url = await self.image_service.generate_image(
                story_text=panel_text,
                theme="comic",
                image_style=style,
                image_size="1024x1024"
            )
            
            comic_panels.append({
                "panel_number": i + 1,
                "text": panel_text,
                "image_url": image_url,
                "speech_bubbles": self._extract_speech_bubbles(panel_text)
            })
        
        # Sayfalara organize et
        pages = []
        for i in range(0, len(comic_panels), panels_per_page):
            page_panels = comic_panels[i:i + panels_per_page]
            pages.append({
                "page_number": len(pages) + 1,
                "panels": page_panels
            })
        
        comic = {
            "comic_id": comic_id,
            "story_id": story_id,
            "style": style,
            "pages": pages,
            "total_panels": len(comic_panels),
            "created_at": datetime.now().isoformat()
        }
        
        comics = self._load_comics()
        comics.append(comic)
        self._save_comics(comics)
        
        return {
            "comic_id": comic_id,
            "pages_count": len(pages),
            "panels_count": len(comic_panels)
        }
    
    async def create_strip_comic(
        self,
        story_id: str,
        story_text: str,
        num_strips: int = 3
    ) -> Dict:
        """Strip çizgi roman oluşturur."""
        comic_id = str(uuid.uuid4())
        
        # Hikayeyi strip'lere böl
        strips = self._split_into_strips(story_text, num_strips)
        
        comic_strips = []
        for i, strip_text in enumerate(strips):
            image_url = await self.image_service.generate_image(
                story_text=strip_text,
                theme="comic_strip",
                image_style="cartoon",
                image_size="1024x512"
            )
            
            comic_strips.append({
                "strip_number": i + 1,
                "text": strip_text,
                "image_url": image_url
            })
        
        comic = {
            "comic_id": comic_id,
            "story_id": story_id,
            "type": "strip",
            "strips": comic_strips,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "comic_id": comic_id,
            "strips_count": len(comic_strips)
        }
    
    def _split_into_panels(self, text: str, panels_per_page: int = 4) -> List[str]:
        """Metni panellere ayırır."""
        sentences = text.split('.')
        panels = []
        current_panel = ""
        
        sentences_per_panel = max(2, len(sentences) // (panels_per_page * 2))
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                current_panel += sentence.strip() + ". "
                
                if (i + 1) % sentences_per_panel == 0:
                    panels.append(current_panel.strip())
                    current_panel = ""
        
        if current_panel:
            panels.append(current_panel.strip())
        
        return panels if panels else [text]
    
    def _split_into_strips(self, text: str, num_strips: int) -> List[str]:
        """Metni strip'lere böl."""
        sentences = text.split('.')
        strips = []
        sentences_per_strip = len(sentences) // num_strips
        
        for i in range(0, len(sentences), sentences_per_strip):
            strip_text = '. '.join(sentences[i:i + sentences_per_strip])
            if strip_text.strip():
                strips.append(strip_text.strip() + '.')
        
        return strips if strips else [text]
    
    def _extract_speech_bubbles(self, text: str) -> List[str]:
        """Konuşma balonlarını çıkarır."""
        # Tırnak içindeki metinleri bul
        import re
        speech_bubbles = re.findall(r'"([^"]*)"', text)
        return speech_bubbles if speech_bubbles else []
    
    async def get_comic(self, comic_id: str) -> Optional[Dict]:
        """Çizgi romanı getirir."""
        comics = self._load_comics()
        return next((c for c in comics if c["comic_id"] == comic_id), None)
    
    def _load_comics(self) -> List[Dict]:
        """Çizgi romanları yükler."""
        try:
            with open(self.comics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_comics(self, comics: List[Dict]):
        """Çizgi romanları kaydeder."""
        with open(self.comics_file, 'w', encoding='utf-8') as f:
            json.dump(comics, f, ensure_ascii=False, indent=2)

