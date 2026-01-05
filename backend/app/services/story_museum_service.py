from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryMuseumService:
    """Hikaye müze ve sergi formatı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.museums_file = os.path.join(settings.STORAGE_PATH, "story_museums.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.museums_file):
            with open(self.museums_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_museum_exhibition(
        self,
        story_id: str,
        story_text: str,
        exhibition_theme: str = "story_journey"
    ) -> Dict:
        """Hikayeden müze sergisi oluşturur."""
        museum_id = str(uuid.uuid4())
        
        # Hikayeyi eserlere ayır
        artifacts = await self._extract_artifacts(story_text)
        
        # Her eser için görsel oluştur
        exhibition_items = []
        for i, artifact in enumerate(artifacts):
            image_url = await self.image_service.generate_image(
                story_text=artifact["description"],
                theme="museum",
                image_style="realistic"
            )
            
            exhibition_items.append({
                "item_id": str(uuid.uuid4()),
                "artifact_name": artifact["name"],
                "description": artifact["description"],
                "image_url": image_url,
                "display_order": i + 1,
                "era": artifact.get("era", "unknown"),
                "significance": artifact.get("significance", "")
            })
        
        museum = {
            "museum_id": museum_id,
            "story_id": story_id,
            "exhibition_theme": exhibition_theme,
            "items": exhibition_items,
            "created_at": datetime.now().isoformat()
        }
        
        museums = self._load_museums()
        museums.append(museum)
        self._save_museums(museums)
        
        return {
            "museum_id": museum_id,
            "items_count": len(exhibition_items),
            "message": "Müze sergisi oluşturuldu"
        }
    
    async def create_virtual_tour(
        self,
        museum_id: str,
        tour_type: str = "guided"
    ) -> Dict:
        """Sanal tur oluşturur."""
        tour_id = str(uuid.uuid4())
        
        museums = self._load_museums()
        museum = next((m for m in museums if m["museum_id"] == museum_id), None)
        
        if not museum:
            raise ValueError("Müze bulunamadı")
        
        # Tur rotası oluştur
        tour_stops = []
        for item in museum["items"]:
            tour_stops.append({
                "stop_number": len(tour_stops) + 1,
                "item_id": item["item_id"],
                "narration": f"Bu eser: {item['description']}"
            })
        
        tour = {
            "tour_id": tour_id,
            "museum_id": museum_id,
            "tour_type": tour_type,
            "stops": tour_stops,
            "estimated_duration": len(tour_stops) * 2,  # Dakika
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "tour_id": tour_id,
            "stops_count": len(tour_stops),
            "estimated_duration": tour["estimated_duration"]
        }
    
    async def _extract_artifacts(self, story_text: str) -> List[Dict]:
        """Hikayeden eserleri çıkarır."""
        prompt = f"""Aşağıdaki hikayedeki önemli nesneleri, eşyaları ve eserleri bul.
Her biri için kısa bir açıklama yap:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir müze küratörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Basit parse
        artifacts = []
        lines = response.choices[0].message.content.split('\n')
        
        for line in lines:
            if line.strip() and len(line) > 10:
                artifacts.append({
                    "name": line.split(':')[0].strip() if ':' in line else line[:30],
                    "description": line,
                    "era": "unknown",
                    "significance": ""
                })
        
        return artifacts[:10] if artifacts else [
            {"name": "Hikaye Eseri", "description": story_text[:200], "era": "unknown", "significance": ""}
        ]
    
    def _load_museums(self) -> List[Dict]:
        """Müzeleri yükler."""
        try:
            with open(self.museums_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_museums(self, museums: List[Dict]):
        """Müzeleri kaydeder."""
        with open(self.museums_file, 'w', encoding='utf-8') as f:
            json.dump(museums, f, ensure_ascii=False, indent=2)

