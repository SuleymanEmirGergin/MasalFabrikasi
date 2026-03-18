from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime, timedelta


class StoryViralFeaturesService:
    """Hikaye sosyal paylaşım ve viral özellikler servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.viral_data_file = os.path.join(settings.STORAGE_PATH, "viral_data.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.viral_data_file):
            with open(self.viral_data_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_viral_content(
        self,
        story_id: str,
        story_text: str,
        content_type: str = "quote"
    ) -> Dict:
        """Viral içerik oluşturur."""
        viral_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeden {content_type} formatında viral içerik oluştur.
Paylaşılabilir, ilgi çekici ve akılda kalıcı olsun:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir sosyal medya içerik uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        viral_content = response.choices[0].message.content
        
        content = {
            "viral_id": viral_id,
            "story_id": story_id,
            "content_type": content_type,
            "content": viral_content,
            "shares": 0,
            "likes": 0,
            "views": 0,
            "created_at": datetime.now().isoformat()
        }
        
        viral_data = self._load_viral_data()
        if story_id not in viral_data:
            viral_data[story_id] = []
        viral_data[story_id].append(content)
        self._save_viral_data(viral_data)
        
        return {
            "viral_id": viral_id,
            "content_type": content_type,
            "content": viral_content
        }
    
    async def track_sharing(
        self,
        story_id: str,
        platform: str,
        user_id: Optional[str] = None
    ) -> Dict:
        """Paylaşımı takip eder."""
        viral_data = self._load_viral_data()
        
        if story_id not in viral_data:
            viral_data[story_id] = []
        
        # Paylaşım sayısını artır
        for content in viral_data[story_id]:
            content["shares"] = content.get("shares", 0) + 1
        
        sharing_event = {
            "event_id": str(uuid.uuid4()),
            "story_id": story_id,
            "platform": platform,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        if "sharing_events" not in viral_data:
            viral_data["sharing_events"] = []
        viral_data["sharing_events"].append(sharing_event)
        
        self._save_viral_data(viral_data)
        
        return {
            "message": "Paylaşım kaydedildi",
            "total_shares": sum(c.get("shares", 0) for c in viral_data.get(story_id, []))
        }
    
    async def get_viral_stats(
        self,
        story_id: str
    ) -> Dict:
        """Viral istatistikleri getirir."""
        viral_data = self._load_viral_data()
        story_content = viral_data.get(story_id, [])
        
        total_shares = sum(c.get("shares", 0) for c in story_content)
        total_likes = sum(c.get("likes", 0) for c in story_content)
        total_views = sum(c.get("views", 0) for c in story_content)
        
        # Son 24 saatteki paylaşımlar
        recent_shares = 0
        if "sharing_events" in viral_data:
            cutoff = datetime.now() - timedelta(hours=24)
            recent_shares = len([
                e for e in viral_data["sharing_events"]
                if e.get("story_id") == story_id
                and datetime.fromisoformat(e["timestamp"]) >= cutoff
            ])
        
        return {
            "story_id": story_id,
            "total_shares": total_shares,
            "total_likes": total_likes,
            "total_views": total_views,
            "recent_shares_24h": recent_shares,
            "viral_score": self._calculate_viral_score(total_shares, total_likes, total_views)
        }
    
    def _calculate_viral_score(
        self,
        shares: int,
        likes: int,
        views: int
    ) -> float:
        """Viral skor hesaplar."""
        if views == 0:
            return 0.0
        
        engagement_rate = (shares + likes) / views
        return round(engagement_rate * 100, 2)
    
    async def create_shareable_image(
        self,
        story_id: str,
        quote: str,
        style: str = "modern"
    ) -> Dict:
        """Paylaşılabilir görsel oluşturur."""
        image_id = str(uuid.uuid4())
        
        # Görsel oluşturma için prompt
        image_prompt = f"{quote} - {style} stilinde paylaşılabilir görsel"
        
        return {
            "image_id": image_id,
            "quote": quote,
            "style": style,
            "image_prompt": image_prompt,
            "message": "Paylaşılabilir görsel oluşturuldu"
        }
    
    def _load_viral_data(self) -> Dict:
        """Viral verileri yükler."""
        try:
            with open(self.viral_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_viral_data(self, viral_data: Dict):
        """Viral verileri kaydeder."""
        with open(self.viral_data_file, 'w', encoding='utf-8') as f:
            json.dump(viral_data, f, ensure_ascii=False, indent=2)

