from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryTemplatesShortcutsService:
    """Hikaye şablon ve kısayollar servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.templates_file = os.path.join(settings.STORAGE_PATH, "story_templates_shortcuts.json")
        self.shortcuts_file = os.path.join(settings.STORAGE_PATH, "story_shortcuts.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.templates_file):
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.shortcuts_file):
            with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def create_template(
        self,
        template_name: str,
        template_structure: Dict,
        category: str = "general",
        description: Optional[str] = None
    ) -> Dict:
        """Şablon oluşturur."""
        template_id = str(uuid.uuid4())
        
        template = {
            "template_id": template_id,
            "name": template_name,
            "description": description,
            "category": category,
            "structure": template_structure,
            "usage_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        templates = self._load_templates()
        templates.append(template)
        self._save_templates(templates)
        
        return {
            "template_id": template_id,
            "name": template_name,
            "message": "Şablon oluşturuldu"
        }
    
    async def use_template(
        self,
        template_id: str,
        user_inputs: Dict
    ) -> Dict:
        """Şablonu kullanarak hikaye oluşturur."""
        templates = self._load_templates()
        template = next((t for t in templates if t["template_id"] == template_id), None)
        
        if not template:
            raise ValueError("Şablon bulunamadı")
        
        # Şablon yapısını kullanıcı girdileriyle doldur
        story_text = self._fill_template(template["structure"], user_inputs)
        
        # Kullanım sayısını artır
        template["usage_count"] += 1
        template["last_used_at"] = datetime.now().isoformat()
        self._save_templates(templates)
        
        return {
            "template_id": template_id,
            "story_text": story_text,
            "message": "Şablon kullanıldı"
        }
    
    async def create_shortcut(
        self,
        user_id: str,
        shortcut_key: str,
        shortcut_action: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Kısayol oluşturur."""
        shortcut_id = str(uuid.uuid4())
        
        shortcut = {
            "shortcut_id": shortcut_id,
            "user_id": user_id,
            "key": shortcut_key,
            "action": shortcut_action,
            "parameters": parameters or {},
            "created_at": datetime.now().isoformat()
        }
        
        shortcuts = self._load_shortcuts()
        if user_id not in shortcuts:
            shortcuts[user_id] = []
        shortcuts[user_id].append(shortcut)
        self._save_shortcuts(shortcuts)
        
        return {
            "shortcut_id": shortcut_id,
            "key": shortcut_key,
            "message": "Kısayol oluşturuldu"
        }
    
    async def execute_shortcut(
        self,
        user_id: str,
        shortcut_key: str
    ) -> Dict:
        """Kısayolu çalıştırır."""
        shortcuts = self._load_shortcuts()
        user_shortcuts = shortcuts.get(user_id, [])
        
        shortcut = next((s for s in user_shortcuts if s["key"] == shortcut_key), None)
        
        if not shortcut:
            raise ValueError("Kısayol bulunamadı")
        
        return {
            "action": shortcut["action"],
            "parameters": shortcut["parameters"],
            "message": "Kısayol çalıştırıldı"
        }
    
    def _fill_template(self, structure: Dict, inputs: Dict) -> str:
        """Şablonu doldurur."""
        # Basit şablon doldurma
        story_parts = []
        
        if "beginning" in structure:
            beginning = structure["beginning"].format(**inputs)
            story_parts.append(beginning)
        
        if "middle" in structure:
            middle = structure["middle"].format(**inputs)
            story_parts.append(middle)
        
        if "ending" in structure:
            ending = structure["ending"].format(**inputs)
            story_parts.append(ending)
        
        return " ".join(story_parts)
    
    async def get_popular_templates(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """Popüler şablonları getirir."""
        templates = self._load_templates()
        
        # Kullanım sayısına göre sırala
        templates.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        
        return templates[:limit]
    
    def _load_templates(self) -> List[Dict]:
        """Şablonları yükler."""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_templates(self, templates: List[Dict]):
        """Şablonları kaydeder."""
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
    
    def _load_shortcuts(self) -> Dict:
        """Kısayolları yükler."""
        try:
            with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_shortcuts(self, shortcuts: Dict):
        """Kısayolları kaydeder."""
        with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
            json.dump(shortcuts, f, ensure_ascii=False, indent=2)

