from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentEnrichmentService:
    """Hikaye içerik zenginleştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.enrichments_file = os.path.join(settings.STORAGE_PATH, "content_enrichments.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.enrichments_file):
            with open(self.enrichments_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def enrich_story(
        self,
        story_id: str,
        story_text: str,
        enrichment_type: str = "descriptive"
    ) -> Dict:
        """Hikayeyi zenginleştirir."""
        enrichment_id = str(uuid.uuid4())
        
        enrichment_prompts = {
            "descriptive": "Açıklayıcı detaylar ekle, görsel betimlemeler yap",
            "emotional": "Duygusal derinlik ekle, karakterlerin hislerini detaylandır",
            "dialogue": "Daha fazla diyalog ekle, karakterlerin konuşmalarını genişlet",
            "action": "Aksiyon sahnelerini detaylandır, hareketleri betimle",
            "setting": "Mekan betimlemelerini zenginleştir, atmosfer yarat"
        }
        
        prompt = f"""Aşağıdaki hikayeyi zenginleştir. 
{enrichment_prompts.get(enrichment_type, 'Genel olarak zenginleştir')}:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye zenginleştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        enriched_text = response.choices[0].message.content
        
        enrichment = {
            "enrichment_id": enrichment_id,
            "story_id": story_id,
            "enrichment_type": enrichment_type,
            "original_text": story_text,
            "enriched_text": enriched_text,
            "created_at": datetime.now().isoformat()
        }
        
        enrichments = self._load_enrichments()
        enrichments.append(enrichment)
        self._save_enrichments(enrichments)
        
        return {
            "enrichment_id": enrichment_id,
            "enriched_text": enriched_text,
            "improvement_percentage": round(
                ((len(enriched_text) - len(story_text)) / len(story_text)) * 100, 2
            ) if story_text else 0
        }
    
    async def add_sensory_details(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Duyusal detaylar ekler."""
        prompt = f"""Aşağıdaki hikayeye duyusal detaylar ekle (görme, işitme, dokunma, koku, tat):

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir duyusal betimleme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        enriched_text = response.choices[0].message.content
        
        return {
            "story_id": story_id,
            "enriched_text": enriched_text,
            "enrichment_type": "sensory"
        }
    
    def _load_enrichments(self) -> List[Dict]:
        """Zenginleştirmeleri yükler."""
        try:
            with open(self.enrichments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_enrichments(self, enrichments: List[Dict]):
        """Zenginleştirmeleri kaydeder."""
        with open(self.enrichments_file, 'w', encoding='utf-8') as f:
            json.dump(enrichments, f, ensure_ascii=False, indent=2)

