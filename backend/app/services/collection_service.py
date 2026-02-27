import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from app.core.config import settings


class CollectionService:
    def __init__(self):
        self.collections_file = f"{settings.STORAGE_PATH}/collections.json"
        self._ensure_collections_file()
    
    def _ensure_collections_file(self):
        """Collections dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.collections_file):
            with open(self.collections_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_collections(self) -> List[Dict]:
        """Tüm koleksiyonları yükler."""
        try:
            with open(self.collections_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_collections(self, collections: List[Dict]):
        """Koleksiyonları kaydeder."""
        with open(self.collections_file, 'w', encoding='utf-8') as f:
            json.dump(collections, f, ensure_ascii=False, indent=2)
    
    def create_collection(self, name: str, description: str = "") -> Dict:
        """Yeni bir koleksiyon oluşturur."""
        collections = self._load_collections()
        
        collection_id = f"collection_{len(collections) + 1}_{datetime.now().timestamp()}"
        collection = {
            'collection_id': collection_id,
            'name': name,
            'description': description,
            'story_ids': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        collections.append(collection)
        self._save_collections(collections)
        return collection
    
    def get_all_collections(self) -> List[Dict]:
        """Tüm koleksiyonları getirir."""
        return self._load_collections()
    
    def get_collection(self, collection_id: str) -> Optional[Dict]:
        """Belirli bir koleksiyonu getirir."""
        collections = self._load_collections()
        return next((c for c in collections if c.get('collection_id') == collection_id), None)
    
    def update_collection(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Dict]:
        """Koleksiyonu günceller."""
        collections = self._load_collections()
        collection = next((c for c in collections if c.get('collection_id') == collection_id), None)
        
        if not collection:
            return None
        
        if name is not None:
            collection['name'] = name
        if description is not None:
            collection['description'] = description
        
        collection['updated_at'] = datetime.now().isoformat()
        self._save_collections(collections)
        return collection
    
    def delete_collection(self, collection_id: str) -> bool:
        """Bir koleksiyonu siler."""
        collections = self._load_collections()
        initial_count = len(collections)
        collections = [c for c in collections if c.get('collection_id') != collection_id]
        
        if len(collections) < initial_count:
            self._save_collections(collections)
            return True
        
        return False
    
    def add_story_to_collection(self, collection_id: str, story_id: str) -> Optional[Dict]:
        """Koleksiyona hikâye ekler."""
        collections = self._load_collections()
        collection = next((c for c in collections if c.get('collection_id') == collection_id), None)
        
        if not collection:
            return None
        
        if story_id not in collection.get('story_ids', []):
            collection['story_ids'].append(story_id)
            collection['updated_at'] = datetime.now().isoformat()
            self._save_collections(collections)
        
        return collection
    
    def remove_story_from_collection(self, collection_id: str, story_id: str) -> Optional[Dict]:
        """Koleksiyondan hikâye çıkarır."""
        collections = self._load_collections()
        collection = next((c for c in collections if c.get('collection_id') == collection_id), None)
        
        if not collection:
            return None
        
        if story_id in collection.get('story_ids', []):
            collection['story_ids'].remove(story_id)
            collection['updated_at'] = datetime.now().isoformat()
            self._save_collections(collections)
        
        return collection
    
    def get_collection_stories(self, collection_id: str, story_storage) -> List[Dict]:
        """Koleksiyondaki hikâyeleri getirir."""
        collection = self.get_collection(collection_id)
        if not collection:
            return []
        
        story_ids = collection.get('story_ids', [])
        stories = []
        for story_id in story_ids:
            story = story_storage.get_story(story_id)
            if story:
                stories.append(story)
        
        return stories

