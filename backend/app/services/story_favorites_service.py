from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class StoryFavoritesService:
    """Hikaye favorileri ve koleksiyonlar servisi"""
    
    def __init__(self):
        self.favorites_file = os.path.join(settings.STORAGE_PATH, "story_favorites.json")
        self.collections_file = os.path.join(settings.STORAGE_PATH, "story_collections.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.favorites_file):
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.collections_file):
            with open(self.collections_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def add_to_favorites(
        self,
        story_id: str,
        user_id: str,
        category: Optional[str] = None
    ) -> Dict:
        """Hikayeyi favorilere ekler."""
        favorites = self._load_favorites()
        
        if user_id not in favorites:
            favorites[user_id] = []
        
        # Zaten favorilerde mi kontrol et
        if any(f["story_id"] == story_id for f in favorites[user_id]):
            return {"message": "Hikaye zaten favorilerde"}
        
        favorite = {
            "story_id": story_id,
            "category": category,
            "added_at": datetime.now().isoformat()
        }
        
        favorites[user_id].append(favorite)
        self._save_favorites(favorites)
        
        return {
            "message": "Favorilere eklendi",
            "total_favorites": len(favorites[user_id])
        }
    
    async def remove_from_favorites(
        self,
        story_id: str,
        user_id: str
    ) -> Dict:
        """Hikayeyi favorilerden çıkarır."""
        favorites = self._load_favorites()
        
        if user_id not in favorites:
            return {"message": "Favori bulunamadı"}
        
        favorites[user_id] = [f for f in favorites[user_id] if f["story_id"] != story_id]
        self._save_favorites(favorites)
        
        return {
            "message": "Favorilerden çıkarıldı",
            "total_favorites": len(favorites.get(user_id, []))
        }
    
    async def get_user_favorites(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Kullanıcının favorilerini getirir."""
        favorites = self._load_favorites()
        user_favorites = favorites.get(user_id, [])
        
        if category:
            user_favorites = [f for f in user_favorites if f.get("category") == category]
        
        # Tarihe göre sırala
        user_favorites.sort(key=lambda x: x.get("added_at", ""), reverse=True)
        
        return user_favorites
    
    async def create_collection(
        self,
        user_id: str,
        collection_name: str,
        description: Optional[str] = None,
        is_public: bool = False
    ) -> Dict:
        """Yeni koleksiyon oluşturur."""
        collections = self._load_collections()
        
        collection = {
            "collection_id": str(uuid.uuid4()),
            "user_id": user_id,
            "name": collection_name,
            "description": description,
            "is_public": is_public,
            "stories": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        collections.append(collection)
        self._save_collections(collections)
        
        return {
            "collection_id": collection["collection_id"],
            "message": "Koleksiyon oluşturuldu"
        }
    
    async def add_story_to_collection(
        self,
        collection_id: str,
        story_id: str,
        user_id: str
    ) -> Dict:
        """Hikayeyi koleksiyona ekler."""
        collections = self._load_collections()
        collection = next((c for c in collections if c["collection_id"] == collection_id), None)
        
        if not collection:
            raise ValueError("Koleksiyon bulunamadı")
        
        if collection["user_id"] != user_id:
            raise ValueError("Bu koleksiyonu düzenleme yetkiniz yok")
        
        if story_id not in collection["stories"]:
            collection["stories"].append(story_id)
            collection["updated_at"] = datetime.now().isoformat()
            self._save_collections(collections)
            return {"message": "Hikaye koleksiyona eklendi"}
        else:
            return {"message": "Hikaye zaten koleksiyonda"}
    
    async def get_user_collections(
        self,
        user_id: str,
        include_public: bool = True
    ) -> List[Dict]:
        """Kullanıcının koleksiyonlarını getirir."""
        collections = self._load_collections()
        user_collections = [
            c for c in collections
            if c["user_id"] == user_id or (include_public and c.get("is_public", False))
        ]
        
        return user_collections
    
    def _load_favorites(self) -> Dict:
        """Favorileri yükler."""
        try:
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_favorites(self, favorites: Dict):
        """Favorileri kaydeder."""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
    
    def _load_collections(self) -> List[Dict]:
        """Koleksiyonları yükler."""
        try:
            with open(self.collections_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_collections(self, collections: List[Dict]):
        """Koleksiyonları kaydeder."""
        with open(self.collections_file, 'w', encoding='utf-8') as f:
            json.dump(collections, f, ensure_ascii=False, indent=2)

