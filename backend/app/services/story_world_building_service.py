from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryWorldBuildingService:
    """Hikaye dünya yapımı (world building) servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.worlds_file = os.path.join(settings.STORAGE_PATH, "story_worlds.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.worlds_file):
            with open(self.worlds_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_world(
        self,
        story_id: str,
        story_text: str,
        world_type: str = "fantasy"
    ) -> Dict:
        """Hikayeden dünya oluşturur."""
        world_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeden detaylı bir dünya oluştur. Şunları ekle:
1. Coğrafya ve yerler
2. Kültür ve toplum
3. Tarih ve mitoloji
4. Teknoloji veya sihir sistemi
5. Önemli karakterler ve gruplar

Hikaye:
{story_text}

Dünya türü: {world_type}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir dünya yapımı uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        world_description = response.choices[0].message.content
        
        world = {
            "world_id": world_id,
            "story_id": story_id,
            "world_type": world_type,
            "description": world_description,
            "locations": [],
            "characters": [],
            "history": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Dünya öğelerini çıkar
        world["locations"] = await self._extract_locations(world_description)
        world["characters"] = await self._extract_world_characters(world_description)
        
        worlds = self._load_worlds()
        worlds.append(world)
        self._save_worlds(worlds)
        
        return {
            "world_id": world_id,
            "world_type": world_type,
            "locations_count": len(world["locations"]),
            "characters_count": len(world["characters"])
        }
    
    async def add_location(
        self,
        world_id: str,
        location_name: str,
        description: str,
        location_type: str = "city"
    ) -> Dict:
        """Dünyaya yer ekler."""
        worlds = self._load_worlds()
        world = next((w for w in worlds if w["world_id"] == world_id), None)
        
        if not world:
            raise ValueError("Dünya bulunamadı")
        
        location = {
            "location_id": str(uuid.uuid4()),
            "name": location_name,
            "description": description,
            "type": location_type,
            "created_at": datetime.now().isoformat()
        }
        
        world["locations"].append(location)
        self._save_worlds(worlds)
        
        return {
            "location_id": location["location_id"],
            "message": "Yer eklendi"
        }
    
    async def add_world_character(
        self,
        world_id: str,
        character_name: str,
        character_role: str,
        description: str
    ) -> Dict:
        """Dünyaya karakter ekler."""
        worlds = self._load_worlds()
        world = next((w for w in worlds if w["world_id"] == world_id), None)
        
        if not world:
            raise ValueError("Dünya bulunamadı")
        
        character = {
            "character_id": str(uuid.uuid4()),
            "name": character_name,
            "role": character_role,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        world["characters"].append(character)
        self._save_worlds(worlds)
        
        return {
            "character_id": character["character_id"],
            "message": "Karakter eklendi"
        }
    
    async def _extract_locations(self, world_text: str) -> List[Dict]:
        """Yerleri çıkarır."""
        # Basit yaklaşım
        locations = []
        location_keywords = ["şehir", "köy", "kale", "orman", "dağ", "nehir", "deniz", "ada"]
        
        for keyword in location_keywords:
            if keyword in world_text.lower():
                locations.append({
                    "location_id": str(uuid.uuid4()),
                    "name": keyword.capitalize(),
                    "type": keyword
                })
        
        return locations[:10]
    
    async def _extract_world_characters(self, world_text: str) -> List[Dict]:
        """Dünya karakterlerini çıkarır."""
        # Basit yaklaşım
        characters = []
        words = world_text.split()
        
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 3:
                if i == 0 or words[i-1][-1] in '.!?':
                    characters.append({
                        "character_id": str(uuid.uuid4()),
                        "name": word.strip('.,!?;:')
                    })
        
        return list({c["name"]: c for c in characters}.values())[:10]
    
    async def get_world(self, world_id: str) -> Optional[Dict]:
        """Dünyayı getirir."""
        worlds = self._load_worlds()
        return next((w for w in worlds if w["world_id"] == world_id), None)
    
    def _load_worlds(self) -> List[Dict]:
        """Dünyaları yükler."""
        try:
            with open(self.worlds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_worlds(self, worlds: List[Dict]):
        """Dünyaları kaydeder."""
        with open(self.worlds_file, 'w', encoding='utf-8') as f:
            json.dump(worlds, f, ensure_ascii=False, indent=2)

