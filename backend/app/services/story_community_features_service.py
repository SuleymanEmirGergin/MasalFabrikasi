from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryCommunityFeaturesService:
    """Hikaye topluluk özellikleri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.communities_file = os.path.join(settings.STORAGE_PATH, "communities.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.communities_file):
            with open(self.communities_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_community(
        self,
        creator_id: str,
        community_name: str,
        description: str,
        is_public: bool = True
    ) -> Dict:
        """Topluluk oluşturur."""
        community_id = str(uuid.uuid4())
        
        community = {
            "community_id": community_id,
            "creator_id": creator_id,
            "name": community_name,
            "description": description,
            "is_public": is_public,
            "members": [creator_id],
            "stories": [],
            "created_at": datetime.now().isoformat()
        }
        
        communities = self._load_communities()
        communities.append(community)
        self._save_communities(communities)
        
        return {
            "community_id": community_id,
            "name": community_name,
            "message": "Topluluk oluşturuldu"
        }
    
    async def join_community(
        self,
        community_id: str,
        user_id: str
    ) -> Dict:
        """Topluluğa katıl."""
        communities = self._load_communities()
        community = next((c for c in communities if c["community_id"] == community_id), None)
        
        if not community:
            raise ValueError("Topluluk bulunamadı")
        
        if user_id in community["members"]:
            return {"message": "Zaten topluluk üyesisiniz"}
        
        community["members"].append(user_id)
        self._save_communities(communities)
        
        return {
            "message": "Topluluğa katıldınız",
            "members_count": len(community["members"])
        }
    
    async def share_story_to_community(
        self,
        community_id: str,
        story_id: str,
        user_id: str
    ) -> Dict:
        """Hikayeyi topluluğa paylaş."""
        communities = self._load_communities()
        community = next((c for c in communities if c["community_id"] == community_id), None)
        
        if not community:
            raise ValueError("Topluluk bulunamadı")
        
        if user_id not in community["members"]:
            raise ValueError("Topluluk üyesi değilsiniz")
        
        if story_id not in community["stories"]:
            community["stories"].append(story_id)
            self._save_communities(communities)
            return {"message": "Hikaye topluluğa paylaşıldı"}
        else:
            return {"message": "Hikaye zaten paylaşılmış"}
    
    async def get_community_stories(
        self,
        community_id: str
    ) -> List[str]:
        """Topluluk hikayelerini getirir."""
        communities = self._load_communities()
        community = next((c for c in communities if c["community_id"] == community_id), None)
        
        if not community:
            raise ValueError("Topluluk bulunamadı")
        
        return community.get("stories", [])
    
    async def get_popular_communities(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """Popüler toplulukları getirir."""
        communities = self._load_communities()
        
        # Üye sayısına göre sırala
        communities.sort(key=lambda x: len(x.get("members", [])), reverse=True)
        
        return [
            {
                "community_id": c["community_id"],
                "name": c["name"],
                "members_count": len(c.get("members", [])),
                "stories_count": len(c.get("stories", []))
            }
            for c in communities[:limit]
        ]
    
    def _load_communities(self) -> List[Dict]:
        """Toplulukları yükler."""
        try:
            with open(self.communities_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_communities(self, communities: List[Dict]):
        """Toplulukları kaydeder."""
        with open(self.communities_file, 'w', encoding='utf-8') as f:
            json.dump(communities, f, ensure_ascii=False, indent=2)

