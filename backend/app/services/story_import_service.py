from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage
import re


class StoryImportService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.import_path = os.path.join(settings.STORAGE_PATH, "imports")
        os.makedirs(self.import_path, exist_ok=True)
    
    def import_from_file(
        self,
        file_path: str,
        user_id: str,
        file_format: str = "auto"
    ) -> Dict:
        """Dosyadan içe aktarır."""
        if not os.path.exists(file_path):
            raise ValueError("Dosya bulunamadı")
        
        # Format algılama
        if file_format == "auto":
            file_format = self._detect_format(file_path)
        
        # İçe aktarma
        if file_format == "json":
            return self._import_from_json(file_path, user_id)
        elif file_format == "txt":
            return self._import_from_txt(file_path, user_id)
        elif file_format == "markdown":
            return self._import_from_markdown(file_path, user_id)
        else:
            raise ValueError(f"Desteklenmeyen format: {file_format}")
    
    def _detect_format(self, file_path: str) -> str:
        """Dosya formatını algılar."""
        ext = os.path.splitext(file_path)[1].lower()
        format_map = {
            ".json": "json",
            ".txt": "txt",
            ".md": "markdown",
            ".markdown": "markdown"
        }
        return format_map.get(ext, "txt")
    
    def _import_from_json(
        self,
        file_path: str,
        user_id: str
    ) -> Dict:
        """JSON'dan içe aktarır."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            stories = []
            for item in data:
                story = self._create_story_from_data(item, user_id)
                self.story_storage.save_story(story)
                stories.append(story)
            return {"imported_count": len(stories), "stories": stories}
        else:
            story = self._create_story_from_data(data, user_id)
            self.story_storage.save_story(story)
            return {"imported_count": 1, "story": story}
    
    def _import_from_txt(
        self,
        file_path: str,
        user_id: str
    ) -> Dict:
        """TXT'den içe aktarır."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basit parsing - başlık ve içerik
        lines = content.split('\n')
        title = lines[0] if lines else "İçe Aktarılan Hikâye"
        text = '\n'.join(lines[1:]) if len(lines) > 1 else content
        
        story = {
            "story_id": str(uuid.uuid4()),
            "theme": title,
            "story_text": text,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "language": "tr",
            "story_type": "masal"
        }
        
        self.story_storage.save_story(story)
        return {"imported_count": 1, "story": story}
    
    def _import_from_markdown(
        self,
        file_path: str,
        user_id: str
    ) -> Dict:
        """Markdown'dan içe aktarır."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basit markdown parsing
        lines = content.split('\n')
        title = ""
        text_lines = []
        
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
            else:
                text_lines.append(line)
        
        story = {
            "story_id": str(uuid.uuid4()),
            "theme": title or "İçe Aktarılan Hikâye",
            "story_text": '\n'.join(text_lines),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "language": "tr",
            "story_type": "masal"
        }
        
        self.story_storage.save_story(story)
        return {"imported_count": 1, "story": story}
    
    def _create_story_from_data(
        self,
        data: Dict,
        user_id: str
    ) -> Dict:
        """Veriden hikâye oluşturur."""
        return {
            "story_id": str(uuid.uuid4()),
            "theme": data.get('theme') or data.get('title') or "İçe Aktarılan Hikâye",
            "story_text": data.get('story_text') or data.get('content') or data.get('text', ''),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "language": data.get('language', 'tr'),
            "story_type": data.get('story_type', 'masal')
        }
    
    def import_from_url(
        self,
        url: str,
        user_id: str
    ) -> Dict:
        """URL'den içe aktarır."""
        # Placeholder - gerçek implementasyon için HTTP isteği gerekli
        return {
            "error": "URL'den içe aktarma henüz desteklenmiyor",
            "url": url
        }
    
    def batch_import(
        self,
        file_paths: List[str],
        user_id: str
    ) -> Dict:
        """Toplu içe aktarma."""
        results = []
        for file_path in file_paths:
            try:
                result = self.import_from_file(file_path, user_id)
                results.append(result)
            except Exception as e:
                results.append({"file_path": file_path, "error": str(e)})
        
        return {
            "total": len(file_paths),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }

