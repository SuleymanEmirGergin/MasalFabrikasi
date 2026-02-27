import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from app.core.config import settings


class CommentService:
    def __init__(self):
        self.comments_file = f"{settings.STORAGE_PATH}/comments.json"
        self._ensure_comments_file()
    
    def _ensure_comments_file(self):
        """Comments dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.comments_file):
            with open(self.comments_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_comments(self) -> List[Dict]:
        """Tüm yorumları yükler."""
        try:
            with open(self.comments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_comments(self, comments: List[Dict]):
        """Yorumları kaydeder."""
        with open(self.comments_file, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
    
    def add_comment(self, story_id: str, user_id: str, text: str) -> Dict:
        """Yeni yorum ekler."""
        comments = self._load_comments()
        
        comment = {
            'comment_id': str(uuid.uuid4()),
            'story_id': story_id,
            'user_id': user_id,
            'text': text,
            'likes': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        comments.append(comment)
        self._save_comments(comments)
        
        return comment
    
    def get_story_comments(self, story_id: str) -> List[Dict]:
        """Bir hikâyenin yorumlarını getirir."""
        comments = self._load_comments()
        story_comments = [c for c in comments if c.get('story_id') == story_id]
        # En yeni önce
        story_comments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return story_comments
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Yorumu siler (sadece yazar silebilir)."""
        comments = self._load_comments()
        comment = next((c for c in comments if c.get('comment_id') == comment_id), None)
        
        if not comment:
            return False
        
        if comment.get('user_id') != user_id:
            return False  # Yetki yok
        
        comments = [c for c in comments if c.get('comment_id') != comment_id]
        self._save_comments(comments)
        return True
    
    def like_comment(self, comment_id: str, user_id: str) -> Dict:
        """Yorumu beğenir veya beğeniyi kaldırır."""
        comments = self._load_comments()
        comment = next((c for c in comments if c.get('comment_id') == comment_id), None)
        
        if not comment:
            raise ValueError("Yorum bulunamadı")
        
        likes = comment.get('likes', [])
        if user_id in likes:
            likes.remove(user_id)
            is_liked = False
        else:
            likes.append(user_id)
            is_liked = True
        
        comment['likes'] = likes
        comment['updated_at'] = datetime.now().isoformat()
        
        self._save_comments(comments)
        
        return {
            'comment_id': comment_id,
            'likes': likes,
            'like_count': len(likes),
            'is_liked': is_liked
        }

