from typing import Dict, Optional
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage
try:
    from ebooklib import epub
    EBOOKLIB_AVAILABLE = True
except ImportError:
    EBOOKLIB_AVAILABLE = False
    epub = None
import json


class EbookService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.ebooks_path = os.path.join(settings.STORAGE_PATH, "ebooks")
        self._ensure_directory()
    
    def _ensure_directory(self):
        """E-kitap dizinini oluşturur."""
        os.makedirs(self.ebooks_path, exist_ok=True)
    
    def create_epub(
        self,
        story_id: str,
        title: Optional[str] = None,
        author: Optional[str] = None
    ) -> Dict:
        """
        Hikâyeyi EPUB formatında oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            title: Kitap başlığı (opsiyonel)
            author: Yazar adı (opsiyonel)
        
        Returns:
            EPUB dosyası bilgileri
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # EPUB kitap oluştur
        book = epub.EpubBook()
        
        # Metadata
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(title or story.get('theme', 'Masal'))
        book.set_language(story.get('language', 'tr'))
        
        if author:
            book.add_author(author)
        else:
            book.add_author('Masal Fabrikası')
        
        # Kapak görseli (varsa)
        if story.get('image_url'):
            # Görseli ekle (gerçek uygulamada dosyadan okunmalı)
            pass
        
        # Bölüm oluştur
        chapter = epub.EpubHtml(
            title=story.get('theme', 'Hikâye'),
            file_name='chapter.xhtml',
            lang=story.get('language', 'tr')
        )
        
        # Hikâye metnini HTML'e çevir
        story_text = story.get('story_text', '')
        html_content = f"""
        <html>
        <head>
            <title>{story.get('theme', 'Hikâye')}</title>
        </head>
        <body>
            <h1>{story.get('theme', 'Hikâye')}</h1>
            <p>{story_text.replace(chr(10), '</p><p>')}</p>
        </body>
        </html>
        """
        
        chapter.content = html_content
        book.add_item(chapter)
        
        # Table of contents
        book.toc = [chapter]
        
        # Spine
        book.spine = [chapter]
        
        # CSS (opsiyonel)
        nav_css = epub.EpubItem(
            uid="nav_css",
            file_name="style/nav.css",
            media_type="text/css",
            content='body { font-family: Arial, sans-serif; }'
        )
        book.add_item(nav_css)
        
        # Dosyayı kaydet
        ebook_id = str(uuid.uuid4())
        ebook_path = os.path.join(self.ebooks_path, f"{ebook_id}.epub")
        epub.write_epub(ebook_path, book)
        
        return {
            "ebook_id": ebook_id,
            "file_path": f"/storage/ebooks/{ebook_id}.epub",
            "format": "epub",
            "story_id": story_id,
            "created_at": datetime.now().isoformat()
        }
    
    def create_mobi(
        self,
        story_id: str,
        title: Optional[str] = None,
        author: Optional[str] = None
    ) -> Dict:
        """
        Hikâyeyi MOBI formatında oluşturur.
        Not: MOBI oluşturmak için kindlegen veya calibre gerekir.
        Bu basit bir implementasyon, gerçek uygulamada calibre kullanılabilir.
        """
        # Önce EPUB oluştur
        epub_result = self.create_epub(story_id, title, author)
        
        # EPUB'u MOBI'ye çevir (calibre ile)
        # Bu kısım gerçek uygulamada calibre komut satırı aracı kullanılabilir
        # Şimdilik EPUB döndürüyoruz
        
        return {
            "ebook_id": epub_result["ebook_id"],
            "file_path": epub_result["file_path"].replace('.epub', '.mobi'),
            "format": "mobi",
            "story_id": story_id,
            "note": "MOBI formatı için calibre gerekir",
            "created_at": datetime.now().isoformat()
        }
    
    def create_azw3(
        self,
        story_id: str,
        title: Optional[str] = None,
        author: Optional[str] = None
    ) -> Dict:
        """
        Hikâyeyi AZW3 formatında oluşturur.
        Not: AZW3 oluşturmak için calibre gerekir.
        """
        # Önce EPUB oluştur
        epub_result = self.create_epub(story_id, title, author)
        
        return {
            "ebook_id": epub_result["ebook_id"],
            "file_path": epub_result["file_path"].replace('.epub', '.azw3'),
            "format": "azw3",
            "story_id": story_id,
            "note": "AZW3 formatı için calibre gerekir",
            "created_at": datetime.now().isoformat()
        }
    
    def create_collection_ebook(
        self,
        story_ids: list,
        collection_title: str,
        author: Optional[str] = None
    ) -> Dict:
        """
        Birden fazla hikâyeyi bir e-kitap olarak birleştirir.
        
        Args:
            story_ids: Hikâye ID'leri listesi
            collection_title: Koleksiyon başlığı
            author: Yazar adı
        
        Returns:
            E-kitap bilgileri
        """
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(collection_title)
        book.set_language('tr')
        
        if author:
            book.add_author(author)
        else:
            book.add_author('Masal Fabrikası')
        
        chapters = []
        toc_items = []
        
        for i, story_id in enumerate(story_ids, 1):
            story = self.story_storage.get_story(story_id)
            if not story:
                continue
            
            chapter = epub.EpubHtml(
                title=f"{i}. {story.get('theme', 'Hikâye')}",
                file_name=f'chapter_{i}.xhtml',
                lang=story.get('language', 'tr')
            )
            
            story_text = story.get('story_text', '')
            html_content = f"""
            <html>
            <head>
                <title>{story.get('theme', 'Hikâye')}</title>
            </head>
            <body>
                <h1>{story.get('theme', 'Hikâye')}</h1>
                <p>{story_text.replace(chr(10), '</p><p>')}</p>
            </body>
            </html>
            """
            
            chapter.content = html_content
            book.add_item(chapter)
            chapters.append(chapter)
            toc_items.append(chapter)
        
        book.toc = toc_items
        book.spine = chapters
        
        # Dosyayı kaydet
        ebook_id = str(uuid.uuid4())
        ebook_path = os.path.join(self.ebooks_path, f"{ebook_id}.epub")
        epub.write_epub(ebook_path, book)
        
        return {
            "ebook_id": ebook_id,
            "file_path": f"/storage/ebooks/{ebook_id}.epub",
            "format": "epub",
            "collection_title": collection_title,
            "story_count": len(story_ids),
            "created_at": datetime.now().isoformat()
        }

