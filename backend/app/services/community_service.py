from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage


class CommunityService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.contests_file = os.path.join(settings.STORAGE_PATH, "contests.json")
        self.themes_file = os.path.join(settings.STORAGE_PATH, "community_themes.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.contests_file):
            with open(self.contests_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.themes_file):
            with open(self.themes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_contest(
        self,
        title: str,
        description: str,
        theme: str,
        start_date: str,
        end_date: str,
        created_by: str
    ) -> Dict:
        """
        Yeni bir yarışma oluşturur.
        
        Args:
            title: Yarışma başlığı
            description: Açıklama
            theme: Yarışma teması
            start_date: Başlangıç tarihi (ISO format)
            end_date: Bitiş tarihi (ISO format)
            created_by: Oluşturan kullanıcı ID'si
        
        Returns:
            Yarışma objesi
        """
        contest = {
            "contest_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "theme": theme,
            "start_date": start_date,
            "end_date": end_date,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "participants": [],
            "submissions": [],
            "winners": []
        }
        
        self._save_contest(contest)
        return contest
    
    def _save_contest(self, contest: Dict):
        """Yarışmayı kaydeder."""
        with open(self.contests_file, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        contests.append(contest)
        
        with open(self.contests_file, 'w', encoding='utf-8') as f:
            json.dump(contests, f, ensure_ascii=False, indent=2)
    
    def get_active_contests(self) -> List[Dict]:
        """Aktif yarışmaları getirir."""
        with open(self.contests_file, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        now = datetime.now().isoformat()
        active = [
            c for c in contests
            if c.get('start_date') <= now <= c.get('end_date')
        ]
        
        return sorted(active, key=lambda x: x.get('end_date'), reverse=True)
    
    def get_contest(self, contest_id: str) -> Optional[Dict]:
        """Yarışmayı getirir."""
        with open(self.contests_file, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        return next((c for c in contests if c.get('contest_id') == contest_id), None)
    
    def submit_to_contest(self, contest_id: str, story_id: str, user_id: str) -> Dict:
        """Yarışmaya hikâye gönderir."""
        contest = self.get_contest(contest_id)
        if not contest:
            raise ValueError("Yarışma bulunamadı")
        
        # Yarışma aktif mi kontrol et
        now = datetime.now().isoformat()
        if not (contest.get('start_date') <= now <= contest.get('end_date')):
            raise ValueError("Yarışma aktif değil")
        
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        # Kullanıcı zaten katılmış mı?
        submissions = contest.get('submissions', [])
        if any(s.get('user_id') == user_id for s in submissions):
            raise ValueError("Bu yarışmaya zaten katıldınız")
        
        # Gönderimi ekle
        submission = {
            "story_id": story_id,
            "user_id": user_id,
            "submitted_at": datetime.now().isoformat(),
            "votes": 0,
            "likes": 0
        }
        
        submissions.append(submission)
        contest['submissions'] = submissions
        
        # Katılımcı listesine ekle
        if user_id not in contest.get('participants', []):
            contest['participants'].append(user_id)
        
        # Yarışmayı güncelle
        self._update_contest(contest)
        
        return submission
    
    def _update_contest(self, contest: Dict):
        """Yarışmayı günceller."""
        with open(self.contests_file, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        contests = [c for c in contests if c.get('contest_id') != contest.get('contest_id')]
        contests.append(contest)
        
        with open(self.contests_file, 'w', encoding='utf-8') as f:
            json.dump(contests, f, ensure_ascii=False, indent=2)
    
    def vote_for_contest_submission(self, contest_id: str, story_id: str, user_id: str) -> bool:
        """Yarışma gönderimine oy verir."""
        contest = self.get_contest(contest_id)
        if not contest:
            raise ValueError("Yarışma bulunamadı")
        
        submissions = contest.get('submissions', [])
        submission = next((s for s in submissions if s.get('story_id') == story_id), None)
        
        if not submission:
            raise ValueError("Gönderim bulunamadı")
        
        # Oy sayısını artır
        submission['votes'] = submission.get('votes', 0) + 1
        
        self._update_contest(contest)
        return True
    
    def get_community_themes(self) -> List[Dict]:
        """Topluluk temalarını getirir."""
        try:
            with open(self.themes_file, 'r', encoding='utf-8') as f:
                themes = json.load(f)
            return themes
        except:
            return []
    
    def add_community_theme(self, theme: str, description: str, added_by: str) -> Dict:
        """Yeni topluluk teması ekler."""
        theme_obj = {
            "theme_id": str(uuid.uuid4()),
            "theme": theme,
            "description": description,
            "added_by": added_by,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "likes": 0
        }
        
        with open(self.themes_file, 'r', encoding='utf-8') as f:
            themes = json.load(f)
        
        themes.append(theme_obj)
        
        with open(self.themes_file, 'w', encoding='utf-8') as f:
            json.dump(themes, f, ensure_ascii=False, indent=2)
        
        return theme_obj
    
    def get_weekly_themes(self) -> List[Dict]:
        """Haftalık temaları getirir (son 7 gün)."""
        themes = self.get_community_themes()
        
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_themes = [t for t in themes if t.get('created_at', '') >= week_ago]
        
        # Kullanım sayısına göre sırala
        recent_themes.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
        
        return recent_themes[:10]

