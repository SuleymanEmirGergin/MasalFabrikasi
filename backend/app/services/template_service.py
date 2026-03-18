import json
import os
from typing import List, Dict, Optional
from pathlib import Path
from app.core.config import settings


class TemplateService:
    def __init__(self):
        self.templates_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'story_templates.json'
        )
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Şablonları yükler."""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"templates": [], "categories": []}
    
    def get_all_templates(self, category: Optional[str] = None) -> List[Dict]:
        """Tüm şablonları getirir."""
        templates = self.templates.get('templates', [])
        
        if category and category != 'all':
            templates = [t for t in templates if t.get('category') == category]
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Belirli bir şablonu getirir."""
        templates = self.templates.get('templates', [])
        return next((t for t in templates if t.get('id') == template_id), None)
    
    def get_categories(self) -> List[Dict]:
        """Kategorileri getirir."""
        return self.templates.get('categories', [])
    
    def get_templates_by_type(self, story_type: str) -> List[Dict]:
        """Belirli bir türdeki şablonları getirir."""
        templates = self.templates.get('templates', [])
        return [t for t in templates if t.get('story_type') == story_type]
    
    def create_custom_template(
        self,
        user_id: str,
        template_name: str,
        template_structure: Dict,
        category: str = "custom"
    ) -> Dict:
        """
        Özel şablon oluşturur.
        
        Args:
            user_id: Kullanıcı ID'si
            template_name: Şablon adı
            template_structure: Şablon yapısı
            category: Kategori
        
        Returns:
            Şablon objesi
        """
        import uuid
        from datetime import datetime
        
        custom_templates_file = os.path.join(settings.STORAGE_PATH, "custom_templates.json")
        
        try:
            with open(custom_templates_file, 'r', encoding='utf-8') as f:
                custom_templates = json.load(f)
        except:
            custom_templates = []
        
        template = {
            "template_id": str(uuid.uuid4()),
            "user_id": user_id,
            "template_name": template_name,
            "template_structure": template_structure,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        custom_templates.append(template)
        
        with open(custom_templates_file, 'w', encoding='utf-8') as f:
            json.dump(custom_templates, f, ensure_ascii=False, indent=2)
        
        return template
    
    def get_user_templates(self, user_id: str) -> List[Dict]:
        """Kullanıcının özel şablonlarını getirir."""
        custom_templates_file = os.path.join(settings.STORAGE_PATH, "custom_templates.json")
        
        try:
            with open(custom_templates_file, 'r', encoding='utf-8') as f:
                custom_templates = json.load(f)
            return [t for t in custom_templates if t.get('user_id') == user_id]
        except:
            return []
    
    def share_template(self, template_id: str, user_id: str) -> bool:
        """Şablonu paylaşır (topluluk şablonlarına ekler)."""
        custom_templates_file = os.path.join(settings.STORAGE_PATH, "custom_templates.json")
        
        try:
            with open(custom_templates_file, 'r', encoding='utf-8') as f:
                custom_templates = json.load(f)
            
            template = next((t for t in custom_templates if t.get('template_id') == template_id), None)
            if not template or template.get('user_id') != user_id:
                return False
            
            # Topluluk şablonlarına ekle (basit implementasyon)
            template['is_shared'] = True
            template['shared_at'] = datetime.now().isoformat()
            
            with open(custom_templates_file, 'w', encoding='utf-8') as f:
                json.dump(custom_templates, f, ensure_ascii=False, indent=2)
            
            return True
        except:
            return False

