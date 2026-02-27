from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json
import uuid
from datetime import datetime


class AIStoryCreationAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
        self.universes_file = f"{settings.STORAGE_PATH}/story_universes.json"
        self.series_file = f"{settings.STORAGE_PATH}/story_series.json"
        self._ensure_files()
    
    def _ensure_files(self):
        import os
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.universes_file, self.series_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_multi_character_story(
        self,
        theme: str,
        characters: List[Dict],
        language: str = "tr",
        story_type: str = "masal"
    ) -> Dict:
        """Çoklu karakter hikâyesi oluşturur."""
        characters_desc = "\n".join([
            f"- {c.get('name')}: {c.get('description', '')} ({c.get('role', 'karakter')})"
            for c in characters
        ])
        
        prompt = f"""
Aşağıdaki karakterlerle bir {story_type} hikâyesi yaz.

Tema: {theme}
Karakterler:
{characters_desc}

Hikâyede tüm karakterlerin etkileşimde bulunması gerekiyor. Her karakterin kendine özgü kişiliği ve rolü olsun.

JSON formatında döndür:
{{
  "story_text": "Hikâye metni",
  "character_interactions": [
    {{"character": "İsim", "action": "Yaptığı eylem", "dialogue": "Söylediği söz"}}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir hikâye yazarısın. Çoklu karakter hikâyeleri yazıyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            story_id = str(uuid.uuid4())
            story = {
                "story_id": story_id,
                "theme": theme,
                "story_text": result.get("story_text", ""),
                "story_type": story_type,
                "language": language,
                "characters": characters,
                "character_interactions": result.get("character_interactions", []),
                "created_at": datetime.now().isoformat(),
                "is_multi_character": True
            }
            
            self.story_storage.save_story(story)
            return story
        except Exception as e:
            return {"error": str(e)}
    
    async def create_parallel_universe(
        self,
        base_story_id: str,
        universe_name: str,
        divergence_point: str
    ) -> Dict:
        """Paralel hikâye evreni oluşturur."""
        base_story = self.story_storage.get_story(base_story_id)
        if not base_story:
            raise ValueError("Temel hikâye bulunamadı")
        
        prompt = f"""
Aşağıdaki hikâyeden bir paralel evren oluştur. "{divergence_point}" noktasında hikâye farklı bir yöne gitsin.

Orijinal Hikâye:
{base_story.get('story_text', '')}

Ayrılma Noktası: {divergence_point}

Yeni paralel evren hikâyesini yaz. JSON formatında döndür:
{{
  "story_text": "Paralel evren hikâyesi",
  "divergence_point": "{divergence_point}",
  "differences": ["Fark 1", "Fark 2"]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir hikâye yazarısın. Paralel evrenler oluşturuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            universe_id = str(uuid.uuid4())
            universe = {
                "universe_id": universe_id,
                "base_story_id": base_story_id,
                "universe_name": universe_name,
                "story_text": result.get("story_text", ""),
                "divergence_point": divergence_point,
                "differences": result.get("differences", []),
                "created_at": datetime.now().isoformat()
            }
            
            # Evrenleri kaydet
            import os
            with open(self.universes_file, 'r', encoding='utf-8') as f:
                universes = json.load(f)
            universes.append(universe)
            with open(self.universes_file, 'w', encoding='utf-8') as f:
                json.dump(universes, f, ensure_ascii=False, indent=2)
            
            return universe
        except Exception as e:
            return {"error": str(e)}
    
    def create_story_series(
        self,
        series_name: str,
        description: str,
        user_id: str
    ) -> Dict:
        """Hikâye serisi oluşturur."""
        series_id = str(uuid.uuid4())
        series = {
            "series_id": series_id,
            "series_name": series_name,
            "description": description,
            "user_id": user_id,
            "stories": [],
            "created_at": datetime.now().isoformat()
        }
        
        import os
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        all_series.append(series)
        with open(self.series_file, 'w', encoding='utf-8') as f:
            json.dump(all_series, f, ensure_ascii=False, indent=2)
        
        return series
    
    def add_story_to_series(self, series_id: str, story_id: str) -> Dict:
        """Seriye hikâye ekler."""
        import os
        with open(self.series_file, 'r', encoding='utf-8') as f:
            all_series = json.load(f)
        
        series = next((s for s in all_series if s.get('series_id') == series_id), None)
        if not series:
            raise ValueError("Seri bulunamadı")
        
        if story_id not in series.get('stories', []):
            series['stories'].append(story_id)
            series['updated_at'] = datetime.now().isoformat()
        
        with open(self.series_file, 'w', encoding='utf-8') as f:
            json.dump(all_series, f, ensure_ascii=False, indent=2)
        
        return series
    
    async def auto_continue_story(
        self,
        story_id: str,
        continuation_length: str = "medium"
    ) -> Dict:
        """Hikâyeyi otomatik devam ettirir."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        length_map = {
            "short": "2-3 paragraf",
            "medium": "4-6 paragraf",
            "long": "8-10 paragraf"
        }
        
        prompt = f"""
Aşağıdaki hikâyeyi devam ettir. {length_map.get(continuation_length, '4-6 paragraf')} uzunluğunda devam et.

Mevcut Hikâye:
{story.get('story_text', '')}

Devamını yaz. Sadece devam metnini döndür.
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir hikâye yazarısın. Hikâyeleri doğal bir şekilde devam ettiriyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            continuation = response.choices[0].message.content.strip()
            
            # Hikâyeyi güncelle
            story['story_text'] += "\n\n" + continuation
            story['updated_at'] = datetime.now().isoformat()
            self.story_storage.save_story(story)
            
            return {
                "story_id": story_id,
                "continuation": continuation,
                "updated_story": story
            }
        except Exception as e:
            return {"error": str(e)}

