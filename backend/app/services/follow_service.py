import json
import os
from typing import Dict, List
from app.core.config import settings


class FollowService:
    def __init__(self):
        self.follows_file = f"{settings.STORAGE_PATH}/follows.json"
        self._ensure_follows_file()
    
    def _ensure_follows_file(self):
        """Follows dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.follows_file):
            with open(self.follows_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_follows(self) -> Dict[str, List[str]]:
        """Tüm takip ilişkilerini yükler."""
        try:
            with open(self.follows_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_follows(self, follows: Dict[str, List[str]]):
        """Takip ilişkilerini kaydeder."""
        with open(self.follows_file, 'w', encoding='utf-8') as f:
            json.dump(follows, f, ensure_ascii=False, indent=2)
    
    def follow_user(self, follower_id: str, following_id: str) -> Dict:
        """Kullanıcıyı takip eder veya takipten çıkarır."""
        if follower_id == following_id:
            raise ValueError("Kendinizi takip edemezsiniz")
        
        follows = self._load_follows()
        
        if follower_id not in follows:
            follows[follower_id] = []
        
        if following_id in follows[follower_id]:
            follows[follower_id].remove(following_id)
            is_following = False
        else:
            follows[follower_id].append(following_id)
            is_following = True
        
        self._save_follows(follows)
        
        return {
            'follower_id': follower_id,
            'following_id': following_id,
            'is_following': is_following
        }
    
    def get_followers(self, user_id: str) -> List[str]:
        """Kullanıcının takipçilerini getirir."""
        follows = self._load_follows()
        followers = []
        for follower_id, following_list in follows.items():
            if user_id in following_list:
                followers.append(follower_id)
        return followers
    
    def get_following(self, user_id: str) -> List[str]:
        """Kullanıcının takip ettiklerini getirir."""
        follows = self._load_follows()
        return follows.get(user_id, [])
    
    def is_following(self, follower_id: str, following_id: str) -> bool:
        """Takip durumunu kontrol eder."""
        follows = self._load_follows()
        return following_id in follows.get(follower_id, [])

