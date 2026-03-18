from sqlalchemy.orm import Session
from app.models import UserAchievement, UserProfile
from typing import List, Dict, Optional
import os
import json
import uuid

class AchievementService:
    def __init__(self):
        self.achievements_file = os.path.join(os.path.dirname(__file__), '../data/achievements.json')
        self._achievements = self._load_achievements()

    def _load_achievements(self) -> List[Dict]:
        """Başarı tanımlarını yükler."""
        try:
            if os.path.exists(self.achievements_file):
                with open(self.achievements_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return [
                {"id": "first_story", "title": "İlk Masal", "description": "İlk masalını oluştur.", "xp_reward": 50},
                {"id": "story_master", "title": "Masal Ustası", "description": "10 masal oluştur.", "xp_reward": 500},
                {"id": "favorite_collector", "title": "Koleksiyoner", "description": "5 masalı favoriye ekle.", "xp_reward": 100},
                {"id": "character_creator", "title": "Yaratıcı", "description": "İlk karakterini oluştur.", "xp_reward": 50},
                {"id": "social_butterfly", "title": "Sosyal Kelebek", "description": "10 yorum yap.", "xp_reward": 200},
            ]
        except Exception:
             return []

    def get_user_achievements(self, db: Session, user_id: str) -> List[Dict]:
        """Kullanıcının başarılarını getirir (kazanılanlar işaretlenmiş olarak)."""
        unlocked = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
        unlocked_ids = {a.achievement_id for a in unlocked}
        
        result = []
        for achievement in self._achievements:
            achievement_copy = achievement.copy()
            achievement_copy['unlocked'] = achievement['id'] in unlocked_ids
            result.append(achievement_copy)
        
        return result

    def unlock_achievement(self, db: Session, user_id: str, achievement_id: str) -> Optional[Dict]:
        """Başarıyı veritabanına kaydeder ve XP verir."""
        # Check definitions
        achievement_def = next((a for a in self._achievements if a['id'] == achievement_id), None)
        if not achievement_def:
            return None
            
        # Check if already unlocked
        exists = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id
        ).first()
        
        if exists:
            return None # Already unlocked

        # Unlock
        new_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id
        )
        db.add(new_achievement)
        
        # Add XP
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if user:
            user.xp += achievement_def.get('xp_reward', 0)
            
        db.commit()
        db.refresh(new_achievement)
        return achievement_def

    def check_achievements(self, db: Session, user_id: str, action: str, count: int = 1) -> List[Dict]:
        """Kullanıcı eylemlerine göre başarıları kontrol eder."""
        unlocked = []
        
        # İlk hikâye
        if action == "story_created":
            if count >= 1:
                ach = self.unlock_achievement(db, user_id, "first_story")
                if ach: unlocked.append(ach)
            if count >= 10:
                ach = self.unlock_achievement(db, user_id, "story_master")
                if ach: unlocked.append(ach)

        # 5 favori
        if action == "favorite_added" and count >= 5:
            ach = self.unlock_achievement(db, user_id, "favorite_collector")
            if ach: unlocked.append(ach)
        
        # İlk karakter
        if action == "character_created" and count >= 1:
            ach = self.unlock_achievement(db, user_id, "character_creator")
            if ach: unlocked.append(ach)
            
        return unlocked

achievement_service = AchievementService()
