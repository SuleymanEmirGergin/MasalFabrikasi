from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.story_service import StoryService


class StoryAutomationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.story_service = StoryService()
        self.automations_file = os.path.join(settings.STORAGE_PATH, "story_automations.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.automations_file):
            with open(self.automations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_automation(
        self,
        user_id: str,
        automation_type: str,
        trigger: Dict,
        action: Dict
    ) -> Dict:
        """Otomasyon oluşturur."""
        automation = {
            "automation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "automation_type": automation_type,
            "trigger": trigger,
            "action": action,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.automations_file, 'r', encoding='utf-8') as f:
            automations = json.load(f)
        automations.append(automation)
        with open(self.automations_file, 'w', encoding='utf-8') as f:
            json.dump(automations, f, ensure_ascii=False, indent=2)
        
        return automation
    
    async def execute_automation(self, automation_id: str, trigger_data: Dict) -> Dict:
        """Otomasyonu çalıştırır."""
        with open(self.automations_file, 'r', encoding='utf-8') as f:
            automations = json.load(f)
        
        automation = next((a for a in automations if a.get('automation_id') == automation_id), None)
        if not automation or not automation.get('is_active'):
            return {"executed": False, "reason": "Otomasyon bulunamadı veya aktif değil"}
        
        action = automation.get('action', {})
        action_type = action.get('type')
        
        if action_type == "create_story":
            # Otomatik hikâye oluştur
            theme = action.get('theme', 'Otomatik hikâye')
            story_text = await self.story_service.generate_story(theme, "tr", "masal")
            return {"executed": True, "story_created": True, "theme": theme}
        
        elif action_type == "send_notification":
            return {"executed": True, "notification_sent": True}
        
        return {"executed": False, "reason": "Bilinmeyen aksiyon tipi"}
    
    def get_user_automations(self, user_id: str) -> List[Dict]:
        """Kullanıcının otomasyonlarını getirir."""
        with open(self.automations_file, 'r', encoding='utf-8') as f:
            automations = json.load(f)
        return [a for a in automations if a.get('user_id') == user_id and a.get('is_active', False)]

