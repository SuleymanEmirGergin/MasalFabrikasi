from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryGamificationBadgesService:
    """Hikaye oyunlaştırma ve rozetler servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.badges_file = os.path.join(settings.STORAGE_PATH, "user_badges.json")
        self.achievements_file = os.path.join(settings.STORAGE_PATH, "achievements.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.badges_file):
            with open(self.badges_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.achievements_file):
            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def check_and_award_badge(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict
    ) -> Dict:
        """Rozet kontrolü ve ödül verme."""
        badges = self._load_badges()
        
        if user_id not in badges:
            badges[user_id] = []
        
        # Rozet kriterlerini kontrol et
        earned_badges = self._check_badge_criteria(user_id, action_type, action_data, badges[user_id])
        
        if earned_badges:
            badges[user_id].extend(earned_badges)
            self._save_badges(badges)
            
            return {
                "badges_earned": earned_badges,
                "message": f"{len(earned_badges)} yeni rozet kazandınız!"
            }
        
        return {"badges_earned": [], "message": "Henüz yeni rozet yok"}
    
    def _check_badge_criteria(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict,
        existing_badges: List[Dict]
    ) -> List[Dict]:
        """Rozet kriterlerini kontrol eder."""
        earned = []
        existing_badge_ids = [b["badge_id"] for b in existing_badges]
        
        # İlk hikaye rozeti
        if action_type == "story_created" and "first_story" not in existing_badge_ids:
            earned.append({
                "badge_id": "first_story",
                "name": "İlk Hikaye",
                "description": "İlk hikayenizi oluşturdunuz",
                "icon": "📖",
                "earned_at": datetime.now().isoformat()
            })
        
        # 10 hikaye rozeti
        if action_type == "story_created":
            story_count = action_data.get("total_stories", 0)
            if story_count >= 10 and "story_master_10" not in existing_badge_ids:
                earned.append({
                    "badge_id": "story_master_10",
                    "name": "Hikaye Ustası",
                    "description": "10 hikaye oluşturdunuz",
                    "icon": "⭐",
                    "earned_at": datetime.now().isoformat()
                })
        
        # Paylaşım rozeti
        if action_type == "story_shared" and "sharer" not in existing_badge_ids:
            earned.append({
                "badge_id": "sharer",
                "name": "Paylaşımcı",
                "description": "İlk hikayenizi paylaştınız",
                "icon": "📤",
                "earned_at": datetime.now().isoformat()
            })
        
        # Yorum rozeti
        if action_type == "comment_added" and "commentator" not in existing_badge_ids:
            earned.append({
                "badge_id": "commentator",
                "name": "Yorumcu",
                "description": "İlk yorumunuzu yaptınız",
                "icon": "💬",
                "earned_at": datetime.now().isoformat()
            })
        
        return earned
    
    async def get_user_badges(
        self,
        user_id: str
    ) -> Dict:
        """Kullanıcının rozetlerini getirir."""
        badges = self._load_badges()
        user_badges = badges.get(user_id, [])
        
        # Rozet kategorilerine göre grupla
        categories = {
            "creation": [b for b in user_badges if "story" in b.get("badge_id", "")],
            "social": [b for b in user_badges if b.get("badge_id") in ["sharer", "commentator"]],
            "achievement": [b for b in user_badges if "master" in b.get("badge_id", "")]
        }
        
        return {
            "user_id": user_id,
            "total_badges": len(user_badges),
            "badges": user_badges,
            "categories": categories
        }
    
    async def create_custom_badge(
        self,
        badge_name: str,
        description: str,
        criteria: Dict,
        icon: str = "🏆"
    ) -> Dict:
        """Özel rozet oluşturur."""
        badge_id = str(uuid.uuid4())
        
        badge = {
            "badge_id": badge_id,
            "name": badge_name,
            "description": description,
            "icon": icon,
            "criteria": criteria,
            "created_at": datetime.now().isoformat()
        }
        
        achievements = self._load_achievements()
        achievements.append(badge)
        self._save_achievements(achievements)
        
        return {
            "badge_id": badge_id,
            "message": "Özel rozet oluşturuldu"
        }
    
    def _load_badges(self) -> Dict:
        """Rozetleri yükler."""
        try:
            with open(self.badges_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_badges(self, badges: Dict):
        """Rozetleri kaydeder."""
        with open(self.badges_file, 'w', encoding='utf-8') as f:
            json.dump(badges, f, ensure_ascii=False, indent=2)
    
    def _load_achievements(self) -> List[Dict]:
        """Başarımları yükler."""
        try:
            with open(self.achievements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_achievements(self, achievements: List[Dict]):
        """Başarımları kaydeder."""
        with open(self.achievements_file, 'w', encoding='utf-8') as f:
            json.dump(achievements, f, ensure_ascii=False, indent=2)

