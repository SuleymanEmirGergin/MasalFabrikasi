from typing import Dict, List, Optional
from app.services.story_service import StoryService
from app.services.character_service import CharacterService
import json


class StoryOutlineService:
    def __init__(self):
        self.story_service = StoryService()
        self.character_service = CharacterService()
    
    async def generate_outline(
        self,
        theme: str,
        language: str = "tr",
        story_type: str = "masal",
        include_characters: bool = True
    ) -> Dict:
        """
        Hikâye özeti/planı oluşturur.
        
        Args:
            theme: Hikâye teması
            language: Dil
            story_type: Hikâye türü
            include_characters: Karakter listesi dahil edilsin mi
        
        Returns:
            Hikâye planı (özet, bölümler, karakterler)
        """
        # Özet üret
        summary = await self._generate_summary(theme, language, story_type)
        
        # Bölüm planı oluştur
        sections = await self._generate_sections(theme, language, story_type)
        
        # Karakter listesi (opsiyonel)
        characters = []
        if include_characters:
            characters = await self._extract_characters(summary, language)
        
        return {
            "theme": theme,
            "summary": summary,
            "sections": sections,
            "characters": characters,
            "story_type": story_type,
            "language": language,
        }
    
    async def _generate_summary(
        self,
        theme: str,
        language: str,
        story_type: str
    ) -> str:
        """Hikâye özeti üretir."""
        if language == "tr":
            prompt = f"""Aşağıdaki temaya göre bir {story_type} hikâyesi için kısa bir özet oluştur:

Tema: {theme}

Özet 2-3 paragraf uzunluğunda olsun ve hikâyenin ana hatlarını, karakterleri ve olay örgüsünü içersin."""
        else:
            prompt = f"""Create a short summary for a {story_type} story based on the following theme:

Theme: {theme}

The summary should be 2-3 paragraphs long and include the main plot, characters, and storyline."""
        
        try:
            if self.story_service.openai_client:
                response = self.story_service.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen bir hikâye planlamacısısın. Hikâyeler için özet ve plan oluşturursun."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Özet üretim hatası: {e}")
        
        # Fallback
        return f"Bu hikâye {theme} teması etrafında gelişecek. Karakterler maceralı bir yolculuğa çıkacak ve birçok zorlukla karşılaşacaklar."
    
    async def _generate_sections(
        self,
        theme: str,
        language: str,
        story_type: str
    ) -> List[Dict]:
        """Bölüm planı oluşturur."""
        if language == "tr":
            prompt = f"""Aşağıdaki temaya göre bir {story_type} hikâyesi için bölüm planı oluştur:

Tema: {theme}

Lütfen 3-5 bölüm oluştur. Her bölüm için:
- Başlık
- Kısa açıklama (1-2 cümle)

JSON formatında döndür:
[
  {{"title": "Bölüm Başlığı", "description": "Bölüm açıklaması"}},
  ...
]"""
        else:
            prompt = f"""Create a section plan for a {story_type} story based on the following theme:

Theme: {theme}

Please create 3-5 sections. For each section:
- Title
- Short description (1-2 sentences)

Return in JSON format:
[
  {{"title": "Section Title", "description": "Section description"}},
  ...
]"""
        
        try:
            if self.story_service.openai_client:
                response = self.story_service.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen bir hikâye planlamacısısın. JSON formatında bölüm planları oluşturursun."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                import re
                json_str = response.choices[0].message.content.strip()
                json_str = re.sub(r'```json\n?', '', json_str)
                json_str = re.sub(r'```\n?', '', json_str)
                return json.loads(json_str)
        except Exception as e:
            print(f"Bölüm planı üretim hatası: {e}")
        
        # Fallback
        return [
            {"title": "Başlangıç", "description": "Hikâyenin başlangıcı ve karakterlerin tanıtımı"},
            {"title": "Gelişme", "description": "Olayların gelişimi ve çatışmalar"},
            {"title": "Sonuç", "description": "Hikâyenin sonu ve çözüm"},
        ]
    
    async def _extract_characters(
        self,
        summary: str,
        language: str
    ) -> List[Dict]:
        """Özetten karakterleri çıkarır."""
        if language == "tr":
            prompt = f"""Aşağıdaki hikâye özetinden karakterleri çıkar:

{summary}

Her karakter için:
- İsim
- Rol (kahraman, kötü karakter, yardımcı, vb.)
- Kısa açıklama

JSON formatında döndür:
[
  {{"name": "İsim", "role": "Rol", "description": "Açıklama"}},
  ...
]"""
        else:
            prompt = f"""Extract characters from the following story summary:

{summary}

For each character:
- Name
- Role (hero, villain, sidekick, etc.)
- Short description

Return in JSON format:
[
  {{"name": "Name", "role": "Role", "description": "Description"}},
  ...
]"""
        
        try:
            if self.story_service.openai_client:
                response = self.story_service.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen bir karakter analizcisisin. Hikâye özetlerinden karakterleri çıkarırsın."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.7
                )
                import re
                json_str = response.choices[0].message.content.strip()
                json_str = re.sub(r'```json\n?', '', json_str)
                json_str = re.sub(r'```\n?', '', json_str)
                return json.loads(json_str)
        except Exception as e:
            print(f"Karakter çıkarma hatası: {e}")
        
        # Fallback
        return [
            {"name": "Ana Karakter", "role": "kahraman", "description": "Hikâyenin ana karakteri"},
        ]

