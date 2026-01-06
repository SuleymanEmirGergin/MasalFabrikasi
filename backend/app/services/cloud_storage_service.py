import os
from typing import Optional, Dict
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.core.config import settings
from app.core.supabase import supabase

logger = logging.getLogger(__name__)

class CloudStorageService:
    """
    Supabase Storage tabanlı cloud storage servisi.
    Görsel ve ses dosyalarını Supabase Storage'a yükler.
    """
    
    def __init__(self):
        self.enabled = bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)
        self.client = supabase
        
        if self.enabled:
            logger.info("✅ Supabase Storage configured successfully (using central client)")
        else:
            logger.warning("⚠️ Supabase credentials missing (SUPABASE_URL or SUPABASE_SERVICE_KEY)")

        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Bucket names
        self.buckets = {
            "image": "images",
            "audio": "audio"
        }

    async def initialize_buckets(self):
        """Uygulama başlangıcında gerekli bucketları oluşturur."""
        if not self.enabled:
            return

        for bucket_key, bucket_name in self.buckets.items():
            await self._ensure_bucket_exists(bucket_name)

    async def _ensure_bucket_exists(self, bucket_name: str):
        """Bucket yoksa oluşturur (Not: Service key gerektirir)"""
        if not self.enabled or not self.client:
            return

        try:
            # List buckets and check if exists
            buckets = self.client.storage.list_buckets()
            existing = [b.name for b in buckets]
            
            if bucket_name not in existing:
                self.client.storage.create_bucket(bucket_name, options={"public": True})
                logger.info(f"Bucket created: {bucket_name}")
        except Exception as e:
            logger.warning(f"Bucket check/create failed for {bucket_name}: {e}")

    async def upload_image(
        self, 
        file_path: str, 
        folder: str = "stories",
        public_id: Optional[str] = None,
        transformations: Optional[Dict] = None
    ) -> str:
        """
        Upload image to Supabase Storage.
        """
        if not self.enabled:
            logger.warning("Supabase not configured, returning local path")
            if "storage" in file_path:
                return f"/storage{file_path.split('storage')[1].replace(os.sep, '/')}"
            return file_path
        
        bucket_name = self.buckets["image"]
        
        try:
            # Dosya adını belirle
            file_name = os.path.basename(file_path)
            if public_id:
                # public_id varsa uzantısını koruyarak kullan
                ext = file_name.split('.')[-1]
                storage_path = f"{folder}/{public_id}.{ext}"
            else:
                storage_path = f"{folder}/{file_name}"

            # Asenkron upload
            loop = asyncio.get_event_loop()
            
            def _upload():
                # WebP Dönüştürme ve Optimizasyon
                from PIL import Image
                import io

                with open(file_path, 'rb') as f:
                    img = Image.open(f)
                    
                    # RGB'ye çevir (PNG transparanlıklarını korumak için gerekirse RGBA kalsa da WebP destekler)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")
                    
                    # Bellekte WebP oluştur
                    output = io.BytesIO()
                    img.save(output, format="WEBP", quality=80)
                    output.seek(0)
                    
                    # Storage yolu güncelle (.webp uzantısı ekle)
                    nonlocal storage_path
                    if not storage_path.endswith(".webp"):
                        storage_path = os.path.splitext(storage_path)[0] + ".webp"

                    self.client.storage.from_(bucket_name).upload(
                        path=storage_path,
                        file=output,
                        file_options={"content-type": "image/webp", "upsert": "true"}
                    )
                
                # Public URL al
                return self.client.storage.from_(bucket_name).get_public_url(storage_path)

            public_url = await loop.run_in_executor(self.executor, _upload)
            
            logger.info(f"✅ Image uploaded to Supabase: {public_url}")
            
            # Local dosyayı sil
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Supabase upload failed: {e}")
            # Fallback to local
            if "storage" in file_path:
                return f"/storage{file_path.split('storage')[1].replace(os.sep, '/')}"
            return file_path

    async def upload_audio(
        self,
        file_path: str,
        folder: str = "audio",
        public_id: Optional[str] = None
    ) -> str:
        """
        Upload audio to Supabase Storage.
        """
        if not self.enabled:
            return file_path
            
        bucket_name = self.buckets["audio"]
        
        try:
            file_name = os.path.basename(file_path)
            if public_id:
                ext = file_name.split('.')[-1]
                storage_path = f"{folder}/{public_id}.{ext}"
            else:
                storage_path = f"{folder}/{file_name}"

            loop = asyncio.get_event_loop()
            
            def _upload():
                with open(file_path, 'rb') as f:
                    self.client.storage.from_(bucket_name).upload(
                        path=storage_path,
                        file=f,
                        file_options={"content-type": "audio/mpeg", "upsert": "true"}
                    )
                return self.client.storage.from_(bucket_name).get_public_url(storage_path)

            public_url = await loop.run_in_executor(self.executor, _upload)
            
            logger.info(f"✅ Audio uploaded to Supabase: {public_url}")
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
                    
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Supabase audio upload failed: {e}")
            if "storage" in file_path:
                return f"/storage{file_path.split('storage')[1].replace(os.sep, '/')}"
            return file_path

    async def delete_file(self, public_url: str):
        """Delete file from Supabase by URL."""
        if not self.enabled:
            return

        try:
            # URL'den path'i çıkar
            # Örn: https://.../storage/v1/object/public/images/stories/file.png
            # Path: stories/file.png ve bucket: images
            
            parts = public_url.split("/public/")
            if len(parts) < 2:
                return
            
            bucket_and_path = parts[1].split("/", 1)
            bucket_name = bucket_and_path[0]
            file_path = bucket_and_path[1]
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                lambda: self.client.storage.from_(bucket_name).remove([file_path])
            )
            logger.info(f"✅ Deleted from Supabase: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Supabase delete failed: {e}")

# Global instance
cloud_storage_service = CloudStorageService()
