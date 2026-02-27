import os
import uuid
from pathlib import Path
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    letter = A4 = getSampleStyleSheet = ParagraphStyle = inch = None
    SimpleDocTemplate = Paragraph = Spacer = RLImage = PageBreak = None
    TA_CENTER = TA_JUSTIFY = pdfmetrics = TTFont = None
import httpx
try:
    from ebooklib import epub
    EBOOKLIB_AVAILABLE = True
except ImportError:
    EBOOKLIB_AVAILABLE = False
    epub = None
from app.core.config import settings


class ExportService:
    def __init__(self):
        self.storage_path = settings.STORAGE_PATH
        os.makedirs(f"{self.storage_path}/exports", exist_ok=True)
    
    async def export_to_pdf(self, story: dict) -> str:
        """
        Hikâyeyi PDF formatında dışa aktarır.
        """
        try:
            pdf_id = str(uuid.uuid4())
            pdf_path = f"{self.storage_path}/exports/{pdf_id}.pdf"
            
            # PDF oluştur
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story_content = []
            
            # Stil tanımlamaları
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#6200ee',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            theme_style = ParagraphStyle(
                'CustomTheme',
                parent=styles['Heading2'],
                fontSize=18,
                textColor='#333',
                spaceAfter=20,
                alignment=TA_CENTER
            )
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=12,
                textColor='#000',
                spaceAfter=12,
                alignment=TA_JUSTIFY,
                leading=18
            )
            
            # Başlık
            story_content.append(Paragraph("Masal Fabrikası AI", title_style))
            story_content.append(Spacer(1, 0.5*inch))
            
            # Tema
            if story.get('theme'):
                story_content.append(Paragraph(f"Tema: {story.get('theme')}", theme_style))
                story_content.append(Spacer(1, 0.3*inch))
            
            # Görsel (varsa)
            if story.get('image_url'):
                try:
                    image_url = story.get('image_url')
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_url)
                        if response.status_code == 200:
                            temp_image_path = f"{self.storage_path}/exports/temp_{pdf_id}.png"
                            with open(temp_image_path, 'wb') as f:
                                f.write(response.content)
                            
                            img = RLImage(temp_image_path, width=5*inch, height=3.75*inch)
                            story_content.append(img)
                            story_content.append(Spacer(1, 0.3*inch))
                            
                            # Geçici dosyayı sil
                            try:
                                os.remove(temp_image_path)
                            except:
                                pass
                except:
                    pass  # Görsel yüklenemezse devam et
            
            # Hikâye metni
            story_text = story.get('story_text', '')
            paragraphs = story_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story_content.append(Paragraph(para.strip().replace('\n', '<br/>'), body_style))
                    story_content.append(Spacer(1, 0.2*inch))
            
            # PDF'i oluştur
            doc.build(story_content)
            
            return f"/storage/exports/{pdf_id}.pdf"
        except Exception as e:
            print(f"PDF export hatası: {e}")
            raise
    
    async def export_to_epub(self, story: dict) -> str:
        """
        Hikâyeyi EPUB formatında dışa aktarır.
        """
        try:
            epub_id = str(uuid.uuid4())
            epub_path = f"{self.storage_path}/exports/{epub_id}.epub"
            
            # EPUB kitap oluştur
            book = epub.EpubBook()
            
            # Kitap metadata
            book.set_identifier(epub_id)
            book.set_title(story.get('theme', 'Hikâye'))
            book.set_language('tr')
            book.add_author('Masal Fabrikası AI')
            
            # Bölüm oluştur
            chapter = epub.EpubHtml(
                title=story.get('theme', 'Hikâye'),
                file_name='chapter.xhtml',
                lang='tr'
            )
            
            # HTML içerik
            html_content = f"""
            <html>
            <head>
                <title>{story.get('theme', 'Hikâye')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    h1 {{ color: #6200ee; }}
                    p {{ text-align: justify; line-height: 1.6; }}
                </style>
            </head>
            <body>
                <h1>{story.get('theme', 'Hikâye')}</h1>
                <p>{story.get('story_text', '').replace(chr(10), '<br/>')}</p>
            </body>
            </html>
            """
            
            chapter.content = html_content
            book.add_item(chapter)
            
            # TOC ve spine
            book.toc = (chapter,)
            book.spine = ['nav', chapter]
            
            # Nav dosyası
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # EPUB'ı kaydet
            epub.write_epub(epub_path, book)
            
            return f"/storage/exports/{epub_id}.epub"
        except Exception as e:
            print(f"EPUB export hatası: {e}")
            raise

