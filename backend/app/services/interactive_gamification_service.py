from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class InteractiveGamificationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.choices_file = os.path.join(settings.STORAGE_PATH, "story_choices.json")
        self.scores_file = os.path.join(settings.STORAGE_PATH, "story_scores.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.choices_file, self.scores_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def add_choice_point(self, story_id: str, position: int, choices: List[Dict]) -> Dict:
        """Hikâyeye seçim noktası ekler."""
        choice_point = {
            "choice_id": str(uuid.uuid4()),
            "story_id": story_id,
            "position": position,
            "choices": choices,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.choices_file, 'r', encoding='utf-8') as f:
            all_choices = json.load(f)
        all_choices.append(choice_point)
        with open(self.choices_file, 'w', encoding='utf-8') as f:
            json.dump(all_choices, f, ensure_ascii=False, indent=2)
        
        return choice_point
    
    def record_choice(self, choice_id: str, user_id: str, selected_choice: int) -> Dict:
        """Kullanıcı seçimini kaydeder."""
        choice_record = {
            "record_id": str(uuid.uuid4()),
            "choice_id": choice_id,
            "user_id": user_id,
            "selected_choice": selected_choice,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.scores_file, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        scores.append(choice_record)
        with open(self.scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        
        return choice_record
    
    def calculate_story_score(self, story_id: str, user_id: str) -> Dict:
        """Hikâye skorunu hesaplar."""
        with open(self.scores_file, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        
        user_scores = [s for s in scores if s.get('user_id') == user_id]
        story_choices = self.get_story_choices(story_id)
        
        total_points = 0
        for choice in story_choices:
            user_choice = next((s for s in user_scores if s.get('choice_id') == choice.get('choice_id')), None)
            if user_choice:
                selected = choice.get('choices', [])[user_choice.get('selected_choice', 0)]
                total_points += selected.get('points', 0)
        
        return {
            "story_id": story_id,
            "user_id": user_id,
            "total_score": total_points,
            "max_score": sum(max((c.get('points', 0) for c in ch.get('choices', [])), default=0) for ch in story_choices),
            "completion_rate": len(user_scores) / max(len(story_choices), 1) * 100
        }
    
    def get_story_choices(self, story_id: str) -> List[Dict]:
        """Hikâyedeki seçimleri getirir."""
        with open(self.choices_file, 'r', encoding='utf-8') as f:
            all_choices = json.load(f)
        return [c for c in all_choices if c.get('story_id') == story_id]

