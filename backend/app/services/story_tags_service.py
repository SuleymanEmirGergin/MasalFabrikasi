from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StoryTagsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.tags_file = os.path.join(settings.STORAGE_PATH, "story_tags.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.tags_file):
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def add_tag(
        self,
        story_id: str,
        tag: str,
        user_id: str
    ) -> Dict:
        """Etiket ekler."""
        with open(self.tags_file, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
        
        if story_id not in tags_data:
            tags_data[story_id] = {
                "tags": [],
                "created_by": user_id
            }
        
        if tag not in tags_data[story_id]["tags"]:
            tags_data[story_id]["tags"].append(tag)
            tags_data[story_id]["updated_at"] = datetime.now().isoformat()
        
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
        
        return {"story_id": story_id, "tag": tag, "tags": tags_data[story_id]["tags"]}
    
    def remove_tag(
        self,
        story_id: str,
        tag: str
    ) -> Dict:
        """Etiketi kaldırır."""
        with open(self.tags_file, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
        
        if story_id in tags_data:
            if tag in tags_data[story_id]["tags"]:
                tags_data[story_id]["tags"].remove(tag)
                tags_data[story_id]["updated_at"] = datetime.now().isoformat()
        
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
        
        return {"story_id": story_id, "tags": tags_data.get(story_id, {}).get("tags", [])}
    
    def get_story_tags(self, story_id: str) -> List[str]:
        """Hikâye etiketlerini getirir."""
        with open(self.tags_file, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
        
        return tags_data.get(story_id, {}).get("tags", [])
    
    def get_stories_by_tag(self, tag: str) -> List[str]:
        """Etikete göre hikâyeleri getirir."""
        with open(self.tags_file, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
        
        story_ids = []
        for story_id, data in tags_data.items():
            if tag in data.get("tags", []):
                story_ids.append(story_id)
        
        return story_ids
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict]:
        """Popüler etiketleri getirir."""
        with open(self.tags_file, 'r', encoding='utf-8') as f:
            tags_data = json.load(f)
        
        tag_counts = {}
        for story_id, data in tags_data.items():
            for tag in data.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"tag": tag, "count": count} for tag, count in sorted_tags[:limit]]

