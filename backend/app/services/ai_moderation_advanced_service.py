from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.content_moderation_service import ContentModerationService
import json
import os
from datetime import datetime
from app.core.config import settings


class AIModerationAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.moderation_service = ContentModerationService()
        self.moderation_logs_file = os.path.join(settings.STORAGE_PATH, "moderation_logs.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.moderation_logs_file):
            with open(self.moderation_logs_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def realtime_content_check(
        self,
        text: str,
        content_type: str = "story"
    ) -> Dict:
        """Gerçek zamanlı içerik kontrolü yapar."""
        # Hızlı kontrol için basit keyword kontrolü
        inappropriate_keywords = []  # Gerçek uygulamada liste olmalı
        
        text_lower = text.lower()
        found_keywords = [kw for kw in inappropriate_keywords if kw in text_lower]
        
        if found_keywords:
            return {
                "is_appropriate": False,
                "issues": ["Uygunsuz içerik tespit edildi"],
                "severity": "high",
                "found_keywords": found_keywords
            }
        
        # Detaylı kontrol için AI moderasyon
        return await self.moderation_service.moderate_content(text, content_type)
    
    async def auto_filter_inappropriate(
        self,
        text: str
    ) -> Dict:
        """Uygunsuz içeriği otomatik filtreler."""
        moderation = await self.moderation_service.moderate_content(text, "story")
        
        if not moderation.get('is_appropriate', True):
            # AI ile iyileştirme öner
            prompt = f"""
Aşağıdaki metindeki uygunsuz içeriği temizle ve iyileştir.

Orijinal Metin: {text}
Sorunlar: {', '.join(moderation.get('issues', []))}

İyileştirilmiş metni döndür:
"""
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen bir içerik moderatörüsün. Uygunsuz içeriği temizliyorsun."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                improved_text = response.choices[0].message.content.strip()
            except:
                improved_text = text
            
            return {
                "original_text": text,
                "filtered_text": improved_text,
                "issues": moderation.get('issues', []),
                "suggestions": ["İçerik temizlendi ve iyileştirildi"]
            }
        
        return {
            "original_text": text,
            "filtered_text": text,
            "issues": [],
            "is_clean": True
        }
    
    def log_moderation_action(
        self,
        story_id: str,
        action: str,
        result: Dict
    ):
        """Moderasyon aksiyonunu loglar."""
        log_entry = {
            "story_id": story_id,
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.moderation_logs_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        logs.append(log_entry)
        with open(self.moderation_logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

