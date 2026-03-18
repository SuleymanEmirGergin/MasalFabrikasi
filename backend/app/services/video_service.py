import os
import uuid
import httpx
import time
from typing import Optional
from app.core.config import settings
from app.services.wiro_client import wiro_client
from app.services.cloud_storage_service import cloud_storage_service

class VideoService:
    async def generate_video(
        self,
        image_url: str,
        prompt: str,
        story_id: Optional[str] = None
    ) -> str:
        """
        Wiro Veo3 modelini kullanarak bir görselden kısa video üretir.
        """
        try:
            # Wiro works with form-data (Multipart/Form-Data) for Veo3
            inputs = {
                "inputImage": image_url,
                "prompt": prompt,
                "generateAudio": "true",
                "aspectRatio": "match_input_image",
                "resolution": settings.VIDEO_RESOLUTION,
                "enhancePrompt": "true",
                "personGeneration": "allow_adult",
                "durationSeconds": str(settings.VIDEO_DURATION),
                "seed": str(int(time.time()) % 1000000000)
            }
            
            # google/veo3-fast -> provider=google, model=veo3-fast
            parts = settings.VIDEO_MODEL.split("/")
            provider = parts[0] if len(parts) > 1 else "google"
            model_slug = parts[1] if len(parts) > 1 else parts[0]
            
            # Veo3 prefers multipart for fields even when no local files are sent
            # Wiro run and wait handles the polling
            result = await wiro_client.run_and_wait(
                provider, 
                model_slug, 
                inputs, 
                is_json=False # Veo3 specified as multipart/form-data in example
            )
            
            detail = result.get("detail", {})
            if detail and detail.get("tasklist"):
                outputs = detail["tasklist"][0].get("outputs", [])
                if outputs:
                    video_url = outputs[0]["url"]
                    return await self._save_video_from_url(video_url, story_id)
            
            print(f"Wiro video generation failed: {result}")
            return ""
            
        except Exception as e:
            print(f"Video generation error: {e}")
            return ""

    async def _save_video_from_url(self, url: str, story_id: Optional[str]) -> str:
        """URL'den videoyu indirip buluta kaydeder."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            video_id = story_id or str(uuid.uuid4())
            temp_path = f"{settings.STORAGE_PATH}/video/{video_id}.mp4"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            # Cloud storage upload
            cloud_url = await cloud_storage_service.upload_video(
                temp_path,
                folder="stories/videos",
                public_id=f"story_video_{video_id}"
            )
            
            return cloud_url

video_service = VideoService()
