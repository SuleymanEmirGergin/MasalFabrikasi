from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryAutoTitleService:
    """Hikaye otomatik başlık önerileri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.titles_file = os.path.join(settings.STORAGE_PATH, "story_titles.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.titles_file):
            with open(self.titles_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def generate_titles(
        self,
        story_id: str,
        story_text: str,
        num_titles: int = 5,
        title_style: str = "creative"
    ) -> Dict:
        """Başlık önerileri oluşturur."""
        title_id = str(uuid.uuid4())
        
        style_instructions = {
            "creative": "Yaratıcı ve ilgi çekici başlıklar",
            "descriptive": "Açıklayıcı ve bilgilendirici başlıklar",
            "short": "Kısa ve öz başlıklar",
            "poetic": "Şiirsel ve duygusal başlıklar",
            "mysterious": "Gizemli ve merak uyandıran başlıklar"
        }
        
        prompt = f"""Aşağıdaki hikaye için {num_titles} adet {style_instructions.get(title_style, 'yaratıcı')} başlık öner:

{story_text}

Her başlık farklı bir açıdan yaklaşsın."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir başlık yazım uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )
        
        titles_text = response.choices[0].message.content
        
        # Başlıkları parse et
        titles = self._parse_titles(titles_text, num_titles)
        
        title_record = {
            "title_id": title_id,
            "story_id": story_id,
            "titles": titles,
            "title_style": title_style,
            "created_at": datetime.now().isoformat()
        }
        
        titles_list = self._load_titles()
        titles_list.append(title_record)
        self._save_titles(titles_list)
        
        return {
            "title_id": title_id,
            "titles": titles,
            "titles_count": len(titles)
        }
    
    async def optimize_title(
        self,
        current_title: str,
        story_text: str
    ) -> Dict:
        """Mevcut başlığı optimize eder."""
        prompt = f"""Aşağıdaki başlığı hikayeye daha uygun ve etkili hale getir:

Mevcut başlık: {current_title}

Hikaye:
{story_text[:500]}

3 farklı optimize edilmiş versiyon öner."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir başlık optimizasyon uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        optimized_titles = response.choices[0].message.content
        titles = self._parse_titles(optimized_titles, 3)
        
        return {
            "original_title": current_title,
            "optimized_titles": titles
        }
    
    def _parse_titles(self, titles_text: str, num_titles: int) -> List[str]:
        """Başlıkları parse eder."""
        titles = []
        lines = titles_text.split('\n')
        
        for line in lines:
            if line.strip() and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                title = line.strip().lstrip('1234567890.-• ').strip()
                if title and len(title) < 100:
                    titles.append(title)
        
        return titles[:num_titles] if titles else ["Başlıksız Hikaye"]
    
    def _load_titles(self) -> List[Dict]:
        """Başlıkları yükler."""
        try:
            with open(self.titles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_titles(self, titles: List[Dict]):
        """Başlıkları kaydeder."""
        with open(self.titles_file, 'w', encoding='utf-8') as f:
            json.dump(titles, f, ensure_ascii=False, indent=2)

