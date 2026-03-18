from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class StoryHighlightsService:
    def __init__(self):
        self.highlights_file = os.path.join(settings.STORAGE_PATH, "story_highlights.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.highlights_file):
            with open(self.highlights_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def add_highlight(
        self,
        story_id: str,
        user_id: str,
        text: str,
        start_position: int,
        end_position: int,
        color: str = "yellow"
    ) -> Dict:
        """Vurgulama ekler."""
        highlight = {
            "highlight_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "text": text,
            "start_position": start_position,
            "end_position": end_position,
            "color": color,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.highlights_file, 'r', encoding='utf-8') as f:
            highlights = json.load(f)
        
        if user_id not in highlights:
            highlights[user_id] = {}
        
        if story_id not in highlights[user_id]:
            highlights[user_id][story_id] = []
        
        highlights[user_id][story_id].append(highlight)
        
        with open(self.highlights_file, 'w', encoding='utf-8') as f:
            json.dump(highlights, f, ensure_ascii=False, indent=2)
        
        return highlight
    
    def remove_highlight(
        self,
        highlight_id: str,
        user_id: str,
        story_id: str
    ) -> bool:
        """Vurgulamayı kaldırır."""
        with open(self.highlights_file, 'r', encoding='utf-8') as f:
            highlights = json.load(f)
        
        if user_id in highlights and story_id in highlights[user_id]:
            initial_count = len(highlights[user_id][story_id])
            highlights[user_id][story_id] = [
                h for h in highlights[user_id][story_id]
                if h.get('highlight_id') != highlight_id
            ]
            
            if len(highlights[user_id][story_id]) < initial_count:
                with open(self.highlights_file, 'w', encoding='utf-8') as f:
                    json.dump(highlights, f, ensure_ascii=False, indent=2)
                return True
        
        return False
    
    def get_story_highlights(
        self,
        story_id: str,
        user_id: str
    ) -> List[Dict]:
        """Hikâye vurgulamalarını getirir."""
        with open(self.highlights_file, 'r', encoding='utf-8') as f:
            highlights = json.load(f)
        
        if user_id in highlights and story_id in highlights[user_id]:
            return highlights[user_id][story_id]
        
        return []

