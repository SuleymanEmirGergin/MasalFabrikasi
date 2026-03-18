from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
from app.services.tts_service import TTSService
import json
import os
import uuid
from datetime import datetime


class StoryInteractiveBookService:
    """Hikaye interaktif kitap formatı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.tts_service = TTSService()
        self.interactive_books_file = os.path.join(settings.STORAGE_PATH, "interactive_books.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.interactive_books_file):
            with open(self.interactive_books_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_interactive_book(
        self,
        story_id: str,
        story_text: str,
        interactive_elements: List[str] = ["click", "sound", "animation"]
    ) -> Dict:
        """İnteraktif kitap oluşturur."""
        book_id = str(uuid.uuid4())
        
        # Hikayeyi sayfalara böl
        pages = self._split_into_pages(story_text)
        
        # Her sayfa için interaktif öğeler ekle
        interactive_pages = []
        for i, page_text in enumerate(pages):
            page_data = {
                "page_number": i + 1,
                "text": page_text,
                "image_url": None,
                "audio_url": None,
                "interactive_elements": []
            }
            
            # Görsel ekle
            if "image" in interactive_elements or "click" in interactive_elements:
                page_data["image_url"] = await self.image_service.generate_image(
                    story_text=page_text[:200],
                    theme="interactive",
                    image_style="illustration"
                )
            
            # Ses ekle
            if "sound" in interactive_elements:
                page_data["audio_url"] = await self.tts_service.generate_speech(
                    text=page_text,
                    language="tr",
                    story_id=story_id,
                    voice="alloy"
                )
            
            # Tıklanabilir öğeler
            if "click" in interactive_elements:
                page_data["interactive_elements"] = self._extract_clickable_elements(page_text)
            
            interactive_pages.append(page_data)
        
        book = {
            "book_id": book_id,
            "story_id": story_id,
            "pages": interactive_pages,
            "interactive_features": interactive_elements,
            "created_at": datetime.now().isoformat()
        }
        
        books = self._load_books()
        books.append(book)
        self._save_books(books)
        
        return {
            "book_id": book_id,
            "pages_count": len(interactive_pages),
            "interactive_features": interactive_elements
        }
    
    async def add_animation_to_page(
        self,
        book_id: str,
        page_number: int,
        animation_type: str = "fade"
    ) -> Dict:
        """Sayfaya animasyon ekler."""
        books = self._load_books()
        book = next((b for b in books if b["book_id"] == book_id), None)
        
        if not book:
            raise ValueError("Kitap bulunamadı")
        
        if page_number > len(book["pages"]):
            raise ValueError("Sayfa bulunamadı")
        
        page = book["pages"][page_number - 1]
        page["animation"] = {
            "type": animation_type,
            "duration": 1.0,
            "enabled": True
        }
        
        self._save_books(books)
        
        return {"message": "Animasyon eklendi"}
    
    def _split_into_pages(self, text: str, max_length: int = 500) -> List[str]:
        """Metni sayfalara böl."""
        sentences = text.split('.')
        pages = []
        current_page = ""
        
        for sentence in sentences:
            if len(current_page) + len(sentence) < max_length:
                current_page += sentence + "."
            else:
                if current_page:
                    pages.append(current_page.strip())
                current_page = sentence + "."
        
        if current_page:
            pages.append(current_page.strip())
        
        return pages if pages else [text]
    
    def _extract_clickable_elements(self, text: str) -> List[Dict]:
        """Tıklanabilir öğeleri çıkarır."""
        elements = []
        words = text.split()
        
        # Büyük harfle başlayan kelimeleri potansiyel tıklanabilir öğe yap
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 3:
                elements.append({
                    "element_id": str(uuid.uuid4()),
                    "text": word.strip('.,!?;:'),
                    "type": "character" if i == 0 or words[i-1][-1] in '.!?' else "object",
                    "position": i
                })
        
        return elements[:5]  # İlk 5 öğe
    
    def _load_books(self) -> List[Dict]:
        """Kitapları yükler."""
        try:
            with open(self.interactive_books_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_books(self, books: List[Dict]):
        """Kitapları kaydeder."""
        with open(self.interactive_books_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)

