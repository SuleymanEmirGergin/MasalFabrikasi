from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryMapService:
    """Hikaye coğrafya ve harita oluşturma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.maps_file = os.path.join(settings.STORAGE_PATH, "story_maps.json")
        self.maps_path = os.path.join(settings.STORAGE_PATH, "maps")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.maps_path, exist_ok=True)
        if not os.path.exists(self.maps_file):
            with open(self.maps_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_story_map(
        self,
        story_id: str,
        story_text: str,
        map_style: str = "fantasy"
    ) -> Dict:
        """Hikayeden harita oluşturur."""
        map_id = str(uuid.uuid4())
        
        # Hikayedeki yerleri çıkar
        locations = self._extract_locations(story_text)
        
        # Harita görseli oluştur
        map_description = f"{map_style} harita: " + ", ".join([loc["name"] for loc in locations])
        map_image_url = await self.image_service.generate_image(
            story_text=map_description,
            theme="map",
            image_style=map_style,
            image_size="1024x1024"
        )
        
        story_map = {
            "map_id": map_id,
            "story_id": story_id,
            "map_style": map_style,
            "locations": locations,
            "map_image_url": map_image_url,
            "created_at": datetime.now().isoformat()
        }
        
        maps = self._load_maps()
        maps.append(story_map)
        self._save_maps(maps)
        
        return {
            "map_id": map_id,
            "locations_count": len(locations),
            "map_image_url": map_image_url
        }
    
    async def add_location_to_map(
        self,
        map_id: str,
        location_name: str,
        coordinates: Dict[str, float],
        location_type: str = "city"
    ) -> Dict:
        """Haritaya yer ekler."""
        maps = self._load_maps()
        story_map = next((m for m in maps if m["map_id"] == map_id), None)
        
        if not story_map:
            raise ValueError("Harita bulunamadı")
        
        location = {
            "location_id": str(uuid.uuid4()),
            "name": location_name,
            "coordinates": coordinates,
            "type": location_type,
            "created_at": datetime.now().isoformat()
        }
        
        story_map["locations"].append(location)
        self._save_maps(maps)
        
        return {
            "location_id": location["location_id"],
            "message": "Yer haritaya eklendi"
        }
    
    async def create_route_map(
        self,
        story_id: str,
        locations: List[Dict],
        route_type: str = "journey"
    ) -> Dict:
        """Yolculuk haritası oluşturur."""
        route_map_id = str(uuid.uuid4())
        
        route_description = f"{route_type} haritası: " + " -> ".join([loc["name"] for loc in locations])
        route_image_url = await self.image_service.generate_image(
            story_text=route_description,
            theme="route_map",
            image_style="illustration"
        )
        
        route_map = {
            "route_map_id": route_map_id,
            "story_id": story_id,
            "route_type": route_type,
            "locations": locations,
            "route_image_url": route_image_url,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "route_map_id": route_map_id,
            "locations_count": len(locations),
            "route_image_url": route_image_url
        }
    
    def _extract_locations(self, text: str) -> List[Dict]:
        """Yerleri çıkarır."""
        locations = []
        location_keywords = {
            "şehir": "city",
            "köy": "village",
            "kale": "castle",
            "orman": "forest",
            "dağ": "mountain",
            "nehir": "river",
            "deniz": "sea",
            "ada": "island",
            "çöl": "desert",
            "vadi": "valley"
        }
        
        text_lower = text.lower()
        for keyword_tr, keyword_en in location_keywords.items():
            if keyword_tr in text_lower or keyword_en in text_lower:
                locations.append({
                    "location_id": str(uuid.uuid4()),
                    "name": keyword_tr.capitalize(),
                    "type": keyword_en,
                    "coordinates": {
                        "x": len(locations) * 0.1,
                        "y": len(locations) * 0.1
                    }
                })
        
        return locations[:15]
    
    async def get_map(self, map_id: str) -> Optional[Dict]:
        """Haritayı getirir."""
        maps = self._load_maps()
        return next((m for m in maps if m["map_id"] == map_id), None)
    
    def _load_maps(self) -> List[Dict]:
        """Haritaları yükler."""
        try:
            with open(self.maps_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_maps(self, maps: List[Dict]):
        """Haritaları kaydeder."""
        with open(self.maps_file, 'w', encoding='utf-8') as f:
            json.dump(maps, f, ensure_ascii=False, indent=2)

