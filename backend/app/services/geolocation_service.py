from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class GeolocationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.locations_file = os.path.join(settings.STORAGE_PATH, "story_locations.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Konumlar dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.locations_file):
            with open(self.locations_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def set_story_location(
        self,
        story_id: str,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict:
        """
        Hikâyeye konum ekler.
        
        Args:
            story_id: Hikâye ID'si
            latitude: Enlem
            longitude: Boylam
            location_name: Konum adı (opsiyonel)
            region: Bölge (opsiyonel)
        
        Returns:
            Konum objesi
        """
        try:
            with open(self.locations_file, 'r', encoding='utf-8') as f:
                locations = json.load(f)
        except:
            locations = {}
        
        locations[story_id] = {
            "story_id": story_id,
            "latitude": latitude,
            "longitude": longitude,
            "location_name": location_name,
            "region": region,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.locations_file, 'w', encoding='utf-8') as f:
            json.dump(locations, f, ensure_ascii=False, indent=2)
        
        return locations[story_id]
    
    def get_story_location(self, story_id: str) -> Optional[Dict]:
        """Hikâyenin konumunu getirir."""
        try:
            with open(self.locations_file, 'r', encoding='utf-8') as f:
                locations = json.load(f)
            return locations.get(story_id)
        except:
            return None
    
    def get_nearby_stories(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Yakındaki hikâyeleri getirir.
        
        Args:
            latitude: Enlem
            longitude: Boylam
            radius_km: Yarıçap (kilometre)
            limit: Maksimum sonuç sayısı
        
        Returns:
            Yakındaki hikâyeler listesi
        """
        try:
            with open(self.locations_file, 'r', encoding='utf-8') as f:
                locations = json.load(f)
        except:
            return []
        
        nearby_stories = []
        
        for story_id, location_data in locations.items():
            story_lat = location_data.get('latitude')
            story_lon = location_data.get('longitude')
            
            if story_lat and story_lon:
                distance = self._calculate_distance(
                    latitude, longitude,
                    story_lat, story_lon
                )
                
                if distance <= radius_km:
                    story = self.story_storage.get_story(story_id)
                    if story:
                        nearby_stories.append({
                            "story": story,
                            "distance_km": round(distance, 2),
                            "location": location_data
                        })
        
        # Mesafeye göre sırala
        nearby_stories.sort(key=lambda x: x['distance_km'])
        
        return nearby_stories[:limit]
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        İki nokta arasındaki mesafeyi hesaplar (Haversine formülü).
        Sonuç kilometre cinsinden.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Dereceyi radyana çevir
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formülü
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Dünya yarıçapı (km)
        R = 6371.0
        
        distance = R * c
        return distance
    
    def get_regional_stories(
        self,
        region: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Bölgesel hikâyeleri getirir.
        
        Args:
            region: Bölge adı
            limit: Maksimum sonuç sayısı
        
        Returns:
            Bölgesel hikâyeler listesi
        """
        try:
            with open(self.locations_file, 'r', encoding='utf-8') as f:
                locations = json.load(f)
        except:
            return []
        
        regional_stories = []
        
        for story_id, location_data in locations.items():
            if location_data.get('region', '').lower() == region.lower():
                story = self.story_storage.get_story(story_id)
                if story:
                    regional_stories.append({
                        "story": story,
                        "location": location_data
                    })
        
        return regional_stories[:limit]
    
    def get_location_based_recommendations(
        self,
        user_latitude: float,
        user_longitude: float,
        limit: int = 10
    ) -> List[Dict]:
        """
        Konum bazlı hikâye önerileri getirir.
        """
        # Yakındaki hikâyeleri al
        nearby = self.get_nearby_stories(user_latitude, user_longitude, radius_km=50.0, limit=limit)
        
        return [item['story'] for item in nearby]

