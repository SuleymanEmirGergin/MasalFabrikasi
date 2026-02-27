from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentMergerService:
    """Hikaye içerik birleştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.mergers_file = os.path.join(settings.STORAGE_PATH, "content_mergers.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.mergers_file):
            with open(self.mergers_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def merge_stories(
        self,
        story_ids: List[str],
        story_texts: List[str],
        merge_style: str = "seamless"
    ) -> Dict:
        """Hikayeleri birleştirir."""
        merger_id = str(uuid.uuid4())
        
        stories_text = "\n\n---\n\n".join([
            f"Hikaye {i+1}:\n{text}" for i, text in enumerate(story_texts)
        ])
        
        style_instructions = {
            "seamless": "Sorunsuz bir şekilde birleştir, geçişleri yumuşak yap",
            "chapter": "Her hikayeyi ayrı bölüm olarak birleştir",
            "parallel": "Paralel hikayeler olarak birleştir",
            "sequential": "Sıralı olarak birleştir"
        }
        
        prompt = f"""Aşağıdaki hikayeleri {style_instructions.get(merge_style, 'birleştir')}:

{stories_text}

Tutarlı ve akıcı bir hikaye oluştur."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye birleştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        merged_text = response.choices[0].message.content
        
        merger = {
            "merger_id": merger_id,
            "story_ids": story_ids,
            "merge_style": merge_style,
            "merged_text": merged_text,
            "created_at": datetime.now().isoformat()
        }
        
        mergers = self._load_mergers()
        mergers.append(merger)
        self._save_mergers(mergers)
        
        return {
            "merger_id": merger_id,
            "merged_text": merged_text,
            "stories_merged": len(story_ids)
        }
    
    async def blend_stories(
        self,
        story1_text: str,
        story2_text: str,
        blend_ratio: float = 0.5
    ) -> Dict:
        """Hikayeleri harmanlar."""
        prompt = f"""Aşağıdaki iki hikayeyi harmanla. 
Her iki hikayenin öğelerini birleştirerek yeni bir hikaye oluştur:

Hikaye 1:
{story1_text}

Hikaye 2:
{story2_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye harmanlama uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        blended_text = response.choices[0].message.content
        
        return {
            "blended_text": blended_text,
            "blend_ratio": blend_ratio,
            "message": "Hikayeler harmanlandı"
        }
    
    def _load_mergers(self) -> List[Dict]:
        """Birleştirmeleri yükler."""
        try:
            with open(self.mergers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_mergers(self, mergers: List[Dict]):
        """Birleştirmeleri kaydeder."""
        with open(self.mergers_file, 'w', encoding='utf-8') as f:
            json.dump(mergers, f, ensure_ascii=False, indent=2)

