import json
import os
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import settings
from app.services.story_storage import StoryStorage


from app.services.ai_gamification_advanced_service import AIGamificationAdvancedService

class UserProfileService:
    def __init__(self):
        self.profile_file = f"{settings.STORAGE_PATH}/user_profile.json"
        self.story_storage = StoryStorage()
        self.gamification_service = AIGamificationAdvancedService()
        self._ensure_profile_file()
    
    def _ensure_profile_file(self):
        """Profil dosyası yoksa oluşturur."""
        if not os.path.exists(self.profile_file):
            default_profile = self._get_default_profile()
            self._save_profile(default_profile)

    def _load_profile(self) -> Dict:
        """Profil verilerini yükler."""
        self._ensure_profile_file()
        try:
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_default_profile()

    def _get_default_profile(self) -> Dict:
        """Varsayılan profil."""
        return {
            "user_id": "default_user",
            "xp": 0,
            "level": 1,
            "preferences": {
                "default_language": "tr",
                "default_story_type": "masal",
                "default_image_style": "fantasy",
                "default_image_size": "1024x1024",
                "default_audio_speed": 1.0,
                "theme": "light",
            },
            "statistics": {
                "total_stories": 0,
                "favorite_stories": 0,
                "collections_count": 0,
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    
    def _save_profile(self, profile: Dict):
        """Profil verilerini kaydeder."""
        profile['updated_at'] = datetime.now().isoformat()
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    
    def get_profile(self) -> Dict:
        """Kullanıcı profilini getirir."""
        profile = self._load_profile()
        
        # İstatistikleri güncelle
        stories = self.story_storage.get_all_stories()
        profile['statistics']['total_stories'] = len(stories)
        profile['statistics']['favorite_stories'] = len(
            [s for s in stories if s.get('is_favorite', False)]
        )
        
        # Koleksiyon sayısını güncelle (opsiyonel - collection service'den alınabilir)
        # Şimdilik 0 olarak bırakıyoruz
        
        self._save_profile(profile)
        return profile
    
    def update_preferences(self, preferences: Dict) -> Dict:
        """Kullanıcı tercihlerini günceller."""
        profile = self._load_profile()
        profile['preferences'].update(preferences)
        self._save_profile(profile)
        return profile
    
    def get_preferences(self) -> Dict:
        """Kullanıcı tercihlerini getirir."""
        profile = self._load_profile()
        return profile.get('preferences', {})
    
    def get_statistics(self) -> Dict:
        """Kullanıcı istatistiklerini getirir."""
        profile = self.get_profile()
        return profile.get('statistics', {})

    def add_xp(self, amount: int) -> Dict:
        """
        Kullanıcıya XP ekler ve seviye kontrolü yapar.
        Returns:
            {
                "xp_gained": int,
                "new_xp": int,
                "level": int,
                "leveled_up": bool,
                "message": str
            }
        """
        profile = self._load_profile()
        
        # XP ve Level alanlarını kontrol et (eski profiller için)
        if 'xp' not in profile: profile['xp'] = 0
        if 'level' not in profile: profile['level'] = 1
        
        old_level = profile['level']
        profile['xp'] += amount
        
        # Seviye hesapla using advanced service
        # Default system ID kullanıyoruz şimdilik
        level_info = self.gamification_service.calculate_user_level(
            profile['user_id'], 
            "default", 
            profile['xp']
        )
        
        new_level = level_info.get('level', 1)
        
        leveled_up = new_level > old_level
        profile['level'] = new_level
        
        self._save_profile(profile)
        
        return {
            "xp_gained": amount,
            "new_xp": profile['xp'],
            "level": new_level,
            "leveled_up": leveled_up,
            "message": f"Tebrikler! Seviye {new_level} oldunuz!" if leveled_up else f"+{amount} XP kazanıldı"
        }


