from typing import Dict, Optional
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None
from io import BytesIO
import base64
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class SharingService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.qr_codes_path = os.path.join(settings.STORAGE_PATH, "qr_codes")
        self.share_links_file = os.path.join(settings.STORAGE_PATH, "share_links.json")
        self._ensure_directory()
        self._ensure_file()
    
    def _ensure_directory(self):
        """QR kod dizinini oluşturur."""
        os.makedirs(self.qr_codes_path, exist_ok=True)
    
    def _ensure_file(self):
        """Paylaşım linkleri dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.share_links_file):
            import json
            with open(self.share_links_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def generate_qr_code(
        self,
        story_id: str,
        base_url: str = "https://masalfabrikasi.com"
    ) -> Dict:
        """
        Hikâye için QR kod oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            base_url: Base URL (QR kod linki için)
        
        Returns:
            QR kod bilgileri
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        share_url = f"{base_url}/story/{story_id}"
        
        # QR kod oluştur
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)
        
        # QR kod görselini oluştur
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Dosyaya kaydet
        qr_id = str(uuid.uuid4())
        qr_path = os.path.join(self.qr_codes_path, f"{qr_id}.png")
        img.save(qr_path)
        
        # Base64 encode (API response için)
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return {
            "qr_code_id": qr_id,
            "qr_code_url": f"/storage/qr_codes/{qr_id}.png",
            "qr_code_base64": f"data:image/png;base64,{img_base64}",
            "share_url": share_url,
            "story_id": story_id
        }
    
    def create_share_link(
        self,
        story_id: str,
        custom_slug: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> Dict:
        """
        Özel paylaşım linki oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            custom_slug: Özel slug (opsiyonel)
            expires_in_days: Kaç gün sonra geçersiz olsun (opsiyonel)
        
        Returns:
            Paylaşım linki bilgileri
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        import json
        
        # Slug oluştur
        if custom_slug:
            slug = custom_slug
        else:
            slug = str(uuid.uuid4())[:8]
        
        # Süre hesapla
        expires_at = None
        if expires_in_days:
            from datetime import timedelta
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        share_link = {
            "link_id": str(uuid.uuid4()),
            "slug": slug,
            "story_id": story_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "access_count": 0,
            "is_active": True
        }
        
        # Kaydet
        with open(self.share_links_file, 'r', encoding='utf-8') as f:
            links = json.load(f)
        
        links[slug] = share_link
        
        with open(self.share_links_file, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
        
        return {
            "link_id": share_link["link_id"],
            "slug": slug,
            "share_url": f"https://masalfabrikasi.com/s/{slug}",
            "expires_at": expires_at
        }
    
    def get_story_from_share_link(self, slug: str) -> Optional[Dict]:
        """Paylaşım linkinden hikâyeyi getirir."""
        import json
        
        try:
            with open(self.share_links_file, 'r', encoding='utf-8') as f:
                links = json.load(f)
            
            link_data = links.get(slug)
            if not link_data:
                return None
            
            # Süre kontrolü
            if link_data.get('expires_at'):
                expires_at = datetime.fromisoformat(link_data['expires_at'])
                if datetime.now() > expires_at:
                    return None
            
            # Aktif kontrolü
            if not link_data.get('is_active', True):
                return None
            
            # Erişim sayısını artır
            link_data['access_count'] = link_data.get('access_count', 0) + 1
            links[slug] = link_data
            
            with open(self.share_links_file, 'w', encoding='utf-8') as f:
                json.dump(links, f, ensure_ascii=False, indent=2)
            
            # Hikâyeyi getir
            story = self.story_storage.get_story(link_data.get('story_id'))
            return story
        
        except:
            return None
    
    def generate_embed_code(self, story_id: str, width: int = 600, height: int = 400) -> str:
        """
        Hikâye için embed kodu oluşturur.
        
        Args:
            story_id: Hikâye ID'si
            width: Genişlik
            height: Yükseklik
        
        Returns:
            Embed HTML kodu
        """
        base_url = "https://masalfabrikasi.com"
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
    
    def get_social_media_preview(
        self,
        story_id: str
    ) -> Dict:
        """
        Sosyal medya paylaşımı için önizleme verileri oluşturur.
        
        Args:
            story_id: Hikâye ID'si
        
        Returns:
            Önizleme verileri (Open Graph, Twitter Card vb.)
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        preview_text = story_text[:200] + "..." if len(story_text) > 200 else story_text
        
        return {
            "title": story.get('theme', 'Masal Fabrikası Hikâyesi'),
            "description": preview_text,
            "image": story.get('image_url', ''),
            "url": f"https://masalfabrikasi.com/story/{story_id}",
            "type": "article",
            "site_name": "Masal Fabrikası"
        }

