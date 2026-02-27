from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage


class ReadingGoalsService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.goals_file = os.path.join(settings.STORAGE_PATH, "reading_goals.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.goals_file):
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_reading_goal(self, user_id: str, goal_type: str, target: int, period: str = "weekly") -> Dict:
        goal = {
            "goal_id": str(uuid.uuid4()),
            "user_id": user_id,
            "goal_type": goal_type,
            "target": target,
            "current": 0,
            "period": period,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7 if period == "weekly" else 30)).isoformat(),
            "status": "active"
        }
        
        with open(self.goals_file, 'r', encoding='utf-8') as f:
            goals = json.load(f)
        if user_id not in goals:
            goals[user_id] = []
        goals[user_id].append(goal)
        with open(self.goals_file, 'w', encoding='utf-8') as f:
            json.dump(goals, f, ensure_ascii=False, indent=2)
        
        return goal
    
    def update_goal_progress(self, user_id: str, goal_id: str, progress: int) -> Dict:
        with open(self.goals_file, 'r', encoding='utf-8') as f:
            goals = json.load(f)
        
        user_goals = goals.get(user_id, [])
        goal = next((g for g in user_goals if g.get('goal_id') == goal_id), None)
        if not goal:
            raise ValueError("Hedef bulunamadı")
        
        goal['current'] = progress
        if goal['current'] >= goal['target']:
            goal['status'] = 'completed'
        
        with open(self.goals_file, 'w', encoding='utf-8') as f:
            json.dump(goals, f, ensure_ascii=False, indent=2)
        
        return goal
    
    def get_user_goals(self, user_id: str) -> List[Dict]:
        with open(self.goals_file, 'r', encoding='utf-8') as f:
            goals = json.load(f)
        return goals.get(user_id, [])

