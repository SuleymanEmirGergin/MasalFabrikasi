from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class SocialFeaturesService:
    def __init__(self):
        self.clubs_file = os.path.join(settings.STORAGE_PATH, "story_clubs.json")
        self.groups_file = os.path.join(settings.STORAGE_PATH, "reading_groups.json")
        self.challenges_file = os.path.join(settings.STORAGE_PATH, "writing_challenges.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.clubs_file, self.groups_file, self.challenges_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_story_club(
        self,
        name: str,
        description: str,
        created_by: str,
        is_public: bool = True
    ) -> Dict:
        """
        Hikâye kulübü oluşturur.
        """
        club = {
            "club_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "created_by": created_by,
            "is_public": is_public,
            "members": [created_by],
            "stories": [],
            "created_at": datetime.now().isoformat()
        }
        
        self._save_club(club)
        return club
    
    def _save_club(self, club: Dict):
        """Kulübü kaydeder."""
        with open(self.clubs_file, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
        
        clubs = [c for c in clubs if c.get('club_id') != club.get('club_id')]
        clubs.append(club)
        
        with open(self.clubs_file, 'w', encoding='utf-8') as f:
            json.dump(clubs, f, ensure_ascii=False, indent=2)
    
    def join_club(self, club_id: str, user_id: str) -> Dict:
        """Kulübe katılır."""
        club = self.get_club(club_id)
        if not club:
            raise ValueError("Kulüp bulunamadı")
        
        if user_id not in club.get('members', []):
            club['members'].append(user_id)
            self._save_club(club)
        
        return club
    
    def get_club(self, club_id: str) -> Optional[Dict]:
        """Kulübü getirir."""
        with open(self.clubs_file, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
        
        return next((c for c in clubs if c.get('club_id') == club_id), None)
    
    def get_public_clubs(self, limit: int = 20) -> List[Dict]:
        """Herkese açık kulüpleri getirir."""
        with open(self.clubs_file, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
        
        public = [c for c in clubs if c.get('is_public', False)]
        return sorted(public, key=lambda x: len(x.get('members', [])), reverse=True)[:limit]
    
    def create_reading_group(
        self,
        name: str,
        description: str,
        created_by: str,
        reading_goal: Optional[str] = None
    ) -> Dict:
        """
        Okuma grubu oluşturur.
        """
        group = {
            "group_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "created_by": created_by,
            "members": [created_by],
            "reading_goal": reading_goal,
            "discussions": [],
            "created_at": datetime.now().isoformat()
        }
        
        self._save_group(group)
        return group
    
    def _save_group(self, group: Dict):
        """Grubu kaydeder."""
        with open(self.groups_file, 'r', encoding='utf-8') as f:
            groups = json.load(f)
        
        groups = [g for g in groups if g.get('group_id') != group.get('group_id')]
        groups.append(group)
        
        with open(self.groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=2)
    
    def create_writing_challenge(
        self,
        title: str,
        description: str,
        theme: str,
        deadline: str,
        created_by: str
    ) -> Dict:
        """
        Yazma meydan okuması oluşturur.
        """
        challenge = {
            "challenge_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "theme": theme,
            "deadline": deadline,
            "created_by": created_by,
            "participants": [],
            "submissions": [],
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self._save_challenge(challenge)
        return challenge
    
    def _save_challenge(self, challenge: Dict):
        """Meydan okumayı kaydeder."""
        with open(self.challenges_file, 'r', encoding='utf-8') as f:
            challenges = json.load(f)
        
        challenges = [c for c in challenges if c.get('challenge_id') != challenge.get('challenge_id')]
        challenges.append(challenge)
        
        with open(self.challenges_file, 'w', encoding='utf-8') as f:
            json.dump(challenges, f, ensure_ascii=False, indent=2)
    
    def submit_to_challenge(
        self,
        challenge_id: str,
        story_id: str,
        user_id: str
    ) -> Dict:
        """
        Meydan okumaya hikâye gönderir.
        """
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            raise ValueError("Meydan okuma bulunamadı")
        
        if datetime.now().isoformat() > challenge.get('deadline', ''):
            raise ValueError("Meydan okuma süresi dolmuş")
        
        submission = {
            "submission_id": str(uuid.uuid4()),
            "story_id": story_id,
            "user_id": user_id,
            "submitted_at": datetime.now().isoformat()
        }
        
        challenge['submissions'].append(submission)
        
        if user_id not in challenge.get('participants', []):
            challenge['participants'].append(user_id)
        
        self._save_challenge(challenge)
        
        return submission
    
    def get_challenge(self, challenge_id: str) -> Optional[Dict]:
        """Meydan okumayı getirir."""
        with open(self.challenges_file, 'r', encoding='utf-8') as f:
            challenges = json.load(f)
        
        return next((c for c in challenges if c.get('challenge_id') == challenge_id), None)
    
    def get_active_challenges(self, limit: int = 10) -> List[Dict]:
        """Aktif meydan okumaları getirir."""
        with open(self.challenges_file, 'r', encoding='utf-8') as f:
            challenges = json.load(f)
        
        now = datetime.now().isoformat()
        active = [
            c for c in challenges
            if c.get('status') == 'active' and c.get('deadline', '') > now
        ]
        
        return sorted(active, key=lambda x: x.get('deadline', ''))[:limit]

