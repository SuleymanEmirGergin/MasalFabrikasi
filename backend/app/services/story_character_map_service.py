from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryCharacterMapService:
    """Hikaye karakterleri ve ilişkiler haritası servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.character_maps_file = os.path.join(settings.STORAGE_PATH, "character_maps.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.character_maps_file):
            with open(self.character_maps_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def analyze_characters(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikayedeki karakterleri analiz eder."""
        prompt = f"""Aşağıdaki hikayedeki karakterleri bul ve analiz et. Her karakter için:
1. İsim
2. Rol (ana karakter, yan karakter, kötü karakter, vb.)
3. Özellikler
4. Diğer karakterlerle ilişkileri

Hikaye:
{story_text}

JSON formatında döndür."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        # Basit parse (gerçek uygulamada daha gelişmiş olmalı)
        analysis_text = response.choices[0].message.content
        
        # Karakterleri basit bir şekilde çıkar
        characters = self._extract_characters_from_text(story_text)
        relationships = self._extract_relationships(characters, story_text)
        
        character_map = {
            "story_id": story_id,
            "characters": characters,
            "relationships": relationships,
            "analyzed_at": datetime.now().isoformat()
        }
        
        maps = self._load_maps()
        maps[story_id] = character_map
        self._save_maps(maps)
        
        return character_map
    
    def _extract_characters_from_text(self, text: str) -> List[Dict]:
        """Metinden karakterleri çıkarır (basit yaklaşım)."""
        # Bu basit bir yaklaşım, gerçek uygulamada NLP kullanılmalı
        characters = []
        words = text.split()
        
        # Büyük harfle başlayan kelimeleri potansiyel karakter isimleri olarak işaretle
        potential_names = []
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 2:
                if i == 0 or words[i-1][-1] in '.!?':
                    potential_names.append(word.strip('.,!?;:'))
        
        # Tekrarları kaldır ve karakter oluştur
        unique_names = list(set(potential_names))
        for name in unique_names[:10]:  # İlk 10'u al
            characters.append({
                "character_id": str(uuid.uuid4()),
                "name": name,
                "role": "unknown",
                "traits": [],
                "mentions": text.count(name)
            })
        
        return characters
    
    def _extract_relationships(
        self,
        characters: List[Dict],
        text: str
    ) -> List[Dict]:
        """Karakterler arası ilişkileri çıkarır."""
        relationships = []
        
        for i, char1 in enumerate(characters):
            for char2 in characters[i+1:]:
                # Aynı cümlede geçiyor mu kontrol et
                sentences = text.split('.')
                for sentence in sentences:
                    if char1["name"] in sentence and char2["name"] in sentence:
                        relationships.append({
                            "relationship_id": str(uuid.uuid4()),
                            "character1_id": char1["character_id"],
                            "character2_id": char2["character_id"],
                            "type": "mentioned_together",
                            "context": sentence.strip()
                        })
                        break
        
        return relationships
    
    async def get_character_map(self, story_id: str) -> Optional[Dict]:
        """Karakter haritasını getirir."""
        maps = self._load_maps()
        return maps.get(story_id)
    
    async def update_character(
        self,
        story_id: str,
        character_id: str,
        updates: Dict
    ) -> Dict:
        """Karakter bilgilerini günceller."""
        maps = self._load_maps()
        character_map = maps.get(story_id)
        
        if not character_map:
            raise ValueError("Karakter haritası bulunamadı")
        
        character = next(
            (c for c in character_map["characters"] if c["character_id"] == character_id),
            None
        )
        
        if not character:
            raise ValueError("Karakter bulunamadı")
        
        character.update(updates)
        character_map["updated_at"] = datetime.now().isoformat()
        
        self._save_maps(maps)
        
        return {"message": "Karakter güncellendi", "character": character}
    
    def _load_maps(self) -> Dict:
        """Haritaları yükler."""
        try:
            with open(self.character_maps_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_maps(self, maps: Dict):
        """Haritaları kaydeder."""
        with open(self.character_maps_file, 'w', encoding='utf-8') as f:
            json.dump(maps, f, ensure_ascii=False, indent=2)

