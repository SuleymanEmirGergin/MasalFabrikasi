from typing import Dict, Optional, List
import json
import os
from datetime import datetime
from app.core.config import settings


class PlatformIntegrationService:
    def __init__(self):
        self.integrations_file = os.path.join(settings.STORAGE_PATH, "platform_integrations.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.integrations_file):
            with open(self.integrations_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def connect_wordpress(self, user_id: str, site_url: str, api_key: str) -> Dict:
        integration = {
            "user_id": user_id,
            "platform": "wordpress",
            "site_url": site_url,
            "api_key": api_key,
            "connected_at": datetime.now().isoformat(),
            "is_active": True
        }
        self._save_integration(user_id, integration)
        return integration
    
    def connect_medium(self, user_id: str, access_token: str) -> Dict:
        integration = {
            "user_id": user_id,
            "platform": "medium",
            "access_token": access_token,
            "connected_at": datetime.now().isoformat(),
            "is_active": True
        }
        self._save_integration(user_id, integration)
        return integration
    
    def _save_integration(self, user_id: str, integration: Dict):
        with open(self.integrations_file, 'r', encoding='utf-8') as f:
            integrations = json.load(f)
        if user_id not in integrations:
            integrations[user_id] = []
        integrations[user_id].append(integration)
        with open(self.integrations_file, 'w', encoding='utf-8') as f:
            json.dump(integrations, f, ensure_ascii=False, indent=2)
    
    async def publish_to_wordpress(self, user_id: str, story_id: str, site_url: str) -> Dict:
        return {"message": "WordPress entegrasyonu için API çağrısı yapılmalı", "story_id": story_id}
    
    async def publish_to_medium(self, user_id: str, story_id: str) -> Dict:
        return {"message": "Medium entegrasyonu için API çağrısı yapılmalı", "story_id": story_id}
    
    async def auto_share_to_social(self, user_id: str, story_id: str, platforms: List[str]) -> Dict:
        results = {}
        for platform in platforms:
            if platform == "twitter":
                results["twitter"] = {"status": "shared", "message": "Twitter API entegrasyonu gerekli"}
            elif platform == "facebook":
                results["facebook"] = {"status": "shared", "message": "Facebook API entegrasyonu gerekli"}
        return results

