from typing import List, Dict, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json


class MediaSearchService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
    
    async def search_by_image(self, image_description: str, limit: int = 10) -> List[Dict]:
        """Görsel açıklamasına göre hikâye arar."""
        prompt = f"""
Aşağıdaki görsel açıklamasına uygun hikâye temalarını belirle.

Görsel Açıklaması: {image_description}

JSON formatında döndür:
{{
  "themes": ["tema1", "tema2", "tema3"],
  "keywords": ["kelime1", "kelime2"]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir görsel analiz uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            themes = result.get('themes', [])
            
            # Temalara göre hikâyeleri bul
            all_stories = self.story_storage.get_all_stories()
            matching = []
            
            for story in all_stories:
                story_theme = story.get('theme', '').lower()
                if any(theme.lower() in story_theme for theme in themes):
                    matching.append(story)
            
            return matching[:limit]
        except:
            return []
    
    async def search_by_voice_tone(self, voice_description: str, limit: int = 10) -> List[Dict]:
        """Ses tonuna göre hikâye arar."""
        prompt = f"""
Aşağıdaki ses tonu açıklamasına uygun hikâye duygularını belirle.

Ses Tonu: {voice_description}

JSON formatında döndür:
{{
  "emotions": ["duygu1", "duygu2"],
  "story_types": ["tür1", "tür2"]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir ses analiz uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            emotions = result.get('emotions', [])
            
            # Duygulara göre hikâyeleri bul (basit eşleştirme)
            all_stories = self.story_storage.get_all_stories()
            matching = []
            
            for story in all_stories:
                story_text = story.get('story_text', '').lower()
                if any(emotion.lower() in story_text for emotion in emotions):
                    matching.append(story)
            
            return matching[:limit]
        except:
            return []

