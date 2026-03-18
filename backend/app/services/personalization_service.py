from typing import Dict, List, Optional
import json
import os
from app.core.config import settings


class PersonalizationService:
    def __init__(self):
        self.settings_file = os.path.join(settings.STORAGE_PATH, "user_personalization.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Kullanıcı tercihlerini getirir."""
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            all_preferences = json.load(f)
        return all_preferences.get(user_id, self._get_default_preferences())
    
    def _get_default_preferences(self) -> Dict:
        """Varsayılan tercihleri döndürür."""
        return {
            "theme": "light",
            "font_family": "default",
            "font_size": "medium",
            "color_scheme": "default",
            "reading_preferences": {
                "auto_scroll": False,
                "scroll_speed": "medium",
                "highlight_words": False,
                "show_definitions": False
            }
        }
    
    def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict
    ) -> Dict:
        """Kullanıcı tercihlerini günceller."""
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            all_preferences = json.load(f)
        
        if user_id not in all_preferences:
            all_preferences[user_id] = self._get_default_preferences()
        
        all_preferences[user_id].update(preferences)
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(all_preferences, f, ensure_ascii=False, indent=2)
        
        return all_preferences[user_id]
    
    def get_available_themes(self) -> List[Dict]:
        """Mevcut temaları getirir."""
        return [
            {"id": "light", "name": "Açık", "colors": {"bg": "#FFFFFF", "text": "#000000"}},
            {"id": "dark", "name": "Koyu", "colors": {"bg": "#1E1E1E", "text": "#FFFFFF"}},
            {"id": "sepia", "name": "Sepya", "colors": {"bg": "#F4E4BC", "text": "#5C4A37"}},
            {"id": "night", "name": "Gece", "colors": {"bg": "#0A0A0A", "text": "#E0E0E0"}}
        ]
    
    def get_available_fonts(self) -> List[Dict]:
        """Mevcut fontları getirir."""
        return [
            {"id": "default", "name": "Varsayılan", "family": "System Default"},
            {"id": "serif", "name": "Serif", "family": "Times New Roman"},
            {"id": "sans-serif", "name": "Sans Serif", "family": "Arial"},
            {"id": "monospace", "name": "Monospace", "family": "Courier New"},
            {"id": "handwriting", "name": "El Yazısı", "family": "Comic Sans MS"}
        ]
    
    def get_available_color_schemes(self) -> List[Dict]:
        """Mevcut renk şemalarını getirir."""
        return [
            {"id": "default", "name": "Varsayılan", "primary": "#007AFF", "secondary": "#5856D6"},
            {"id": "ocean", "name": "Okyanus", "primary": "#0077BE", "secondary": "#00A8E8"},
            {"id": "forest", "name": "Orman", "primary": "#2D5016", "secondary": "#4A7C59"},
            {"id": "sunset", "name": "Gün Batımı", "primary": "#FF6B35", "secondary": "#F7931E"},
            {"id": "lavender", "name": "Lavanta", "primary": "#9B59B6", "secondary": "#8E44AD"}
        ]

