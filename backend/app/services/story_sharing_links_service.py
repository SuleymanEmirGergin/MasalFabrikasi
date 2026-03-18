from typing import Dict, List, Optional
import json
import os
import uuid
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None
from io import BytesIO
import base64
from datetime import datetime, timedelta
from app.core.config import settings


class StorySharingLinksService:
    """Hikaye paylaşım linkleri ve QR kod servisi"""
    
    def __init__(self):
        self.sharing_links_file = os.path.join(settings.STORAGE_PATH, "sharing_links.json")
        self.qr_codes_path = os.path.join(settings.STORAGE_PATH, "qr_codes")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        os.makedirs(self.qr_codes_path, exist_ok=True)
        if not os.path.exists(self.sharing_links_file):
            with open(self.sharing_links_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_sharing_link(
        self,
        story_id: str,
        user_id: str,
        expires_in_days: Optional[int] = None,
        password: Optional[str] = None,
        allow_editing: bool = False
    ) -> Dict:
        """Paylaşım linki oluşturur."""
        link_id = str(uuid.uuid4())
        base_url = settings.BASE_URL if hasattr(settings, 'BASE_URL') else "http://localhost:8000"
        share_url = f"{base_url}/share/{link_id}"
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        link_data = {
            "link_id": link_id,
            "story_id": story_id,
            "user_id": user_id,
            "share_url": share_url,
            "password": password,
            "allow_editing": allow_editing,
            "expires_at": expires_at,
            "access_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        links = self._load_links()
        links.append(link_data)
        self._save_links(links)
        
        # QR kod oluştur
        qr_code_data = await self.generate_qr_code(share_url, link_id)
        
        return {
            "link_id": link_id,
            "share_url": share_url,
            "qr_code": qr_code_data,
            "expires_at": expires_at
        }
    
    async def generate_qr_code(
        self,
        url: str,
        link_id: str
    ) -> str:
        """QR kod oluşturur."""
        if not QRCODE_AVAILABLE:
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # QR kod dosyasını kaydet
            qr_path = os.path.join(self.qr_codes_path, f"{link_id}.png")
            img.save(qr_path)
            
            # Base64 olarak döndür
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            print(f"QR kod oluşturma hatası: {e}")
            return None
    
    async def access_shared_story(
        self,
        link_id: str,
        password: Optional[str] = None
    ) -> Dict:
        """Paylaşılan hikayeye erişir."""
        links = self._load_links()
        link = next((l for l in links if l["link_id"] == link_id), None)
        
        if not link:
            raise ValueError("Link bulunamadı")
        
        # Süre kontrolü
        if link.get("expires_at"):
            expires_at = datetime.fromisoformat(link["expires_at"])
            if datetime.now() > expires_at:
                raise ValueError("Link'in süresi dolmuş")
        
        # Şifre kontrolü
        if link.get("password") and link["password"] != password:
            raise ValueError("Yanlış şifre")
        
        # Erişim sayısını artır
        link["access_count"] = link.get("access_count", 0) + 1
        self._save_links(links)
        
        return {
            "story_id": link["story_id"],
            "allow_editing": link.get("allow_editing", False),
            "access_count": link["access_count"]
        }
    
    async def revoke_sharing_link(self, link_id: str, user_id: str) -> Dict:
        """Paylaşım linkini iptal eder."""
        links = self._load_links()
        link = next((l for l in links if l["link_id"] == link_id), None)
        
        if not link:
            raise ValueError("Link bulunamadı")
        
        if link["user_id"] != user_id:
            raise ValueError("Bu linki iptal etme yetkiniz yok")
        
        links = [l for l in links if l["link_id"] != link_id]
        self._save_links(links)
        
        return {"message": "Link iptal edildi"}
    
    async def get_sharing_stats(self, link_id: str) -> Dict:
        """Paylaşım istatistiklerini getirir."""
        links = self._load_links()
        link = next((l for l in links if l["link_id"] == link_id), None)
        
        if not link:
            raise ValueError("Link bulunamadı")
        
        return {
            "link_id": link_id,
            "access_count": link.get("access_count", 0),
            "created_at": link.get("created_at"),
            "expires_at": link.get("expires_at")
        }
    
    def _load_links(self) -> List[Dict]:
        """Linkleri yükler."""
        try:
            with open(self.sharing_links_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_links(self, links: List[Dict]):
        """Linkleri kaydeder."""
        with open(self.sharing_links_file, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)

