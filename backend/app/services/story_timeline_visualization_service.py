from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryTimelineVisualizationService:
    """Hikaye zaman çizelgesi görselleştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.timelines_file = os.path.join(settings.STORAGE_PATH, "story_timelines.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.timelines_file):
            with open(self.timelines_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_timeline(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikaye zaman çizelgesi oluşturur."""
        prompt = f"""Aşağıdaki hikayedeki olayları kronolojik sıraya göre listele. Her olay için:
1. Zaman/konum
2. Olay açıklaması
3. İlgili karakterler

Hikaye:
{story_text}

JSON formatında döndür."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        # Basit parse
        events = self._extract_events_from_text(story_text)
        
        timeline = {
            "story_id": story_id,
            "events": events,
            "created_at": datetime.now().isoformat()
        }
        
        timelines = self._load_timelines()
        timelines[story_id] = timeline
        self._save_timelines(timelines)
        
        return timeline
    
    def _extract_events_from_text(self, text: str) -> List[Dict]:
        """Metinden olayları çıkarır."""
        events = []
        sentences = text.split('.')
        
        for i, sentence in enumerate(sentences):
            if sentence.strip() and len(sentence.strip()) > 10:
                events.append({
                    "event_id": str(uuid.uuid4()),
                    "order": i,
                    "description": sentence.strip(),
                    "characters": [],
                    "location": None
                })
        
        return events
    
    async def get_timeline(self, story_id: str) -> Optional[Dict]:
        """Zaman çizelgesini getirir."""
        timelines = self._load_timelines()
        return timelines.get(story_id)
    
    async def add_custom_event(
        self,
        story_id: str,
        event_description: str,
        order: Optional[int] = None
    ) -> Dict:
        """Özel olay ekler."""
        timelines = self._load_timelines()
        timeline = timelines.get(story_id)
        
        if not timeline:
            raise ValueError("Zaman çizelgesi bulunamadı")
        
        if order is None:
            order = len(timeline["events"])
        
        event = {
            "event_id": str(uuid.uuid4()),
            "order": order,
            "description": event_description,
            "characters": [],
            "location": None,
            "is_custom": True
        }
        
        timeline["events"].append(event)
        timeline["events"].sort(key=lambda x: x["order"])
        timeline["updated_at"] = datetime.now().isoformat()
        
        self._save_timelines(timelines)
        
        return {"message": "Olay eklendi", "event": event}
    
    def _load_timelines(self) -> Dict:
        """Zaman çizelgelerini yükler."""
        try:
            with open(self.timelines_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_timelines(self, timelines: Dict):
        """Zaman çizelgelerini kaydeder."""
        with open(self.timelines_file, 'w', encoding='utf-8') as f:
            json.dump(timelines, f, ensure_ascii=False, indent=2)

