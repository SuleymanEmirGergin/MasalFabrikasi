from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class CollaborationAdvancedService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.collaborations_file = os.path.join(settings.STORAGE_PATH, "collaborations_advanced.json")
        self.comments_file = os.path.join(settings.STORAGE_PATH, "collaboration_comments.json")
        self.changes_file = os.path.join(settings.STORAGE_PATH, "collaboration_changes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.collaborations_file, self.comments_file, self.changes_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def start_collaboration(
        self,
        story_id: str,
        creator_id: str,
        collaborators: List[str],
        permissions: Dict[str, List[str]]
    ) -> Dict:
        """İşbirliği başlatır."""
        collaboration = {
            "collaboration_id": str(uuid.uuid4()),
            "story_id": story_id,
            "creator_id": creator_id,
            "collaborators": collaborators,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        with open(self.collaborations_file, 'r', encoding='utf-8') as f:
            collaborations = json.load(f)
        if story_id not in collaborations:
            collaborations[story_id] = []
        collaborations[story_id].append(collaboration)
        with open(self.collaborations_file, 'w', encoding='utf-8') as f:
            json.dump(collaborations, f, ensure_ascii=False, indent=2)
        
        return collaboration
    
    def add_comment(
        self,
        story_id: str,
        user_id: str,
        text: str,
        position: Optional[Dict] = None
    ) -> Dict:
        """Yorum ekler."""
        comment = {
            "comment_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "text": text,
            "position": position,
            "created_at": datetime.now().isoformat(),
            "replies": []
        }
        
        with open(self.comments_file, 'r', encoding='utf-8') as f:
            comments = json.load(f)
        if story_id not in comments:
            comments[story_id] = []
        comments[story_id].append(comment)
        with open(self.comments_file, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        
        return comment
    
    def track_change(
        self,
        story_id: str,
        user_id: str,
        change_type: str,
        old_value: str,
        new_value: str,
        position: Optional[Dict] = None
    ) -> Dict:
        """Değişikliği takip eder."""
        change = {
            "change_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "change_type": change_type,
            "old_value": old_value,
            "new_value": new_value,
            "position": position,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.changes_file, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        if story_id not in changes:
            changes[story_id] = []
        changes[story_id].append(change)
        with open(self.changes_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, ensure_ascii=False, indent=2)
        
        return change
    
    def get_change_history(
        self,
        story_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """Değişiklik geçmişini getirir."""
        with open(self.changes_file, 'r', encoding='utf-8') as f:
            changes = json.load(f)
        
        story_changes = changes.get(story_id, [])
        return story_changes[-limit:]
    
    def set_user_role(
        self,
        story_id: str,
        user_id: str,
        role: str
    ) -> Dict:
        """Kullanıcı rolünü ayarlar."""
        with open(self.collaborations_file, 'r', encoding='utf-8') as f:
            collaborations = json.load(f)
        
        story_collaborations = collaborations.get(story_id, [])
        collaboration = story_collaborations[0] if story_collaborations else None
        
        if not collaboration:
            raise ValueError("İşbirliği bulunamadı")
        
        if 'roles' not in collaboration:
            collaboration['roles'] = {}
        
        collaboration['roles'][user_id] = role
        collaboration['updated_at'] = datetime.now().isoformat()
        
        with open(self.collaborations_file, 'w', encoding='utf-8') as f:
            json.dump(collaborations, f, ensure_ascii=False, indent=2)
        
        return {"user_id": user_id, "role": role}

