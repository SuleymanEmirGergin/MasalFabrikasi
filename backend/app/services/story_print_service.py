from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryPrintService:
    """Hikaye yazdırma ve fiziksel kitap oluşturma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.print_orders_file = os.path.join(settings.STORAGE_PATH, "print_orders.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.print_orders_file):
            with open(self.print_orders_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_printable_book(
        self,
        story_id: str,
        story_text: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        include_images: bool = True,
        page_size: str = "A4",
        font_size: int = 14
    ) -> Dict:
        """Yazdırılabilir kitap oluşturur."""
        book_id = str(uuid.uuid4())
        
        # Hikayeyi sayfalara böl
        pages = self._split_into_pages(story_text, page_size, font_size)
        
        # Her sayfa için görsel oluştur (isteğe bağlı)
        formatted_pages = []
        for i, page_text in enumerate(pages):
            page_data = {
                "page_number": i + 1,
                "text": page_text,
                "image_url": None
            }
            
            if include_images and i % 2 == 0:  # Her 2 sayfada bir görsel
                image_url = await self.image_service.generate_image(
                    story_text=page_text[:200],  # İlk 200 karakter
                    theme="book",
                    image_style="illustration"
                )
                page_data["image_url"] = image_url
            
            formatted_pages.append(page_data)
        
        book = {
            "book_id": book_id,
            "story_id": story_id,
            "title": title or "Hikaye Kitabı",
            "author": author or "Masal Fabrikası",
            "pages": formatted_pages,
            "page_size": page_size,
            "font_size": font_size,
            "total_pages": len(formatted_pages),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "book_id": book_id,
            "title": book["title"],
            "total_pages": len(formatted_pages),
            "printable_format": "PDF",
            "message": "Yazdırılabilir kitap oluşturuldu"
        }
    
    async def create_coloring_book(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Boyama kitabı oluşturur."""
        coloring_book_id = str(uuid.uuid4())
        
        # Hikayeyi sahnelerine ayır
        scenes = self._extract_scenes(story_text)
        
        # Her sahne için çizim oluştur
        coloring_pages = []
        for i, scene in enumerate(scenes):
            image_url = await self.image_service.generate_image(
                story_text=scene,
                theme="coloring",
                image_style="line_art"
            )
            
            coloring_pages.append({
                "page_number": i + 1,
                "scene_description": scene,
                "coloring_image_url": image_url
            })
        
        coloring_book = {
            "coloring_book_id": coloring_book_id,
            "story_id": story_id,
            "pages": coloring_pages,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "coloring_book_id": coloring_book_id,
            "pages_count": len(coloring_pages),
            "message": "Boyama kitabı oluşturuldu"
        }
    
    async def create_print_order(
        self,
        book_id: str,
        user_id: str,
        shipping_address: Dict,
        quantity: int = 1
    ) -> Dict:
        """Yazdırma siparişi oluşturur."""
        order_id = str(uuid.uuid4())
        
        order = {
            "order_id": order_id,
            "book_id": book_id,
            "user_id": user_id,
            "quantity": quantity,
            "shipping_address": shipping_address,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        orders = self._load_orders()
        orders.append(order)
        self._save_orders(orders)
        
        return {
            "order_id": order_id,
            "status": "pending",
            "message": "Sipariş oluşturuldu"
        }
    
    def _split_into_pages(
        self,
        text: str,
        page_size: str,
        font_size: int
    ) -> List[str]:
        """Metni sayfalara böl."""
        # Sayfa başına karakter sayısı (yaklaşık)
        chars_per_page = {
            "A4": 2000 if font_size == 14 else 1500,
            "A5": 1000 if font_size == 14 else 750,
            "Letter": 1800 if font_size == 14 else 1350
        }
        
        max_chars = chars_per_page.get(page_size, 2000)
        
        words = text.split()
        pages = []
        current_page = ""
        
        for word in words:
            if len(current_page) + len(word) + 1 < max_chars:
                current_page += word + " "
            else:
                if current_page:
                    pages.append(current_page.strip())
                current_page = word + " "
        
        if current_page:
            pages.append(current_page.strip())
        
        return pages if pages else [text]
    
    def _extract_scenes(self, text: str) -> List[str]:
        """Sahneleri çıkarır."""
        paragraphs = text.split('\n\n')
        scenes = [p.strip() for p in paragraphs if p.strip()]
        
        if not scenes:
            sentences = text.split('.')
            scenes = [s.strip() + '.' for s in sentences if s.strip()][:10]
        
        return scenes
    
    def _load_orders(self) -> List[Dict]:
        """Siparişleri yükler."""
        try:
            with open(self.print_orders_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_orders(self, orders: List[Dict]):
        """Siparişleri kaydeder."""
        with open(self.print_orders_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

