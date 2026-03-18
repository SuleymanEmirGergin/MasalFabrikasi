from typing import Dict, List, Optional
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None
import base64
from io import BytesIO
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class SharingEnhancedService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.sharing_file = os.path.join(settings.STORAGE_PATH, "sharing_links.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.sharing_file):
            with open(self.sharing_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def generate_qr_code(self, story_id: str) -> str:
        """QR kod oluşturur."""
        base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
        story_url = f"{base_url}/share/story/{story_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(story_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    
    def create_custom_link(
        self,
        story_id: str,
        custom_slug: Optional[str] = None,
        expires_at: Optional[str] = None
    ) -> Dict:
        """Özel paylaşım linki oluşturur."""
        slug = custom_slug or str(uuid.uuid4())[:8]
        base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
        
        link = {
            "link_id": str(uuid.uuid4()),
            "story_id": story_id,
            "slug": slug,
            "custom_url": f"{base_url}/s/{slug}",
            "expires_at": expires_at,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        with open(self.sharing_file, 'r', encoding='utf-8') as f:
            links = json.load(f)
        links[slug] = link
        with open(self.sharing_file, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
        
        return link
    
    def generate_embed_code(
        self,
        story_id: str,
        width: int = 800,
        height: int = 600
    ) -> str:
        """Embed kodu oluşturur."""
        base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
        embed_url = f"{base_url}/embed/story/{story_id}"
        
        embed_code = f"""
<iframe 
    src="{embed_url}" 
    width="{width}" 
    height="{height}" 
    frameborder="0" 
    allowfullscreen>
</iframe>
"""
        return embed_code.strip()
    
    async def auto_share_to_social_media(
        self,
        story_id: str,
        platforms: List[str],
        access_tokens: Dict[str, str]
    ) -> Dict:
        """Sosyal medyaya otomatik paylaşım."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        results = {}
        for platform in platforms:
            token = access_tokens.get(platform)
            if token:
                # Placeholder - gerçek implementasyon için platform API'leri gerekli
                results[platform] = {
                    "shared": True,
                    "post_url": f"https://{platform}.com/post/123",
                    "shared_at": datetime.now().isoformat()
                }
            else:
                results[platform] = {
                    "shared": False,
                    "error": "Access token bulunamadı"
                }
        
        return {
            "story_id": story_id,
            "results": results
        }
    
    def track_share_analytics(
        self,
        story_id: str,
        share_type: str,
        platform: Optional[str] = None
    ):
        """Paylaşım analitiğini takip eder."""
        with open(self.sharing_file, 'r', encoding='utf-8') as f:
            links = json.load(f)
        
        # Analitik kaydı (basit örnek)
        analytics = {
            "story_id": story_id,
            "share_type": share_type,
            "platform": platform,
            "shared_at": datetime.now().isoformat()
        }
        
        # Gerçek uygulamada daha detaylı analitik sistemi olabilir
        return analytics

