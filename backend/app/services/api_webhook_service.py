from typing import List, Dict, Optional
import json
import os
import uuid
import httpx
from datetime import datetime
from app.core.config import settings


class APIWebhookService:
    def __init__(self):
        self.webhooks_file = os.path.join(settings.STORAGE_PATH, "webhooks.json")
        self.api_keys_file = os.path.join(settings.STORAGE_PATH, "api_keys.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.webhooks_file, self.api_keys_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def create_webhook(self, user_id: str, url: str, events: List[str], secret: Optional[str] = None) -> Dict:
        webhook = {
            "webhook_id": str(uuid.uuid4()),
            "user_id": user_id,
            "url": url,
            "events": events,
            "secret": secret,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        self._save_webhook(webhook)
        return webhook
    
    def _save_webhook(self, webhook: Dict):
        with open(self.webhooks_file, 'r', encoding='utf-8') as f:
            webhooks = json.load(f)
        webhooks.append(webhook)
        with open(self.webhooks_file, 'w', encoding='utf-8') as f:
            json.dump(webhooks, f, ensure_ascii=False, indent=2)
    
    async def trigger_webhook(self, event_type: str, data: Dict):
        with open(self.webhooks_file, 'r', encoding='utf-8') as f:
            webhooks = json.load(f)
        
        active_webhooks = [w for w in webhooks if w.get('is_active', False) and event_type in w.get('events', [])]
        
        for webhook in active_webhooks:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        webhook['url'],
                        json={"event": event_type, "data": data},
                        headers={"X-Webhook-Secret": webhook.get('secret', '')},
                        timeout=5.0
                    )
            except:
                pass
    
    def generate_api_key(self, user_id: str, key_name: str) -> Dict:
        api_key = {
            "key_id": str(uuid.uuid4()),
            "user_id": user_id,
            "key_name": key_name,
            "api_key": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        with open(self.api_keys_file, 'r', encoding='utf-8') as f:
            keys = json.load(f)
        keys.append(api_key)
        with open(self.api_keys_file, 'w', encoding='utf-8') as f:
            json.dump(keys, f, ensure_ascii=False, indent=2)
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        with open(self.api_keys_file, 'r', encoding='utf-8') as f:
            keys = json.load(f)
        
        key_data = next((k for k in keys if k.get('api_key') == api_key and k.get('is_active', False)), None)
        return key_data

