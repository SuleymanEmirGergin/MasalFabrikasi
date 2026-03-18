from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.achievement_service import AchievementService


class AIGamificationAdvancedService:
    def __init__(self):
        self.achievement_service = AchievementService()
        self.dynamic_badges_file = os.path.join(settings.STORAGE_PATH, "dynamic_badges.json")
        self.levels_file = os.path.join(settings.STORAGE_PATH, "dynamic_levels.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.dynamic_badges_file, self.levels_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_dynamic_badge(
        self,
        badge_name: str,
        description: str,
        criteria: Dict,
        icon_url: Optional[str] = None
    ) -> Dict:
        """Dinamik rozet oluşturur."""
        badge = {
            "badge_id": str(uuid.uuid4()),
            "badge_name": badge_name,
            "description": description,
            "criteria": criteria,
            "icon_url": icon_url,
            "created_at": datetime.now().isoformat(),
            "earned_by": []
        }
        
        with open(self.dynamic_badges_file, 'r', encoding='utf-8') as f:
            badges = json.load(f)
        badges[badge['badge_id']] = badge
        with open(self.dynamic_badges_file, 'w', encoding='utf-8') as f:
            json.dump(badges, f, ensure_ascii=False, indent=2)
        
        return badge
    
    def check_and_award_badge(self, user_id: str, badge_id: str, user_stats: Dict) -> Optional[Dict]:
        """Rozet kriterlerini kontrol eder ve ödül verir."""
        with open(self.dynamic_badges_file, 'r', encoding='utf-8') as f:
            badges = json.load(f)
        
        badge = badges.get(badge_id)
        if not badge:
            return None
        
        criteria = badge.get('criteria', {})
        
        # Kriterleri kontrol et
        meets_criteria = True
        for key, value in criteria.items():
            if user_stats.get(key, 0) < value:
                meets_criteria = False
                break
        
        if meets_criteria and user_id not in badge.get('earned_by', []):
            badge['earned_by'].append({
                "user_id": user_id,
                "earned_at": datetime.now().isoformat()
            })
            
            with open(self.dynamic_badges_file, 'w', encoding='utf-8') as f:
                json.dump(badges, f, ensure_ascii=False, indent=2)
            
            return badge
        
        return None
    
    def create_dynamic_level_system(
        self,
        level_name: str,
        xp_requirements: List[int],
        rewards: List[Dict]
    ) -> Dict:
        """Dinamik seviye sistemi oluşturur."""
        level_system = {
            "system_id": str(uuid.uuid4()),
            "level_name": level_name,
            "xp_requirements": xp_requirements,
            "rewards": rewards,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.levels_file, 'r', encoding='utf-8') as f:
            systems = json.load(f)
        systems[level_system['system_id']] = level_system
        with open(self.levels_file, 'w', encoding='utf-8') as f:
            json.dump(systems, f, ensure_ascii=False, indent=2)
        
        return level_system
    
    def calculate_user_level(self, user_id: str, system_id: str, user_xp: int) -> Dict:
        """Kullanıcı seviyesini hesaplar."""
        with open(self.levels_file, 'r', encoding='utf-8') as f:
            systems = json.load(f)
        
        system = systems.get(system_id)
        if not system:
            return {"level": 1, "xp": user_xp, "next_level_xp": 100}
        
        xp_requirements = system.get('xp_requirements', [])
        current_level = 1
        
        for i, xp_req in enumerate(xp_requirements):
            if user_xp >= xp_req:
                current_level = i + 2
            else:
                break
        
        next_level_xp = xp_requirements[current_level - 1] if current_level <= len(xp_requirements) else user_xp + 100
        
        return {
            "level": current_level,
            "xp": user_xp,
            "next_level_xp": next_level_xp,
            "progress": (user_xp / next_level_xp * 100) if next_level_xp > 0 else 0
        }

