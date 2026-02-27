import time
import uuid
from PIL import Image
import time
import uuid
from PIL import Image
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.wiro_client import wiro_client
from app.services.cloud_storage_service import cloud_storage_service
from app.core.resilience import openai_circuit_breaker, retry_on_failure

class ImageService:
    def __init__(self):
        self.client = None
        
        # Standard OpenAI client for compatible providers
        if settings.IMAGEN_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.IMAGEN_API_KEY,
                base_url=settings.GPT_BASE_URL
            )
        # Fallback for DALL-E
        self.openai_client = None
        if settings.OPENAI_API_KEY:
             self.openai_client = AsyncOpenAI(
                 api_key=settings.OPENAI_API_KEY
             )
    
    @retry_on_failure(max_retries=2, delay=2.0)
    async def generate_image(
        self, 
        story_text: str, 
        theme: str,
        image_style: str = "fantasy",
        image_size: str = "1024x1024"
    ) -> str:
        """
        Seri üretim (hızlı) görsel üretimi için Imagen-v4-fast kullanır.
        """
        prompt = self._create_image_prompt(story_text, theme, image_style)
        
        # Specialized Wiro Run/Poll path
        if "imagen" in settings.IMAGEN_FAST_MODEL.lower() and "wiro" in settings.GPT_BASE_URL:
            try:
                inputs = {
                    "prompt": prompt,
                    "samples": "1",
                    "seed": str(int(time.time()) % 1000000000),
                    "enhancePrompt": "true",
                    "addWatermark": "true",
                    "aspectRatio": "1:1" if "1024x1024" in image_size else "16:9",
                    "personGeneration": "allow_adult",
                    "language": "tr",
                    "safetySetting": "block_medium_and_above"
                }
                parts = settings.IMAGEN_FAST_MODEL.split("/")
                provider = parts[0] if len(parts) > 1 else "google"
                model_slug = parts[1] if len(parts) > 1 else parts[0]
                
                result = await wiro_client.run_and_wait(provider, model_slug, inputs, is_json=True)
                detail = result.get("detail", {})
                if detail and detail.get("tasklist"):
                    outputs = detail["tasklist"][0].get("outputs", [])
                    if outputs:
                        return await self._save_image_from_url(outputs[0]["url"])
            except Exception as e:
                print(f"Wiro Imagen Fast error: {e}")
        
        # Fallback to standard OpenAI compatible client
        if not self.client:
            return self._generate_placeholder_image(image_size)
            
        try:
            response = await self.client.images.generate(
                model=settings.IMAGEN_FAST_MODEL,
                prompt=prompt,
                size=image_size,
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            return await self._save_image_from_url(image_url)
        except Exception as e:
            print(f"Imagen Fast generation error: {e}")
            return self._generate_placeholder_image(image_size)

    @retry_on_failure(max_retries=2, delay=2.0)
    async def generate_hero_image(
        self,
        story_text: str,
        theme: str,
        image_style: str = "fantasy"
    ) -> str:
        """
        Kapak/Hero görsel için Imagen-v4-ultra kullanır.
        """
        prompt = self._create_image_prompt(story_text, theme, image_style)
        
        # Specialized Wiro Run/Poll path
        if "imagen" in settings.IMAGEN_ULTRA_MODEL.lower() and "wiro" in settings.GPT_BASE_URL:
            try:
                inputs = {
                    "prompt": prompt,
                    "seed": str(int(time.time()) % 1000000000), # Random seed
                    "enhancePrompt": "true",
                    "addWatermark": "true",
                    "aspectRatio": "1:1",
                    "personGeneration": "allow_adult",
                    "language": "tr",
                    "safetySetting": "block_medium_and_above"
                }
                parts = settings.IMAGEN_ULTRA_MODEL.split("/")
                provider = parts[0] if len(parts) > 1 else "google"
                model_slug = parts[1] if len(parts) > 1 else parts[0]
                
                result = await wiro_client.run_and_wait(provider, model_slug, inputs, is_json=True)
                detail = result.get("detail", {})
                if detail and detail.get("tasklist"):
                    outputs = detail["tasklist"][0].get("outputs", [])
                    if outputs:
                        return await self._save_image_from_url(outputs[0]["url"])
            except Exception as e:
                print(f"Wiro Imagen Ultra error: {e}")

        if not self.client:
            return self._generate_placeholder_image("1024x1024")

        try:
            response = await self.client.images.generate(
                model=settings.IMAGEN_ULTRA_MODEL,
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url
            return await self._save_image_from_url(image_url)
        except Exception as e:
            print(f"Imagen Ultra generation error: {e}")
            return await self.generate_image(story_text, theme, image_style)

    async def _run_replicate(self, model: str, input_data: dict):
        """Replicate API ile görsel üretir."""
        import replicate
        try:
            output = await replicate.async_run(
                model,
                input=input_data
            )
            return output
        except Exception as e:
            print(f"Replicate API hatası: {e}")
            raise
    
    def _create_image_prompt(self, story_text: str, theme: str, image_style: str) -> str:
        """Görsel üretimi için prompt oluşturur."""
        # Stil açıklamaları
        style_descriptions = {
            "fantasy": "fantasy art style, magical, colorful, detailed, enchanting atmosphere",
            "realistic": "photorealistic, highly detailed, professional photography, sharp focus",
            "cartoon": "cartoon style, vibrant colors, playful, animated, Disney-like",
            "oil_painting": "oil painting style, classical art, rich colors, brush strokes, museum quality",
            "watercolor": "watercolor painting, soft colors, artistic, flowing, delicate",
            "digital_art": "digital art, modern, sleek, high quality, concept art",
            "anime": "anime style, Japanese animation, vibrant, detailed, manga-inspired",
            "sketch": "pencil sketch, black and white, artistic, detailed linework",
        }
        
        style_desc = style_descriptions.get(image_style, style_descriptions["fantasy"])
        
        # Hikâyenin ilk cümlelerinden veya temadan görsel prompt oluştur
        prompt = f"Beautiful illustration of {theme}, {style_desc}"
        return prompt
    
    @openai_circuit_breaker.call
    async def _generate_with_dalle(self, prompt: str, image_size: str = "1024x1024") -> str:
        """DALL-E API ile görsel üretir."""
        if not self.openai_client:
             return self._generate_placeholder_image(image_size)

        # DALL-E-3 için geçerli boyutlar
        dalle3_sizes = ["1024x1024", "1024x1792", "1792x1024"]
        # DALL-E-2 için geçerli boyutlar
        dalle2_sizes = ["256x256", "512x512", "1024x1024"]
        
        # Boyutu kontrol et ve ayarla
        if image_size not in dalle3_sizes:
            image_size = "1024x1024"
        
        try:
            response = await self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=image_size,
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            
            # Görseli indirip kaydet
            return await self._save_image_from_url(image_url)
        except Exception as e:
            print(f"DALL-E-3 API hatası: {e}")
            # DALL-E-3 yoksa DALL-E-2 dene
            try:
                # DALL-E-2 için boyutu ayarla
                if image_size not in dalle2_sizes:
                    image_size = "1024x1024"
                
                response = await self.openai_client.images.generate(
                    model="dall-e-2",
                    prompt=prompt,
                    size=image_size,
                    n=1,
                )
                image_url = response.data[0].url
                return await self._save_image_from_url(image_url)
            except Exception as e2:
                print(f"DALL-E-2 API hatası: {e2}")
                return self._generate_placeholder_image(image_size)
    
    async def _generate_with_stable_diffusion(self, prompt: str, image_size: str = "1024x1024") -> str:
        """Stable Diffusion ile görsel üretir."""
        try:
            # Boyutu parse et
            width, height = self._parse_size(image_size)
            
            image = self.sd_pipeline(
                prompt, 
                num_inference_steps=50,
                width=width,
                height=height
            ).images[0]
            
            # Görseli kaydet
            image_id = str(uuid.uuid4())
            image_path = f"{settings.STORAGE_PATH}/images/{image_id}.png"
            image.save(image_path)
            
            # URL döndür
            return f"/storage/images/{image_id}.png"
        except Exception as e:
            print(f"Stable Diffusion hatası: {e}")
            return self._generate_placeholder_image(image_size)
    
    def _parse_size(self, size_str: str) -> tuple:
        """Boyut string'ini (width, height) tuple'ına çevirir."""
        try:
            width, height = map(int, size_str.split('x'))
            # Minimum ve maksimum boyutları kontrol et
            width = max(256, min(width, 2048))
            height = max(256, min(height, 2048))
            return (width, height)
        except:
            return (1024, 1024)
    
    async def _save_image_from_url(self, url: str) -> str:
        """URL'den görsel indirip kaydeder."""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            image_id = str(uuid.uuid4())
            image_path = f"{settings.STORAGE_PATH}/images/{image_id}.png"
            
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            # Upload to Cloudinary (will delete local file if successful)
            cloudinary_url = await cloud_storage_service.upload_image(
                image_path,
                folder="stories",
                public_id=f"story_{image_id}"
            )
            
            return cloudinary_url
    
    def _generate_placeholder_image(self, image_size: str = "1024x1024") -> str:
        """Placeholder görsel oluşturur."""
        # Boyutu parse et
        width, height = self._parse_size(image_size)
        
        # Basit bir placeholder görsel oluştur
        image = Image.new('RGB', (width, height), color='lightblue')
        image_id = str(uuid.uuid4())
        image_path = f"{settings.STORAGE_PATH}/images/{image_id}.png"
        image.save(image_path)
        return f"/storage/images/{image_id}.png"
