from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class FamilyAccountService:
    def __init__(self):
        self.families_file = os.path.join(settings.STORAGE_PATH, "family_accounts.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Aile hesapları dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.families_file):
            with open(self.families_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_family(
        self,
        parent_user_id: str,
        family_name: str
    ) -> Dict:
        """
        Yeni bir aile hesabı oluşturur.
        
        Args:
            parent_user_id: Ebeveyn kullanıcı ID'si
            family_name: Aile adı
        
        Returns:
            Aile objesi
        """
        family = {
            "family_id": str(uuid.uuid4()),
            "family_name": family_name,
            "parent_user_id": parent_user_id,
            "children": [],
            "created_at": datetime.now().isoformat()
        }
        
        self._save_family(family)
        return family
    
    def _save_family(self, family: Dict):
        """Aileyi kaydeder."""
        with open(self.families_file, 'r', encoding='utf-8') as f:
            families = json.load(f)
        
        # Mevcut aileyi güncelle veya yeni ekle
        families = [f for f in families if f.get('family_id') != family.get('family_id')]
        families.append(family)
        
        with open(self.families_file, 'w', encoding='utf-8') as f:
            json.dump(families, f, ensure_ascii=False, indent=2)
    
    def add_child_profile(
        self,
        family_id: str,
        child_name: str,
        child_age: int,
        avatar_url: Optional[str] = None
    ) -> Dict:
        """
        Aileye çocuk profili ekler.
        
        Args:
            family_id: Aile ID'si
            child_name: Çocuk adı
            child_age: Çocuk yaşı
            avatar_url: Avatar URL'i (opsiyonel)
        
        Returns:
            Çocuk profili objesi
        """
        family = self.get_family(family_id)
        if not family:
            raise ValueError("Aile bulunamadı")
        
        child_profile = {
            "child_id": str(uuid.uuid4()),
            "child_name": child_name,
            "child_age": child_age,
            "avatar_url": avatar_url,
            "created_at": datetime.now().isoformat(),
            "stories_read": [],
            "achievements": [],
            "reading_stats": {
                "total_stories": 0,
                "total_reading_time": 0,
                "favorite_themes": []
            }
        }
        
        family['children'].append(child_profile)
        self._save_family(family)
        
        return child_profile
    
    def get_family(self, family_id: str) -> Optional[Dict]:
        """Aileyi getirir."""
        with open(self.families_file, 'r', encoding='utf-8') as f:
            families = json.load(f)
        
        return next((f for f in families if f.get('family_id') == family_id), None)
    
    def get_user_families(self, user_id: str) -> List[Dict]:
        """Kullanıcının ailelerini getirir."""
        with open(self.families_file, 'r', encoding='utf-8') as f:
            families = json.load(f)
        
        return [
            f for f in families
            if f.get('parent_user_id') == user_id
        ]
    
    def get_child_profile(self, family_id: str, child_id: str) -> Optional[Dict]:
        """Çocuk profilini getirir."""
        family = self.get_family(family_id)
        if not family:
            return None
        
        return next(
            (c for c in family.get('children', []) if c.get('child_id') == child_id),
            None
        )
    
    def update_child_reading_stats(
        self,
        family_id: str,
        child_id: str,
        story_id: str,
        reading_time: float
    ):
        """
        Çocuğun okuma istatistiklerini günceller.
        """
        family = self.get_family(family_id)
        if not family:
            raise ValueError("Aile bulunamadı")
        
        child = self.get_child_profile(family_id, child_id)
        if not child:
            raise ValueError("Çocuk profili bulunamadı")
        
        # Hikâyeyi okunanlar listesine ekle
        if story_id not in child.get('stories_read', []):
            child['stories_read'].append(story_id)
        
        # İstatistikleri güncelle
        stats = child.get('reading_stats', {})
        stats['total_stories'] = len(child.get('stories_read', []))
        stats['total_reading_time'] = stats.get('total_reading_time', 0) + reading_time
        
        self._save_family(family)
    
    def get_family_dashboard(self, family_id: str) -> Dict:
        """
        Aile dashboard'unu getirir.
        """
        family = self.get_family(family_id)
        if not family:
            raise ValueError("Aile bulunamadı")
        
        children = family.get('children', [])
        
        total_stories_read = sum(
            len(c.get('stories_read', [])) for c in children
        )
        
        total_reading_time = sum(
            c.get('reading_stats', {}).get('total_reading_time', 0)
            for c in children
        )
        
        return {
            "family_id": family_id,
            "family_name": family.get('family_name'),
            "children_count": len(children),
            "total_stories_read": total_stories_read,
            "total_reading_time": round(total_reading_time, 2),
            "children": [
                {
                    "child_id": c.get('child_id'),
                    "child_name": c.get('child_name'),
                    "stories_read": len(c.get('stories_read', [])),
                    "reading_time": c.get('reading_stats', {}).get('total_reading_time', 0)
                }
                for c in children
            ]
        }
    
    def share_collection_with_family(
        self,
        family_id: str,
        collection_id: str
    ) -> Dict:
        """
        Koleksiyonu aile ile paylaşır.
        """
        family = self.get_family(family_id)
        if not family:
            raise ValueError("Aile bulunamadı")
        
        if 'shared_collections' not in family:
            family['shared_collections'] = []
        
        if collection_id not in family['shared_collections']:
            family['shared_collections'].append(collection_id)
            self._save_family(family)
        
        return {
            "message": "Koleksiyon aile ile paylaşıldı",
            "collection_id": collection_id
        }

