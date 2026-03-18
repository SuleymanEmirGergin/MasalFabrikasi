from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json


class AIFeaturesAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
    
    async def summarize_story(
        self,
        story_id: str,
        summary_length: str = "medium"
    ) -> Dict:
        """Hikâyeyi özetler."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        length_map = {
            "short": "2-3 cümle",
            "medium": "1 paragraf",
            "long": "2-3 paragraf"
        }
        
        prompt = f"""
Aşağıdaki hikâyeyi {length_map.get(summary_length, '1 paragraf')} uzunluğunda özetle.

Hikâye:
{story.get('story_text', '')}

Özet:
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir özet uzmanısın. Hikâyeleri özetliyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "story_id": story_id,
                "summary": summary,
                "summary_length": summary_length,
                "original_length": len(story.get('story_text', '').split())
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_characters(
        self,
        story_id: str
    ) -> Dict:
        """Karakter analizi yapar."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        prompt = f"""
Aşağıdaki hikâyedeki karakterleri analiz et.

Hikâye:
{story.get('story_text', '')}

Her karakter için şunları belirle:
- İsim
- Rol (ana karakter, yan karakter, antagonist, vb.)
- Kişilik özellikleri
- Hikâyedeki önemi
- Gelişim

JSON formatında döndür:
{{
  "characters": [
    {{
      "name": "İsim",
      "role": "Rol",
      "personality": ["Özellik 1", "Özellik 2"],
      "importance": "high/medium/low",
      "development": "Gelişim açıklaması"
    }}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat analiz uzmanısın. Karakterleri analiz ediyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return {
                "story_id": story_id,
                "characters": result.get("characters", [])
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def suggest_themes(
        self,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[str]:
        """Tema önerileri getirir."""
        if user_id:
            all_stories = self.story_storage.get_all_stories()
            user_stories = [s for s in all_stories if s.get('user_id') == user_id]
            themes = [s.get('theme', '') for s in user_stories if s.get('theme')]
        else:
            all_stories = self.story_storage.get_all_stories()
            themes = [s.get('theme', '') for s in all_stories if s.get('theme')]
        
        # Basit öneri algoritması (gerçek uygulamada daha gelişmiş olabilir)
        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        suggestions = [t[0] for t in sorted_themes[:limit]]
        
        # Eğer yeterli tema yoksa, genel öneriler ekle
        general_themes = ["Macera", "Dostluk", "Cesaret", "Hayal Gücü", "Doğa"]
        for theme in general_themes:
            if theme not in suggestions and len(suggestions) < limit:
                suggestions.append(theme)
        
        return suggestions[:limit]
    
    async def auto_translate(
        self,
        story_id: str,
        target_language: str
    ) -> Dict:
        """Otomatik çeviri yapar."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        prompt = f"""
Aşağıdaki hikâyeyi {target_language} diline çevir. Çeviriyi doğal ve akıcı yap.

Orijinal Hikâye ({story.get('language', 'tr')}):
{story.get('story_text', '')}

Çeviri ({target_language}):
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Sen bir çevirmensin. Metinleri {target_language} diline çeviriyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                "story_id": story_id,
                "original_language": story.get('language', 'tr'),
                "target_language": target_language,
                "translated_text": translated_text
            }
        except Exception as e:
            return {"error": str(e)}

