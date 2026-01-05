from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StoryBookmarksService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.bookmarks_file = os.path.join(settings.STORAGE_PATH, "story_bookmarks.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def add_bookmark(
        self,
        story_id: str,
        user_id: str,
        position: Optional[int] = None,
        note: Optional[str] = None
    ) -> Dict:
        """Yer işareti ekler."""
        bookmark = {
            "bookmark_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "position": position,
            "note": note,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        
        if user_id not in bookmarks:
            bookmarks[user_id] = []
        
        bookmarks[user_id].append(bookmark)
        
        with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, ensure_ascii=False, indent=2)
        
        return bookmark
    
    def remove_bookmark(
        self,
        bookmark_id: str,
        user_id: str
    ) -> bool:
        """Yer işaretini kaldırır."""
        with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        
        if user_id in bookmarks:
            initial_count = len(bookmarks[user_id])
            bookmarks[user_id] = [b for b in bookmarks[user_id] if b.get('bookmark_id') != bookmark_id]
            
            if len(bookmarks[user_id]) < initial_count:
                with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                    json.dump(bookmarks, f, ensure_ascii=False, indent=2)
                return True
        
        return False
    
    def get_user_bookmarks(self, user_id: str) -> List[Dict]:
        """Kullanıcı yer işaretlerini getirir."""
        with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        
        return bookmarks.get(user_id, [])
    
    def get_story_bookmarks(
        self,
        story_id: str,
        user_id: str
    ) -> List[Dict]:
        """Hikâye yer işaretlerini getirir."""
        user_bookmarks = self.get_user_bookmarks(user_id)
        return [b for b in user_bookmarks if b.get('story_id') == story_id]

