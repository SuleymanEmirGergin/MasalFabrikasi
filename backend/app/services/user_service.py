import json
import os
import uuid
from typing import Dict, Optional
from datetime import datetime
from app.core.config import settings


class UserService:
    def __init__(self):
        self.users_file = f"{settings.STORAGE_PATH}/users.json"
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Users dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_users(self) -> Dict[str, Dict]:
        """Tüm kullanıcıları yükler."""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict[str, Dict]):
        """Kullanıcıları kaydeder."""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def register_user(self, device_id: str, name: Optional[str] = None) -> Dict:
        """
        Yeni kullanıcı kaydı oluşturur veya mevcut kullanıcıyı getirir.
        
        Args:
            device_id: Cihaz ID'si
            name: Kullanıcı adı (opsiyonel)
        
        Returns:
            Kullanıcı verisi
        """
        users = self._load_users()
        
        # Eğer kullanıcı zaten varsa döndür
        if device_id in users:
            return users[device_id]
        
        # Yeni kullanıcı oluştur
        user_id = str(uuid.uuid4())
        user = {
            'user_id': user_id,
            'device_id': device_id,
            'name': name or f"Kullanıcı {user_id[:8]}",
            'avatar': None,
            'bio': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        users[device_id] = user
        self._save_users(users)
        
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Belirli bir kullanıcıyı getirir."""
        users = self._load_users()
        return next((u for u in users.values() if u.get('user_id') == user_id), None)
    
    def get_user_by_device_id(self, device_id: str) -> Optional[Dict]:
        """Device ID'ye göre kullanıcıyı getirir."""
        users = self._load_users()
        return users.get(device_id)
    
    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        """Kullanıcıyı günceller."""
        users = self._load_users()
        user = next((u for u in users.values() if u.get('user_id') == user_id), None)
        
        if not user:
            return None
        
        user.update(updates)
        user['updated_at'] = datetime.now().isoformat()
        
        # Device ID'ye göre kaydet
        users[user['device_id']] = user
        self._save_users(users)
        
        return user
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Kullanıcı istatistiklerini getirir."""
        from app.services.story_storage import StoryStorage
        story_storage = StoryStorage()
        
        stories = story_storage.get_all_stories()
        user_stories = [s for s in stories if s.get('user_id') == user_id]
        
        return {
            'total_stories': len(user_stories),
            'favorite_stories': sum(1 for s in user_stories if s.get('is_favorite', False)),
            'total_characters': 0,  # TODO: Character service'ten al
            'total_collections': 0,  # TODO: Collection service'ten al
        }
    
    def add_xp(self, user_id: str, xp_amount: int) -> Dict:
        """Kullanıcıya XP ekler ve seviyeyi hesaplar."""
        users = self._load_users()
        user = next((u for u in users.values() if u.get('user_id') == user_id), None)
        
        if not user:
            return None
        
        current_xp = user.get('xp', 0)
        current_level = user.get('level', 1)
        
        new_xp = current_xp + xp_amount
        new_level = self._calculate_level(new_xp)
        
        user['xp'] = new_xp
        user['level'] = new_level
        user['updated_at'] = datetime.now().isoformat()
        
        users[user['device_id']] = user
        self._save_users(users)
        
        return {
            'user_id': user_id,
            'xp': new_xp,
            'level': new_level,
            'xp_gained': xp_amount,
            'leveled_up': new_level > current_level
        }
    
    def _calculate_level(self, xp: int) -> int:
        """XP'ye göre seviye hesaplar."""
        # Her seviye için gerekli XP: level * 100
        level = 1
        required_xp = 0
        while required_xp <= xp:
            level += 1
            required_xp += level * 100
        return level - 1
    
    def record_activity(self, user_id: str) -> Dict:
        """Günlük aktiviteyi kaydeder ve streak'i günceller."""
        users = self._load_users()
        user = next((u for u in users.values() if u.get('user_id') == user_id), None)
        
        if not user:
            return None
        
        today = datetime.now().date().isoformat()
        last_activity = user.get('last_activity_date')
        current_streak = user.get('streak', 0)
        
        if last_activity == today:
            # Bugün zaten aktivite kaydedilmiş
            return {
                'user_id': user_id,
                'streak': current_streak,
                'last_activity_date': today
            }
        
        # Son aktivite bugün değilse streak'i kontrol et
        if last_activity:
            last_date = datetime.fromisoformat(last_activity).date()
            today_date = datetime.now().date()
            days_diff = (today_date - last_date).days
            
            if days_diff == 1:
                # Streak devam ediyor
                current_streak += 1
            elif days_diff > 1:
                # Streak kırıldı
                current_streak = 1
        else:
            # İlk aktivite
            current_streak = 1
        
        user['streak'] = current_streak
        user['last_activity_date'] = today
        user['updated_at'] = datetime.now().isoformat()
        
        users[user['device_id']] = user
        self._save_users(users)
        
        return {
            'user_id': user_id,
            'streak': current_streak,
            'last_activity_date': today,
            'streak_increased': current_streak > (user.get('streak', 0) if last_activity else 0)
        }
    
    def get_streak(self, user_id: str) -> Dict:
        """Kullanıcının streak bilgisini getirir."""
        users = self._load_users()
        user = next((u for u in users.values() if u.get('user_id') == user_id), None)
        
        if not user:
            return {'streak': 0, 'last_activity_date': None}
        
        return {
            'streak': user.get('streak', 0),
            'last_activity_date': user.get('last_activity_date'),
            'longest_streak': user.get('longest_streak', user.get('streak', 0))
        }
    
    def get_user_xp(self, user_id: str) -> Dict:
        """Kullanıcının XP bilgisini getirir."""
        users = self._load_users()
        user = next((u for u in users.values() if u.get('user_id') == user_id), None)
        
        if not user:
            return {'xp': 0, 'level': 1, 'xp_to_next_level': 100}
        
        current_xp = user.get('xp', 0)
        current_level = user.get('level', 1)
        xp_for_current_level = sum(i * 100 for i in range(1, current_level))
        xp_for_next_level = current_level * 100
        xp_to_next_level = xp_for_next_level - (current_xp - xp_for_current_level)
        
        return {
            'xp': current_xp,
            'level': current_level,
            'xp_to_next_level': xp_to_next_level,
            'xp_for_next_level': xp_for_next_level
        }

