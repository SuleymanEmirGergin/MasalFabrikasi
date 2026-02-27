import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings


class ChallengeService:
    def __init__(self):
        self.challenges_file = f"{settings.STORAGE_PATH}/challenges.json"
        self.user_challenges_file = f"{settings.STORAGE_PATH}/user_challenges.json"
        self._ensure_challenges_file()
        self._ensure_user_challenges_file()
    
    def _ensure_challenges_file(self):
        """Challenges dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.challenges_file):
            with open(self.challenges_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _ensure_user_challenges_file(self):
        """User challenges dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.user_challenges_file):
            with open(self.user_challenges_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_challenges(self) -> List[Dict]:
        """Görev tanımlarını yükler."""
        try:
            with open(self.challenges_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _load_user_challenges(self) -> Dict[str, Dict]:
        """Kullanıcı görev durumlarını yükler."""
        try:
            with open(self.user_challenges_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_user_challenges(self, user_challenges: Dict[str, Dict]):
        """Kullanıcı görev durumlarını kaydeder."""
        with open(self.user_challenges_file, 'w', encoding='utf-8') as f:
            json.dump(user_challenges, f, ensure_ascii=False, indent=2)
    
    def get_daily_challenges(self) -> List[Dict]:
        """Günlük görevleri getirir."""
        today = datetime.now().date().isoformat()
        
        challenges = [
            {
                'id': 'daily_story',
                'name': 'Günlük Hikâye',
                'description': 'Bugün bir hikâye oluşturun',
                'type': 'daily',
                'target': 1,
                'xp_reward': 20,
                'date': today
            },
            {
                'id': 'daily_like',
                'name': 'Beğeni Ver',
                'description': '3 hikâyeye beğeni verin',
                'type': 'daily',
                'target': 3,
                'xp_reward': 15,
                'date': today
            },
            {
                'id': 'daily_comment',
                'name': 'Yorum Yap',
                'description': '2 hikâyeye yorum yapın',
                'type': 'daily',
                'target': 2,
                'xp_reward': 10,
                'date': today
            }
        ]
        
        return challenges
    
    def get_weekly_challenges(self) -> List[Dict]:
        """Haftalık mücadeleleri getirir."""
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date().isoformat()
        
        challenges = [
            {
                'id': 'weekly_stories',
                'name': 'Haftalık Yazar',
                'description': 'Bu hafta 5 hikâye oluşturun',
                'type': 'weekly',
                'target': 5,
                'xp_reward': 100,
                'week_start': week_start
            },
            {
                'id': 'weekly_characters',
                'name': 'Karakter Yaratıcısı',
                'description': 'Bu hafta 3 karakter oluşturun',
                'type': 'weekly',
                'target': 3,
                'xp_reward': 75,
                'week_start': week_start
            }
        ]
        
        return challenges
    
    def get_user_challenge_progress(self, user_id: str, challenge_id: str) -> Dict:
        """Kullanıcının görev ilerlemesini getirir."""
        user_challenges = self._load_user_challenges()
        user_key = f"{user_id}_{challenge_id}"
        
        if user_key not in user_challenges:
            return {
                'challenge_id': challenge_id,
                'progress': 0,
                'completed': False,
                'completed_at': None
            }
        
        return user_challenges[user_key]
    
    def update_challenge_progress(self, user_id: str, challenge_id: str, progress: int) -> Dict:
        """Görev ilerlemesini günceller."""
        user_challenges = self._load_user_challenges()
        user_key = f"{user_id}_{challenge_id}"
        
        if user_key not in user_challenges:
            user_challenges[user_key] = {
                'challenge_id': challenge_id,
                'progress': 0,
                'completed': False,
                'completed_at': None
            }
        
        user_challenges[user_key]['progress'] = progress
        
        # Görev tamamlandı mı kontrol et
        challenges = self.get_daily_challenges() + self.get_weekly_challenges()
        challenge = next((c for c in challenges if c['id'] == challenge_id), None)
        
        if challenge and progress >= challenge['target']:
            user_challenges[user_key]['completed'] = True
            user_challenges[user_key]['completed_at'] = datetime.now().isoformat()
        
        self._save_user_challenges(user_challenges)
        return user_challenges[user_key]
    
    def complete_challenge(self, user_id: str, challenge_id: str) -> Dict:
        """Görevi tamamlar."""
        user_challenges = self._load_user_challenges()
        user_key = f"{user_id}_{challenge_id}"
        
        if user_key not in user_challenges:
            raise ValueError("Görev bulunamadı")
        
        if user_challenges[user_key]['completed']:
            raise ValueError("Görev zaten tamamlanmış")
        
        user_challenges[user_key]['completed'] = True
        user_challenges[user_key]['completed_at'] = datetime.now().isoformat()
        
        self._save_user_challenges(user_challenges)
        
        # XP ödülü ver
        challenges = self.get_daily_challenges() + self.get_weekly_challenges()
        challenge = next((c for c in challenges if c['id'] == challenge_id), None)
        
        xp_reward = 0
        if challenge:
            xp_reward = challenge.get('xp_reward', 0)
        
        return {
            'challenge_id': challenge_id,
            'completed': True,
            'xp_reward': xp_reward
        }

