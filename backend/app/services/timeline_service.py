from typing import List, Dict, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json
import re
from datetime import datetime


class TimelineService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
    
    async def generate_timeline(
        self,
        story_id: str
    ) -> Dict:
        """
        Hikâye için zaman çizelgesi oluşturur.
        
        Args:
            story_id: Hikâye ID'si
        
        Returns:
            Zaman çizelgesi objesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        language = story.get('language', 'tr')
        
        prompt = f"""
Aşağıdaki hikâyeyi analiz et ve olayların zaman çizelgesini oluştur. JSON formatında döndür.

Hikâye:
{story_text}

Her olay için:
- event_id: Olay ID'si
- event_description: Olay açıklaması
- timestamp: Zaman damgası (hikâye içindeki zaman)
- order: Sıra numarası
- characters_involved: İlgili karakterler
- location: Konum (varsa)
- importance: Önem seviyesi (high, medium, low)

JSON formatında döndür:
{{
  "timeline": [
    {{
      "event_id": "1",
      "event_description": "Olay açıklaması",
      "timestamp": "Başlangıç",
      "order": 1,
      "characters_involved": ["Karakter1"],
      "location": "Konum",
      "importance": "high"
    }}
  ],
  "total_events": 5,
  "time_span": "Bir gün / Bir hafta / Bir yıl"
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir hikâye analiz uzmanısın. Olayları zaman çizelgesine dönüştürüyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            timeline_text = response.choices[0].message.content
            
            # JSON'u çıkar
            if "```json" in timeline_text:
                timeline_text = timeline_text.split("```json")[1].split("```")[0].strip()
            elif "```" in timeline_text:
                timeline_text = timeline_text.split("```")[1].split("```")[0].strip()
            
            timeline = json.loads(timeline_text)
            
            return timeline
        
        except Exception as e:
            print(f"Zaman çizelgesi oluşturma hatası: {e}")
            return self._fallback_timeline(story_text)
    
    def _fallback_timeline(self, story_text: str) -> Dict:
        """Basit fallback zaman çizelgesi."""
        paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
        
        events = []
        for i, para in enumerate(paragraphs[:10], 1):  # İlk 10 paragraf
            events.append({
                "event_id": str(i),
                "event_description": para[:100] + "..." if len(para) > 100 else para,
                "timestamp": f"Olay {i}",
                "order": i,
                "characters_involved": [],
                "location": None,
                "importance": "medium"
            })
        
        return {
            "timeline": events,
            "total_events": len(events),
            "time_span": "Belirtilmemiş"
        }
    
    async def generate_character_relationship_map(
        self,
        story_id: str
    ) -> Dict:
        """
        Karakter ilişki haritası oluşturur.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        
        prompt = f"""
Aşağıdaki hikâyedeki karakterleri analiz et ve aralarındaki ilişkileri belirle. JSON formatında döndür.

Hikâye:
{story_text}

Her karakter için:
- character_name: Karakter adı
- role: Rolü (protagonist, antagonist, supporting, etc.)
- relationships: Diğer karakterlerle ilişkileri [{{"character": "İsim", "relationship": "arkadaş/düşman/aile", "description": "Açıklama"}}]

JSON formatında döndür:
{{
  "characters": [
    {{
      "character_name": "İsim",
      "role": "protagonist",
      "relationships": [
        {{
          "character": "Diğer karakter",
          "relationship": "arkadaş",
          "description": "İlişki açıklaması"
        }}
      ]
    }}
  ]
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir karakter analiz uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            relationship_text = response.choices[0].message.content
            
            if "```json" in relationship_text:
                relationship_text = relationship_text.split("```json")[1].split("```")[0].strip()
            elif "```" in relationship_text:
                relationship_text = relationship_text.split("```")[1].split("```")[0].strip()
            
            relationships = json.loads(relationship_text)
            
            return relationships
        
        except Exception as e:
            print(f"İlişki haritası oluşturma hatası: {e}")
            return {"characters": []}
    
    async def generate_story_flow_diagram(
        self,
        story_id: str
    ) -> Dict:
        """
        Hikâye akış diyagramı oluşturur.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        
        # Basit akış: giriş, gelişme, sonuç
        paragraphs = [p.strip() for p in story_text.split('\n\n') if p.strip()]
        
        total_paragraphs = len(paragraphs)
        
        # Bölümlere ayır
        intro_end = max(1, total_paragraphs // 3)
        development_end = max(intro_end + 1, (total_paragraphs * 2) // 3)
        
        flow = {
            "introduction": {
                "start": 0,
                "end": intro_end,
                "paragraphs": paragraphs[:intro_end],
                "description": "Giriş bölümü"
            },
            "development": {
                "start": intro_end,
                "end": development_end,
                "paragraphs": paragraphs[intro_end:development_end],
                "description": "Gelişme bölümü"
            },
            "conclusion": {
                "start": development_end,
                "end": total_paragraphs,
                "paragraphs": paragraphs[development_end:],
                "description": "Sonuç bölümü"
            }
        }
        
        return {
            "flow_diagram": flow,
            "total_sections": 3,
            "total_paragraphs": total_paragraphs
        }

