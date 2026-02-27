from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StorySmartTaggingService:
    """Hikaye akıllı etiketleme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.tags_file = os.path.join(settings.STORAGE_PATH, "story_tags.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.tags_file):
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def auto_tag_story(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikayeyi otomatik etiketler."""
        prompt = f"""Aşağıdaki hikayeyi analiz et ve uygun etiketler öner.
5-10 arası etiket ver:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik etiketleme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=300
        )
        
        tags_text = response.choices[0].message.content
        
        # Etiketleri parse et
        tags = self._extract_tags(tags_text, story_text)
        
        tag_record = {
            "tag_id": str(uuid.uuid4()),
            "story_id": story_id,
            "tags": tags,
            "auto_generated": True,
            "created_at": datetime.now().isoformat()
        }
        
        tags_list = self._load_tags()
        tags_list.append(tag_record)
        self._save_tags(tags_list)
        
        return {
            "story_id": story_id,
            "tags": tags,
            "tags_count": len(tags)
        }
    
    def _extract_tags(self, tags_text: str, story_text: str) -> List[str]:
        """Etiketleri çıkarır."""
        tags = []
        
        # Metinden etiketleri parse et
        lines = tags_text.split('\n')
        for line in lines:
            if line.strip() and (line[0].isdigit() or line.startswith('-') or line.startswith('#')):
                tag = line.strip().lstrip('1234567890.-# ').strip()
                if tag and len(tag) < 30:
                    tags.append(tag)
        
        # Hikayeden otomatik etiket çıkarma
        story_lower = story_text.lower()
        common_tags = {
            "masal": ["masal", "peri", "büyü"],
            "macera": ["macera", "yolculuk", "keşif"],
            "arkadaşlık": ["arkadaş", "dost"],
            "hayvan": ["hayvan", "kedi", "köpek"],
            "doğa": ["orman", "ağaç", "çiçek"]
        }
        
        for tag, keywords in common_tags.items():
            if any(keyword in story_lower for keyword in keywords):
                if tag not in tags:
                    tags.append(tag)
        
        return tags[:15] if tags else ["genel"]
    
    async def suggest_tags(
        self,
        story_text: str,
        existing_tags: Optional[List[str]] = None
    ) -> List[str]:
        """Etiket önerileri."""
        prompt = f"""Aşağıdaki hikaye için etiket öner:
{story_text}

{f"Mevcut etiketler: {', '.join(existing_tags)}" if existing_tags else ""}

5 yeni etiket öner."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir etiket öneri uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        suggestions_text = response.choices[0].message.content
        suggestions = self._extract_tags(suggestions_text, story_text)
        
        return suggestions[:5]
    
    async def get_popular_tags(
        self,
        limit: int = 20
    ) -> List[Dict]:
        """Popüler etiketleri getirir."""
        tags_list = self._load_tags()
        
        # Tüm etiketleri topla
        all_tags = {}
        for tag_record in tags_list:
            for tag in tag_record.get("tags", []):
                all_tags[tag] = all_tags.get(tag, 0) + 1
        
        # Sırala
        popular = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"tag": tag, "count": count}
            for tag, count in popular[:limit]
        ]
    
    def _load_tags(self) -> List[Dict]:
        """Etiketleri yükler."""
        try:
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_tags(self, tags: List[Dict]):
        """Etiketleri kaydeder."""
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(tags, f, ensure_ascii=False, indent=2)

