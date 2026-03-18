from typing import List, Dict
from app.services.user_service import UserService
from app.services.story_storage import StoryStorage
from app.services.like_service import LikeService


class LeaderboardService:
    def __init__(self):
        self.user_service = UserService()
        self.story_storage = StoryStorage()
        self.like_service = LikeService()
    
    def get_stories_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Hikâye sayısına göre liderlik tablosu."""
        users = self.user_service._load_users()
        stories = self.story_storage.get_all_stories()
        
        user_story_counts = {}
        for story in stories:
            user_id = story.get('user_id', 'unknown')
            if user_id not in user_story_counts:
                user_story_counts[user_id] = 0
            user_story_counts[user_id] += 1
        
        leaderboard = []
        for user_id, count in sorted(user_story_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            user = self.user_service.get_user(user_id)
            if user:
                leaderboard.append({
                    'user_id': user_id,
                    'name': user.get('name', 'Unknown'),
                    'count': count
                })
        
        return leaderboard
    
    def get_likes_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Toplam beğeni sayısına göre liderlik tablosu."""
        users = self.user_service._load_users()
        stories = self.story_storage.get_all_stories()
        
        user_like_counts = {}
        for story in stories:
            user_id = story.get('user_id', 'unknown')
            likes_data = self.like_service.get_story_likes(story.get('story_id'))
            like_count = likes_data.get('like_count', 0)
            
            if user_id not in user_like_counts:
                user_like_counts[user_id] = 0
            user_like_counts[user_id] += like_count
        
        leaderboard = []
        for user_id, count in sorted(user_like_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
            user = self.user_service.get_user(user_id)
            if user:
                leaderboard.append({
                    'user_id': user_id,
                    'name': user.get('name', 'Unknown'),
                    'count': count
                })
        
        return leaderboard
    
    def get_xp_leaderboard(self, limit: int = 10) -> List[Dict]:
        """XP'ye göre liderlik tablosu."""
        users = self.user_service._load_users()
        
        leaderboard = []
        for user in users.values():
            xp_info = self.user_service.get_user_xp(user.get('user_id'))
            leaderboard.append({
                'user_id': user.get('user_id'),
                'name': user.get('name', 'Unknown'),
                'xp': xp_info.get('xp', 0),
                'level': xp_info.get('level', 1)
            })
        
        leaderboard.sort(key=lambda x: x.get('xp', 0), reverse=True)
        return leaderboard[:limit]

