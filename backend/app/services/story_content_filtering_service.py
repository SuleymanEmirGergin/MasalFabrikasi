from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentFilteringService:
    """Hikaye içerik filtreleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.filters_file = os.path.join(settings.STORAGE_PATH, "content_filters.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.filters_file):
            with open(self.filters_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def filter_content(
        self,
        story_text: str,
        filter_level: str = "moderate",  # "strict", "moderate", "lenient"
        age_group: str = "children"
    ) -> Dict:
        """İçeriği filtreler."""
        filter_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi {age_group} yaş grubu için {filter_level} seviyede kontrol et.
Uygunsuz içerik, şiddet, korku veya zararlı mesajlar var mı kontrol et:

{story_text}

Sadece uygun olup olmadığını ve varsa sorunlu bölümleri belirt."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik moderatörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        filter_result = response.choices[0].message.content
        
        # Basit uygunluk kontrolü
        is_appropriate = "uygun" in filter_result.lower() or "uygundur" in filter_result.lower()
        
        result = {
            "filter_id": filter_id,
            "is_appropriate": is_appropriate,
            "filter_result": filter_result,
            "filter_level": filter_level,
            "age_group": age_group,
            "flagged_sections": self._extract_flagged_sections(filter_result),
            "created_at": datetime.now().isoformat()
        }
        
        filters = self._load_filters()
        filters.append(result)
        self._save_filters(filters)
        
        return result
    
    async def create_safe_version(
        self,
        story_text: str,
        issues: List[str]
    ) -> Dict:
        """Güvenli versiyon oluşturur."""
        prompt = f"""Aşağıdaki hikayeyi çocuklar için güvenli hale getir.
Şu sorunları düzelt: {', '.join(issues)}

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik editörüsün."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        safe_text = response.choices[0].message.content
        
        return {
            "original_text": story_text,
            "safe_text": safe_text,
            "issues_fixed": issues,
            "message": "Güvenli versiyon oluşturuldu"
        }
    
    def _extract_flagged_sections(self, filter_result: str) -> List[str]:
        """İşaretlenen bölümleri çıkarır."""
        # Basit yaklaşım
        flagged = []
        lines = filter_result.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ["sorun", "uygunsuz", "dikkat", "kontrol"]):
                flagged.append(line.strip())
        
        return flagged[:5]  # İlk 5
    
    def _load_filters(self) -> List[Dict]:
        """Filtreleri yükler."""
        try:
            with open(self.filters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_filters(self, filters: List[Dict]):
        """Filtreleri kaydeder."""
        with open(self.filters_file, 'w', encoding='utf-8') as f:
            json.dump(filters, f, ensure_ascii=False, indent=2)

