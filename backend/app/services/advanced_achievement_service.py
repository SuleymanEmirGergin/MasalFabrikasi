"""
Advanced Achievement Service - Genişletilmiş rozet ve başarı sistemi
Maliyet yok, sadece DB tabanlı takip
"""
from sqlalchemy.orm import Session
from typing import Dict, List
import uuid
from datetime import datetime
from app.models import UserProfile, UserAchievement, Story


class AdvancedAchievementService:
    """Genişletilmiş başarı ve rozet sistemi"""
    
    # Tüm başarı tanımları
    ACHIEVEMENTS = {
        # Okuma Milestone'ları
        "first_story": {
            "name": "İlk Adım",
            "description": "İlk hikayeni oluşturdun!",
            "icon": "🎯",
            "xp_reward": 10,
            "condition": "story_count >= 1"
        },
        "10_stories": {
            "name": "Hikaye Avcısı",
            "description": "10 hikaye oluşturdun!",
            "icon": "📚",
            "xp_reward": 50,
            "condition": "story_count >= 10"
        },
        "50_stories": {
            "name": "Hikaye Ustası",
            "description": "50 hikaye tamamladın!",
            "icon": "🏆",
            "xp_reward": 200,
            "condition": "story_count >= 50"
        },
        "100_stories": {
            "name": "Efsane Yazar",
            "description": "100 hikaye oluşturdun!",
            "icon": "👑",
            "xp_reward": 500,
            "condition": "story_count >= 100"
        },
        
        # Streak Başarıları
        "streak_3": {
            "name": "Hızlı Başlangıç",
            "description": "3 gün üst üste oku",
            "icon": "🔥",
            "xp_reward": 30,
            "condition": "current_streak >= 3"
        },
        "streak_7": {
            "name": "Bir Hafta Şampiyon",
            "description": "7 gün üst üste oku",
            "icon": "⭐",
            "xp_reward": 100,
            "condition": "current_streak >= 7"
        },
        "streak_30": {
            "name": "Aylık Kahraman",
            "description": "30 gün kesintisiz okuma!",
            "icon": "🎖️",
            "xp_reward": 500,
            "condition": "current_streak >= 30"
        },
        
        # Koleksiyon Başarıları
        "all_types": {
            "name": "Tür Gezgini",
            "description": "Her türden hikaye oluştur",
            "icon": "🌍",
            "xp_reward": 150,
            "condition": "unique_types >= 5"
        },
        "multilingual": {
            "name": "Çok Dilli",
            "description": "Farklı dillerde hikayeler oluştur",
            "icon": "🌐",
            "xp_reward": 100,
            "condition": "unique_languages >= 2"
        },
        
        # Favoriler
        "collector": {
            "name": "Koleksiyoncu",
            "description": "10 hikayeyi favorilere ekle",
            "icon": "❤️",
            "xp_reward": 50,
            "condition": "favorite_count >= 10"
        },
        
        # Zaman Bazlı
        "night_owl": {
            "name": "Gece Kuşu",
            "description": "Gece yarısından sonra 5 hikaye oku",
            "icon": "🦉",
            "xp_reward": 75,
            "condition": "night_stories >= 5"
        },
        "early_bird": {
            "name": "Erken Kuş",
            "description": "Sabah 6'dan önce 5 hikaye oku",
            "icon": "🌅",
            "xp_reward": 75,
            "condition": "early_stories >= 5"
        },
        
        # Sosyal
        "sharer": {
            "name": "Paylaşımcı",
            "description": "5 hikayeyi paylaş",
            "icon": "📤",
            "xp_reward": 50,
            "condition": "shared_stories >= 5"
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_unlock_achievements(self, user_id: uuid.UUID) -> List[Dict]:
        """
        Kullanıcının başarılarını kontrol eder ve yeni kazanılanları unlock eder
        
        Returns:
            Yeni kazanılan başarıların listesi
        """
        # Kullanıcı verilerini çek
        user_data = self._get_user_achievement_data(user_id)
        
        # Daha önce kazanılmış başarılar
        existing_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        existing_ids = {ach.achievement_id for ach in existing_achievements}
        newly_unlocked = []
        
        # Her başarıyı kontrol et
        for achievement_id, achievement_def in self.ACHIEVEMENTS.items():
            if achievement_id in existing_ids:
                continue  # Zaten kazanılmış
            
            # Koşul kontrolü
            if self._check_condition(achievement_def["condition"], user_data):
                # Başarıyı ekle
                new_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement_id,
                    unlocked_at=datetime.now()
                )
                self.db.add(new_achievement)
                
                # XP ekle
                user_profile = self.db.query(UserProfile).filter(
                    UserProfile.id == user_id
                ).first()
                
                if user_profile:
                    user_profile.xp += achievement_def["xp_reward"]
                
                newly_unlocked.append({
                    **achievement_def,
                    "id": achievement_id,
                    "unlocked_at": datetime.now().isoformat()
                })
        
        if newly_unlocked:
            self.db.commit()
        
        return newly_unlocked
    
    def _get_user_achievement_data(self, user_id: uuid.UUID) -> Dict:
        """Başarı kontrolü için gerekli kullanıcı verilerini toplar"""
        from app.services.reading_analytics_service import ReadingAnalyticsService
        
        analytics = ReadingAnalyticsService(self.db)
        stats = analytics.get_reading_stats(user_id)
        distribution = analytics.get_reading_distribution(user_id)
        
        # Gece/sabah hikaye sayısı hesapla
        stories = self.db.query(Story).filter(Story.user_id == user_id).all()
        night_stories = sum(1 for s in stories if s.created_at.hour >= 0 and s.created_at.hour < 6)
        early_stories = sum(1 for s in stories if s.created_at.hour >= 4 and s.created_at.hour < 6)
        
        return {
            "story_count": stats["total_stories_read"],
            "current_streak": stats["current_streak_days"],
            "favorite_count": stats["favorite_count"],
            "unique_types": len(distribution["by_type"]),
            "unique_languages": len(distribution["by_language"]),
            "night_stories": night_stories,
            "early_stories": early_stories,
            "shared_stories": 0  # TODO: Implement share tracking
        }
    
    def _check_condition(self, condition: str, data: Dict) -> bool:
        """
        Başarı koşulunu kontrol eder
        
        Args:
            condition: "story_count >= 10" gibi string koşul
            data: Kullanıcı verileri dict
        
        Returns:
            Koşul sağlanıyorsa True
        """
        try:
            # Simple eval-based condition check
            # Convert condition to Python expression
            for key, value in data.items():
                condition = condition.replace(key, str(value))
            
            return eval(condition)
        except:
            return False
    
    def get_all_achievements(self) -> List[Dict]:
        """Tüm mevcut başarıları getirir"""
        return [
            {
                "id": achievement_id,
                **achievement_def
            }
            for achievement_id, achievement_def in self.ACHIEVEMENTS.items()
        ]
    
    def get_user_achievements(self, user_id: uuid.UUID) -> Dict:
        """
        Kullanıcının başarılarını getirir
        
        Returns:
            - unlocked: Kazanılmış başarılar
            - locked: Henüz kazanılmamış
            - progress: İlerleme yüzdeleri
        """
        unlocked_achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        unlocked_ids = {ach.achievement_id for ach in unlocked_achievements}
        
        unlocked = []
        locked = []
        
        for achievement_id, achievement_def in self.ACHIEVEMENTS.items():
            achievement_data = {
                "id": achievement_id,
                **achievement_def
            }
            
            if achievement_id in unlocked_ids:
                # Unlock zamanını ekle
                unlock_time = next(
                    (ach.unlocked_at for ach in unlocked_achievements if ach.achievement_id == achievement_id),
                    None
                )
                achievement_data["unlocked_at"] = unlock_time.isoformat() if unlock_time else None
                unlocked.append(achievement_data)
            else:
                locked.append(achievement_data)
        
        return {
            "unlocked": unlocked,
            "locked": locked,
            "total_unlocked": len(unlocked),
            "total_available": len(self.ACHIEVEMENTS),
            "completion_percentage": int((len(unlocked) / len(self.ACHIEVEMENTS)) * 100)
        }
