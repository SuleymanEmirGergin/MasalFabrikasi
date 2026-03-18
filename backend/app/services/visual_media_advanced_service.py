from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class VisualMediaAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.videos_dir = os.path.join(settings.STORAGE_PATH, "videos")
        self.animations_dir = os.path.join(settings.STORAGE_PATH, "animations")
        self.ar_vr_dir = os.path.join(settings.STORAGE_PATH, "ar_vr")
        self._ensure_directories()
    
    def _ensure_directories(self):
        for directory in [self.videos_dir, self.animations_dir, self.ar_vr_dir]:
            os.makedirs(directory, exist_ok=True)
    
    async def create_video_story(
        self,
        story_id: str,
        images: List[str],
        audio_url: Optional[str] = None,
        transition_style: str = "fade"
    ) -> Dict:
        """Video hikâye oluşturur (Fallback/Placeholder)."""
        video_id = str(uuid.uuid4())
        video_path = os.path.join(self.videos_dir, f"{video_id}.mp4")
        return {
            "video_id": video_id,
            "story_id": story_id,
            "video_path": video_path,
            "images": images,
            "audio_url": audio_url,
            "transition_style": transition_style,
            "created_at": datetime.now().isoformat()
        }

    async def generate_video_wiro(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        seconds: int = 4,
        resolution: str = "720p"
    ) -> Dict:
        """
        Wiro AI Sora-2 ile video üretir.
        """
        from app.services.wiro_client import wiro_client
        
        inputs = {
            "prompt": prompt,
            "seconds": str(seconds),
            "resolution": resolution,
            "ratio": "auto"
        }
        
        if image_url:
            inputs["inputImage"] = image_url

        try:
            # Sora-2 is a multipart model in documentation example
            result = await wiro_client.run_and_wait(
                provider="openai",
                model_slug="sora-2",
                inputs=inputs,
                is_json=False # Documentation shows -F (multipart)
            )
            
            detail = result.get("detail", {})
            if detail and detail.get("tasklist"):
                outputs = detail["tasklist"][0].get("outputs", [])
                if outputs:
                    video_url = outputs[0]["url"]
                    return {
                        "success": True,
                        "video_url": video_url,
                        "task_id": detail["tasklist"][0].get("id")
                    }
            
            return {"success": False, "error": "Video üretilemedi", "raw": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_animated_story(
        self,
        story_id: str,
        animation_style: str = "2d",
        frame_count: int = 60
    ) -> Dict:
        """Animasyonlu hikâye oluşturur."""
        animation_id = str(uuid.uuid4())
        animation_path = os.path.join(self.animations_dir, f"{animation_id}.gif")
        
        # Placeholder - gerçek implementasyon için animasyon kütüphanesi gerekli
        
        return {
            "animation_id": animation_id,
            "story_id": story_id,
            "animation_path": animation_path,
            "animation_style": animation_style,
            "frame_count": frame_count,
            "created_at": datetime.now().isoformat()
        }
    
    async def generate_3d_visualization(
        self,
        story_text: str,
        scene_description: str
    ) -> Dict:
        """3D görselleştirme oluşturur."""
        prompt = f"""
Aşağıdaki hikâye sahnesi için 3D görselleştirme açıklaması oluştur.

Hikâye: {story_text}
Sahne: {scene_description}

3D sahne açıklamasını JSON formatında döndür:
{{
  "scene_description": "3D sahne açıklaması",
  "objects": [
    {{"name": "Nesne", "position": {{"x": 0, "y": 0, "z": 0}}, "scale": 1.0}}
  ],
  "lighting": "Aydınlatma açıklaması",
  "camera": {{"position": {{"x": 0, "y": 0, "z": 5}}, "target": {{"x": 0, "y": 0, "z": 0}}}}
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir 3D görselleştirme uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            visualization_id = str(uuid.uuid4())
            return {
                "visualization_id": visualization_id,
                "scene_data": result,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_ar_scene(
        self,
        story_text: str,
        location: Optional[Dict] = None
    ) -> Dict:
        """AR sahne oluşturur."""
        ar_id = str(uuid.uuid4())
        ar_path = os.path.join(self.ar_vr_dir, f"{ar_id}.json")
        
        scene_data = {
            "ar_id": ar_id,
            "story_text": story_text,
            "location": location or {},
            "ar_objects": [],
            "interactions": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(ar_path, 'w', encoding='utf-8') as f:
            json.dump(scene_data, f, ensure_ascii=False, indent=2)
        
        return scene_data
    
    async def generate_vr_experience(
        self,
        story_id: str,
        immersion_level: str = "medium"
    ) -> Dict:
        """VR deneyimi oluşturur."""
        vr_id = str(uuid.uuid4())
        vr_path = os.path.join(self.ar_vr_dir, f"{vr_id}_vr.json")
        
        vr_data = {
            "vr_id": vr_id,
            "story_id": story_id,
            "immersion_level": immersion_level,
            "environments": [],
            "interactions": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(vr_path, 'w', encoding='utf-8') as f:
            json.dump(vr_data, f, ensure_ascii=False, indent=2)
        
        return vr_data

