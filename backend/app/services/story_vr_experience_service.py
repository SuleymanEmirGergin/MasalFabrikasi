from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryVrExperienceService:
    """Hikaye sanal gerçeklik deneyimi servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.vr_experiences_file = os.path.join(settings.STORAGE_PATH, "vr_experiences.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.vr_experiences_file):
            with open(self.vr_experiences_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_vr_scene(
        self,
        story_id: str,
        scene_description: str,
        scene_type: str = "environment"
    ) -> Dict:
        """VR sahnesi oluşturur."""
        scene_id = str(uuid.uuid4())
        
        # 360 derece görsel oluştur
        vr_image_url = await self.image_service.generate_image(
            story_text=scene_description,
            theme="vr",
            image_style="panoramic",
            image_size="2048x1024"  # 360 derece için geniş format
        )
        
        # 3D nesneler için metadata
        objects = self._extract_3d_objects(scene_description)
        
        scene = {
            "scene_id": scene_id,
            "story_id": story_id,
            "scene_type": scene_type,
            "description": scene_description,
            "vr_image_url": vr_image_url,
            "objects": objects,
            "interactions": [],
            "created_at": datetime.now().isoformat()
        }
        
        experiences = self._load_experiences()
        experiences.append(scene)
        self._save_experiences(experiences)
        
        return {
            "scene_id": scene_id,
            "vr_image_url": vr_image_url,
            "objects_count": len(objects)
        }
    
    async def create_immersive_story(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """İmmersif hikaye deneyimi oluşturur."""
        experience_id = str(uuid.uuid4())
        
        # Hikayeyi sahnelerine ayır
        scenes = self._split_into_scenes(story_text)
        
        # Her sahne için VR ortamı oluştur
        vr_scenes = []
        for i, scene_text in enumerate(scenes):
            scene = await self.create_vr_scene(
                story_id,
                scene_text,
                scene_type="immersive"
            )
            vr_scenes.append({
                "scene_number": i + 1,
                "scene_id": scene["scene_id"],
                "description": scene_text
            })
        
        experience = {
            "experience_id": experience_id,
            "story_id": story_id,
            "scenes": vr_scenes,
            "total_duration": len(vr_scenes) * 3,  # Dakika
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "experience_id": experience_id,
            "scenes_count": len(vr_scenes),
            "total_duration": experience["total_duration"]
        }
    
    async def add_interaction(
        self,
        scene_id: str,
        interaction_type: str,
        interaction_data: Dict
    ) -> Dict:
        """Sahneye etkileşim ekler."""
        experiences = self._load_experiences()
        scene = next((s for s in experiences if s["scene_id"] == scene_id), None)
        
        if not scene:
            raise ValueError("Sahne bulunamadı")
        
        interaction = {
            "interaction_id": str(uuid.uuid4()),
            "type": interaction_type,
            "data": interaction_data,
            "created_at": datetime.now().isoformat()
        }
        
        scene["interactions"].append(interaction)
        self._save_experiences(experiences)
        
        return {
            "interaction_id": interaction["interaction_id"],
            "message": "Etkileşim eklendi"
        }
    
    def _extract_3d_objects(self, description: str) -> List[Dict]:
        """3D nesneleri çıkarır."""
        objects = []
        object_keywords = ["masa", "sandalye", "kapı", "pencere", "ağaç", "taş", "ev"]
        
        for keyword in object_keywords:
            if keyword in description.lower():
                objects.append({
                    "object_id": str(uuid.uuid4()),
                    "name": keyword,
                    "type": "static",
                    "position": {"x": 0, "y": 0, "z": 0}
                })
        
        return objects[:10]
    
    def _split_into_scenes(self, text: str) -> List[str]:
        """Metni sahnelerine ayırır."""
        paragraphs = text.split('\n\n')
        scenes = [p.strip() for p in paragraphs if p.strip()]
        
        if not scenes:
            sentences = text.split('.')
            scenes = [s.strip() + '.' for s in sentences if s.strip()][:10]
        
        return scenes
    
    def _load_experiences(self) -> List[Dict]:
        """Deneyimleri yükler."""
        try:
            with open(self.vr_experiences_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_experiences(self, experiences: List[Dict]):
        """Deneyimleri kaydeder."""
        with open(self.vr_experiences_file, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, ensure_ascii=False, indent=2)

