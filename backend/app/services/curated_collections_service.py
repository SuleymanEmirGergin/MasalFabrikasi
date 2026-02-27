from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class CuratedCollectionsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.collections_file = os.path.join(settings.STORAGE_PATH, "curated_collections.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.collections_file):
            with open(self.collections_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_curated_collection(self, title: str, description: str, curator_id: str, is_featured: bool = False) -> Dict:
        collection = {
            "collection_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "curator_id": curator_id,
            "stories": [],
            "is_featured": is_featured,
            "created_at": datetime.now().isoformat()
        }
        self._save_collection(collection)
        return collection
    
    def _save_collection(self, collection: Dict):
        with open(self.collections_file, 'r', encoding='utf-8') as f:
            collections = json.load(f)
        collections = [c for c in collections if c.get('collection_id') != collection.get('collection_id')]
        collections.append(collection)
        with open(self.collections_file, 'w', encoding='utf-8') as f:
            json.dump(collections, f, ensure_ascii=False, indent=2)
    
    def add_story_to_collection(self, collection_id: str, story_id: str) -> Dict:
        collection = self.get_collection(collection_id)
        if not collection:
            raise ValueError("Koleksiyon bulunamadı")
        if story_id not in collection.get('stories', []):
            collection['stories'].append(story_id)
            self._save_collection(collection)
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[Dict]:
        with open(self.collections_file, 'r', encoding='utf-8') as f:
            collections = json.load(f)
        return next((c for c in collections if c.get('collection_id') == collection_id), None)
    
    def get_featured_collections(self, limit: int = 10) -> List[Dict]:
        with open(self.collections_file, 'r', encoding='utf-8') as f:
            collections = json.load(f)
        featured = [c for c in collections if c.get('is_featured', False)]
        return sorted(featured, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]

