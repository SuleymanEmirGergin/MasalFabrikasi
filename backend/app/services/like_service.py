import json
import os
from typing import Dict, List
from app.core.config import settings


class LikeService:
    def __init__(self):
        self.likes_file = f"{settings.STORAGE_PATH}/likes.json"
        self._ensure_likes_file()
    
    def _ensure_likes_file(self):
        """Likes dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.likes_file):
            with open(self.likes_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_likes(self) -> Dict[str, List[str]]:
        """Tüm beğenileri yükler."""
        try:
            with open(self.likes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_likes(self, likes: Dict[str, List[str]]):
        """Beğenileri kaydeder."""
        with open(self.likes_file, 'w', encoding='utf-8') as f:
            json.dump(likes, f, ensure_ascii=False, indent=2)
    
    def like_story(self, story_id: str, user_id: str) -> Dict:
        """Hikâyeyi beğenir veya beğeniyi kaldırır."""
        likes = self._load_likes()
        
        if story_id not in likes:
            likes[story_id] = []
        
        if user_id in likes[story_id]:
            likes[story_id].remove(user_id)
            is_liked = False
        else:
            likes[story_id].append(user_id)
            is_liked = True
        
        self._save_likes(likes)
        
        return {
            'story_id': story_id,
            'like_count': len(likes[story_id]),
            'is_liked': is_liked
        }
    
    def get_story_likes(self, story_id: str) -> Dict:
        """Hikâyenin beğeni sayısını getirir."""
        likes = self._load_likes()
        story_likes = likes.get(story_id, [])
        return {
            'story_id': story_id,
            'like_count': len(story_likes),
            'user_ids': story_likes
        }
    
    def is_liked_by_user(self, story_id: str, user_id: str) -> bool:
        """Kullanıcının hikâyeyi beğenip beğenmediğini kontrol eder."""
        likes = self._load_likes()
        return user_id in likes.get(story_id, [])

