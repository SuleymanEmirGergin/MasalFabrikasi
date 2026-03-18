from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentSplitterService:
    """Hikaye içerik bölme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.splits_file = os.path.join(settings.STORAGE_PATH, "content_splits.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.splits_file):
            with open(self.splits_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def split_into_chapters(
        self,
        story_id: str,
        story_text: str,
        num_chapters: int = 3
    ) -> Dict:
        """Hikayeyi bölümlere ayırır."""
        split_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi {num_chapters} bölüme ayır.
Her bölüm bağımsız ama birbirine bağlı olsun:

{story_text}

Her bölüm için başlık ve içerik ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye bölme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000
        )
        
        chapters_text = response.choices[0].message.content
        
        # Bölümleri parse et
        chapters = self._parse_chapters(chapters_text, num_chapters)
        
        split = {
            "split_id": split_id,
            "story_id": story_id,
            "chapters": chapters,
            "num_chapters": len(chapters),
            "created_at": datetime.now().isoformat()
        }
        
        splits = self._load_splits()
        splits.append(split)
        self._save_splits(splits)
        
        return {
            "split_id": split_id,
            "chapters": chapters,
            "chapters_count": len(chapters)
        }
    
    async def split_by_scenes(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikayeyi sahnelerine ayırır."""
        split_id = str(uuid.uuid4())
        
        # Basit sahne bölme
        paragraphs = story_text.split('\n\n')
        scenes = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                scenes.append({
                    "scene_number": i + 1,
                    "title": f"Sahne {i + 1}",
                    "content": paragraph.strip()
                })
        
        if not scenes:
            # Paragraf yoksa cümlelere böl
            sentences = story_text.split('.')
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    scenes.append({
                        "scene_number": i + 1,
                        "title": f"Sahne {i + 1}",
                        "content": sentence.strip() + '.'
                    })
        
        split = {
            "split_id": split_id,
            "story_id": story_id,
            "scenes": scenes[:20],  # Maksimum 20 sahne
            "created_at": datetime.now().isoformat()
        }
        
        splits = self._load_splits()
        splits.append(split)
        self._save_splits(splits)
        
        return {
            "split_id": split_id,
            "scenes": split["scenes"],
            "scenes_count": len(split["scenes"])
        }
    
    def _parse_chapters(self, chapters_text: str, num_chapters: int) -> List[Dict]:
        """Bölümleri parse eder."""
        chapters = []
        lines = chapters_text.split('\n')
        
        current_chapter = None
        for line in lines:
            if line.strip() and ('Bölüm' in line or 'Chapter' in line or line[0].isdigit()):
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {
                    "chapter_number": len(chapters) + 1,
                    "title": line.strip(),
                    "content": ""
                }
            elif current_chapter and line.strip():
                current_chapter["content"] += line.strip() + " "
        
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters[:num_chapters] if chapters else [
            {"chapter_number": i+1, "title": f"Bölüm {i+1}", "content": ""}
            for i in range(num_chapters)
        ]
    
    def _load_splits(self) -> List[Dict]:
        """Bölmeleri yükler."""
        try:
            with open(self.splits_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_splits(self, splits: List[Dict]):
        """Bölmeleri kaydeder."""
        with open(self.splits_file, 'w', encoding='utf-8') as f:
            json.dump(splits, f, ensure_ascii=False, indent=2)

