from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryAutoCategorizationService:
    """Hikaye otomatik kategorizasyon servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.categories_file = os.path.join(settings.STORAGE_PATH, "story_categories.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.categories_file):
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def categorize_story(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikayeyi otomatik kategorize eder."""
        prompt = f"""Aşağıdaki hikayeyi kategorize et. 
Ana kategori, alt kategori, yaş grubu ve temaları belirle:

{story_text}

JSON formatında döndür."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik kategorizasyon uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        categorization_text = response.choices[0].message.content
        
        # Basit parse
        categories = self._extract_categories(categorization_text, story_text)
        
        category_record = {
            "category_id": str(uuid.uuid4()),
            "story_id": story_id,
            "categories": categories,
            "confidence": 0.85,
            "created_at": datetime.now().isoformat()
        }
        
        categories_list = self._load_categories()
        categories_list.append(category_record)
        self._save_categories(categories_list)
        
        return {
            "story_id": story_id,
            "categories": categories,
            "confidence": category_record["confidence"]
        }
    
    def _extract_categories(self, categorization_text: str, story_text: str) -> Dict:
        """Kategorileri çıkarır."""
        categories = {
            "main_category": "genel",
            "sub_category": "masal",
            "age_group": "çocuk",
            "themes": []
        }
        
        # Basit kategori tespiti
        story_lower = story_text.lower()
        
        # Ana kategori
        if any(word in story_lower for word in ["masal", "peri", "büyü"]):
            categories["main_category"] = "fantastik"
        elif any(word in story_lower for word in ["macera", "yolculuk", "keşif"]):
            categories["main_category"] = "macera"
        elif any(word in story_lower for word in ["hayvan", "doğa", "orman"]):
            categories["main_category"] = "doğa"
        else:
            categories["main_category"] = "genel"
        
        # Temalar
        theme_keywords = {
            "arkadaşlık": ["arkadaş", "dost", "birlik"],
            "cesaret": ["cesur", "korku", "mücadele"],
            "sevgi": ["sevgi", "aşk", "kalp"],
            "eğitim": ["öğren", "okul", "bilgi"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in story_lower for keyword in keywords):
                categories["themes"].append(theme)
        
        return categories
    
    async def get_similar_stories(
        self,
        story_id: str,
        limit: int = 5
    ) -> List[str]:
        """Benzer hikayeleri getirir."""
        categories_list = self._load_categories()
        story_categories = next(
            (c for c in categories_list if c["story_id"] == story_id),
            None
        )
        
        if not story_categories:
            return []
        
        # Aynı kategorideki hikayeleri bul
        similar = [
            c["story_id"] for c in categories_list
            if c["story_id"] != story_id
            and c["categories"]["main_category"] == story_categories["categories"]["main_category"]
        ]
        
        return similar[:limit]
    
    def _load_categories(self) -> List[Dict]:
        """Kategorileri yükler."""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_categories(self, categories: List[Dict]):
        """Kategorileri kaydeder."""
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)

