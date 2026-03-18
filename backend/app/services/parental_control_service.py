from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.story_analysis_service import StoryAnalysisService


class ParentalControlService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.analysis_service = StoryAnalysisService()
        self.settings_file = os.path.join(settings.STORAGE_PATH, "parental_controls.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Ayarlar dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def set_parental_controls(
        self,
        user_id: str,
        child_age: int,
        allowed_themes: Optional[List[str]] = None,
        blocked_themes: Optional[List[str]] = None,
        max_story_length: Optional[int] = None,
        require_approval: bool = False
    ) -> Dict:
        """
        Ebeveyn kontrolü ayarlarını yapar.
        
        Args:
            user_id: Kullanıcı ID'si
            child_age: Çocuk yaşı
            allowed_themes: İzin verilen temalar
            blocked_themes: Engellenen temalar
            max_story_length: Maksimum hikâye uzunluğu (kelime)
            require_approval: Onay gerektir
        
        Returns:
            Ayarlar objesi
        """
        controls = {
            "user_id": user_id,
            "child_age": child_age,
            "allowed_themes": allowed_themes or [],
            "blocked_themes": blocked_themes or [],
            "max_story_length": max_story_length,
            "require_approval": require_approval,
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_controls(user_id, controls)
        return controls
    
    def _save_controls(self, user_id: str, controls: Dict):
        """Kontrolleri kaydeder."""
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            all_controls = json.load(f)
        
        all_controls[user_id] = controls
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(all_controls, f, ensure_ascii=False, indent=2)
    
    def get_parental_controls(self, user_id: str) -> Optional[Dict]:
        """Ebeveyn kontrolü ayarlarını getirir."""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                all_controls = json.load(f)
            return all_controls.get(user_id)
        except:
            return None
    
    async def check_story_appropriateness(
        self,
        story_id: str,
        user_id: str
    ) -> Dict:
        """
        Hikâyenin çocuk için uygun olup olmadığını kontrol eder.
        
        Args:
            story_id: Hikâye ID'si
            user_id: Kullanıcı ID'si
        
        Returns:
            Uygunluk kontrolü sonuçları
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        controls = self.get_parental_controls(user_id)
        if not controls:
            # Kontrol yoksa varsayılan olarak uygun
            return {
                "is_appropriate": True,
                "reason": "Ebeveyn kontrolü ayarlanmamış"
            }
        
        child_age = controls.get('child_age', 10)
        blocked_themes = controls.get('blocked_themes', [])
        allowed_themes = controls.get('allowed_themes', [])
        max_length = controls.get('max_story_length')
        
        # Tema kontrolü
        story_theme = story.get('theme', '').lower()
        
        # Engellenen temalar
        if any(blocked.lower() in story_theme for blocked in blocked_themes):
            return {
                "is_appropriate": False,
                "reason": "Engellenen tema içeriyor",
                "blocked_theme": next((b for b in blocked_themes if b.lower() in story_theme), None)
            }
        
        # İzin verilen temalar (eğer liste varsa)
        if allowed_themes:
            if not any(allowed.lower() in story_theme for allowed in allowed_themes):
                return {
                    "is_appropriate": False,
                    "reason": "İzin verilen temalar listesinde değil"
                }
        
        # Uzunluk kontrolü
        if max_length:
            word_count = len(story.get('story_text', '').split())
            if word_count > max_length:
                return {
                    "is_appropriate": False,
                    "reason": f"Hikâye çok uzun ({word_count} kelime, maksimum {max_length})"
                }
        
        # Yaş uygunluğu kontrolü (AI analizi ile)
        analysis = await self.analysis_service.analyze_story(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        
        recommended_age = analysis.get('recommended_age', '8-10')
        age_range = self._parse_age_range(recommended_age)
        
        if child_age < age_range[0]:
            return {
                "is_appropriate": False,
                "reason": f"Hikâye {age_range[0]}+ yaş için öneriliyor, çocuk {child_age} yaşında",
                "recommended_age": recommended_age
            }
        
        return {
            "is_appropriate": True,
            "reason": "Hikâye uygun",
            "recommended_age": recommended_age
        }
    
    def _parse_age_range(self, age_str: str) -> tuple:
        """Yaş aralığını parse eder (örn: '5-8' -> (5, 8))."""
        try:
            if '-' in age_str:
                parts = age_str.split('-')
                return (int(parts[0]), int(parts[1]))
            elif '+' in age_str:
                return (int(age_str.replace('+', '')), 18)
            else:
                return (8, 10)  # Varsayılan
        except:
            return (8, 10)
    
    def get_filtered_stories(self, user_id: str) -> List[Dict]:
        """
        Kullanıcı için filtrelenmiş hikâyeleri getirir.
        """
        controls = self.get_parental_controls(user_id)
        if not controls:
            # Kontrol yoksa tüm hikâyeler
            return self.story_storage.get_all_stories()
        
        all_stories = self.story_storage.get_all_stories()
        filtered = []
        
        blocked_themes = controls.get('blocked_themes', [])
        allowed_themes = controls.get('allowed_themes', [])
        max_length = controls.get('max_story_length')
        
        for story in all_stories:
            story_theme = story.get('theme', '').lower()
            
            # Engellenen temalar
            if any(blocked.lower() in story_theme for blocked in blocked_themes):
                continue
            
            # İzin verilen temalar
            if allowed_themes:
                if not any(allowed.lower() in story_theme for allowed in allowed_themes):
                    continue
            
            # Uzunluk kontrolü
            if max_length:
                word_count = len(story.get('story_text', '').split())
                if word_count > max_length:
                    continue
            
            filtered.append(story)
        
        return filtered
    
    def get_parent_dashboard(self, user_id: str) -> Dict:
        """
        Ebeveyn dashboard'unu getirir.
        """
        controls = self.get_parental_controls(user_id)
        if not controls:
            return {
                "controls_set": False,
                "message": "Ebeveyn kontrolü ayarlanmamış"
            }
        
        child_age = controls.get('child_age', 10)
        filtered_stories = self.get_filtered_stories(user_id)
        all_stories = self.story_storage.get_all_stories()
        
        return {
            "controls_set": True,
            "child_age": child_age,
            "total_stories": len(all_stories),
            "available_stories": len(filtered_stories),
            "blocked_count": len(all_stories) - len(filtered_stories),
            "settings": controls
        }

