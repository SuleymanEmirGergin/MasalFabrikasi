from typing import Dict, Optional, List
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class ARVRService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.ar_data_file = os.path.join(settings.STORAGE_PATH, "ar_vr_data.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.ar_data_file):
            with open(self.ar_data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_ar_scene(self, story_id: str, scene_data: Dict) -> Dict:
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        ar_scene = {
            "scene_id": str(uuid.uuid4()),
            "story_id": story_id,
            "scene_data": scene_data,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.ar_data_file, 'r', encoding='utf-8') as f:
            ar_data = json.load(f)
        if story_id not in ar_data:
            ar_data[story_id] = []
        ar_data[story_id].append(ar_scene)
        with open(self.ar_data_file, 'w', encoding='utf-8') as f:
            json.dump(ar_data, f, ensure_ascii=False, indent=2)
        
        return ar_scene
    
    def get_ar_data(self, story_id: str) -> List[Dict]:
        with open(self.ar_data_file, 'r', encoding='utf-8') as f:
            ar_data = json.load(f)
        return ar_data.get(story_id, [])
    
    def generate_3d_character(self, character_id: str, character_data: Dict) -> Dict:
        return {
            "character_id": character_id,
            "3d_model_url": f"/storage/3d_models/{character_id}.glb",
            "texture_url": f"/storage/textures/{character_id}.png",
            "note": "3D model oluşturma için ek servis gerekli"
        }

