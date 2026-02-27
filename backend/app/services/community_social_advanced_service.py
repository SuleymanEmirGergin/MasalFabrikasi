from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings


class CommunitySocialAdvancedService:
    def __init__(self):
        self.contests_file = os.path.join(settings.STORAGE_PATH, "contests.json")
        self.templates_file = os.path.join(settings.STORAGE_PATH, "community_templates.json")
        self.groups_file = os.path.join(settings.STORAGE_PATH, "story_groups.json")
        self.author_profiles_file = os.path.join(settings.STORAGE_PATH, "author_profiles.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.contests_file, self.templates_file, self.groups_file, self.author_profiles_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_contest(
        self,
        title: str,
        description: str,
        theme: str,
        start_date: str,
        end_date: str,
        creator_id: str
    ) -> Dict:
        """Hikâye yarışması oluşturur."""
        contest = {
            "contest_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "theme": theme,
            "start_date": start_date,
            "end_date": end_date,
            "creator_id": creator_id,
            "participants": [],
            "submissions": [],
            "winners": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.contests_file, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        contests.append(contest)
        with open(self.contests_file, 'w', encoding='utf-8') as f:
            json.dump(contests, f, ensure_ascii=False, indent=2)
        
        return contest
    
    def submit_to_contest(self, contest_id: str, story_id: str, user_id: str) -> Dict:
        """Yarışmaya hikâye gönderir."""
        with open(self.contests_file, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        contest = next((c for c in contests if c.get('contest_id') == contest_id), None)
        if not contest:
            raise ValueError("Yarışma bulunamadı")
        
        submission = {
            "submission_id": str(uuid.uuid4()),
            "contest_id": contest_id,
            "story_id": story_id,
            "user_id": user_id,
            "submitted_at": datetime.now().isoformat(),
            "votes": 0
        }
        
        contest['submissions'].append(submission)
        if user_id not in contest['participants']:
            contest['participants'].append(user_id)
        
        with open(self.contests_file, 'w', encoding='utf-8') as f:
            json.dump(contests, f, ensure_ascii=False, indent=2)
        
        return submission
    
    def create_community_template(
        self,
        name: str,
        content: str,
        category: str,
        creator_id: str,
        is_public: bool = True
    ) -> Dict:
        """Topluluk şablonu oluşturur."""
        template = {
            "template_id": str(uuid.uuid4()),
            "name": name,
            "content": content,
            "category": category,
            "creator_id": creator_id,
            "is_public": is_public,
            "usage_count": 0,
            "rating": 0.0,
            "ratings": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        templates.append(template)
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        return template
    
    def create_story_group(
        self,
        name: str,
        description: str,
        creator_id: str,
        is_public: bool = True
    ) -> Dict:
        """Hikâye paylaşım grubu oluşturur."""
        group = {
            "group_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "creator_id": creator_id,
            "is_public": is_public,
            "members": [creator_id],
            "stories": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.groups_file, 'r', encoding='utf-8') as f:
            groups = json.load(f)
        groups.append(group)
        with open(self.groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=2)
        
        return group
    
    def create_author_profile(
        self,
        user_id: str,
        pen_name: str,
        bio: Optional[str] = None,
        social_links: Optional[Dict] = None
    ) -> Dict:
        """Yazar profili oluşturur."""
        profile = {
            "profile_id": str(uuid.uuid4()),
            "user_id": user_id,
            "pen_name": pen_name,
            "bio": bio or "",
            "social_links": social_links or {},
            "total_stories": 0,
            "total_views": 0,
            "total_likes": 0,
            "followers": [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.author_profiles_file, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        profiles.append(profile)
        with open(self.author_profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        
        return profile
    
    def get_author_profile(self, user_id: str) -> Optional[Dict]:
        """Yazar profilini getirir."""
        with open(self.author_profiles_file, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        return next((p for p in profiles if p.get('user_id') == user_id), None)
    
    def follow_author(self, author_user_id: str, follower_user_id: str) -> Dict:
        """Yazarı takip et."""
        profile = self.get_author_profile(author_user_id)
        if not profile:
            raise ValueError("Yazar profili bulunamadı")
        
        if follower_user_id not in profile.get('followers', []):
            profile['followers'].append(follower_user_id)
            
            with open(self.author_profiles_file, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
            profiles = [p for p in profiles if p.get('user_id') != author_user_id]
            profiles.append(profile)
            with open(self.author_profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
        
        return profile

