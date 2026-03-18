from typing import List
import re
from app.services.image_service import ImageService
from app.core.config import settings


class MultiImageService:
    def __init__(self):
        self.image_service = ImageService()
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Metni paragraflara böler."""
        # Paragrafları boş satırlara göre ayır
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Metni cümlelere böler."""
        # Basit cümle ayırma (nokta, soru işareti, ünlem)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    async def generate_images_for_story(
        self,
        story_text: str,
        theme: str,
        mode: str = "paragraph",  # "paragraph", "sentence", "scene"
        image_style: str = "fantasy",
        image_size: str = "1024x1024",
        max_images: int = 5
    ) -> List[str]:
        """
        Hikâye için birden fazla görsel üretir.
        
        Args:
            story_text: Hikâye metni
            theme: Hikâye teması
            mode: Görsel üretim modu (paragraph, sentence, scene)
            image_style: Görsel stili
            image_size: Görsel boyutu
            max_images: Maksimum görsel sayısı
        
        Returns:
            Görsel URL'leri listesi
        """
        image_urls = []
        
        if mode == "paragraph":
            # Her paragraf için bir görsel
            paragraphs = self._split_into_paragraphs(story_text)
            paragraphs = paragraphs[:max_images]
            
            for i, paragraph in enumerate(paragraphs):
                # Paragraftan görsel prompt oluştur
                prompt = self._create_scene_prompt(paragraph, theme, i + 1, len(paragraphs))
                image_url = await self.image_service.generate_image(
                    paragraph,
                    theme,
                    image_style=image_style,
                    image_size=image_size
                )
                image_urls.append(image_url)
        
        elif mode == "sentence":
            # Her cümle için bir görsel (ilk birkaç cümle)
            sentences = self._split_into_sentences(story_text)
            sentences = sentences[:max_images]
            
            for i, sentence in enumerate(sentences):
                prompt = self._create_scene_prompt(sentence, theme, i + 1, len(sentences))
                image_url = await self.image_service.generate_image(
                    sentence,
                    theme,
                    image_style=image_style,
                    image_size=image_size
                )
                image_urls.append(image_url)
        
        elif mode == "scene":
            # Hikâyeyi sahneler halinde böl (paragraflar)
            paragraphs = self._split_into_paragraphs(story_text)
            paragraphs = paragraphs[:max_images]
            
            for i, paragraph in enumerate(paragraphs):
                # Sahne açıklaması oluştur
                scene_description = f"Scene {i + 1}: {paragraph[:100]}"
                image_url = await self.image_service.generate_image(
                    scene_description,
                    theme,
                    image_style=image_style,
                    image_size=image_size
                )
                image_urls.append(image_url)
        
        return image_urls
    
    def _create_scene_prompt(self, text: str, theme: str, scene_num: int, total_scenes: int) -> str:
        """Sahne için görsel prompt oluşturur."""
        # Metnin ilk 100 karakterini al
        text_preview = text[:100] + "..." if len(text) > 100 else text
        return f"{text_preview}, scene {scene_num} of {total_scenes}, {theme}"

