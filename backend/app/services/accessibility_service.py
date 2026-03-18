from typing import Dict, Optional
import json
import os
from app.core.config import settings


class AccessibilityService:
    def __init__(self):
        self.settings_file = os.path.join(settings.STORAGE_PATH, "accessibility_settings.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Ayarlar dosyasını oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def get_accessibility_settings(self, user_id: str) -> Dict:
        """Kullanıcının erişilebilirlik ayarlarını getirir."""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
            return all_settings.get(user_id, self._get_default_settings())
        except:
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict:
        """Varsayılan erişilebilirlik ayarları."""
        return {
            "font_size": "medium",  # small, medium, large, xlarge
            "font_family": "default",  # default, dyslexic, sans-serif
            "high_contrast": False,
            "dark_mode": False,
            "screen_reader": False,
            "keyboard_navigation": True,
            "reduce_motion": False,
            "color_blind_mode": None,  # None, protanopia, deuteranopia, tritanopia
            "line_spacing": "normal",  # normal, wide, wider
            "word_spacing": "normal"  # normal, wide
        }
    
    def update_accessibility_settings(self, user_id: str, settings: Dict):
        """Erişilebilirlik ayarlarını günceller."""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
        except:
            all_settings = {}
        
        # Mevcut ayarları güncelle
        if user_id not in all_settings:
            all_settings[user_id] = self._get_default_settings()
        
        all_settings[user_id].update(settings)
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(all_settings, f, ensure_ascii=False, indent=2)
    
    def get_story_accessibility_data(
        self,
        story_text: str,
        settings: Dict
    ) -> Dict:
        """
        Hikâye metnini erişilebilirlik ayarlarına göre formatlar.
        
        Args:
            story_text: Hikâye metni
            settings: Erişilebilirlik ayarları
        
        Returns:
            Formatlanmış hikâye verisi
        """
        # Font boyutu
        font_size_map = {
            "small": "14px",
            "medium": "18px",
            "large": "24px",
            "xlarge": "32px"
        }
        font_size = font_size_map.get(settings.get('font_size', 'medium'), '18px')
        
        # Font ailesi
        font_family_map = {
            "default": "Arial, sans-serif",
            "dyslexic": "OpenDyslexic, Arial, sans-serif",
            "sans-serif": "Arial, Helvetica, sans-serif"
        }
        font_family = font_family_map.get(settings.get('font_family', 'default'), 'Arial, sans-serif')
        
        # Satır aralığı
        line_spacing_map = {
            "normal": "1.5",
            "wide": "2.0",
            "wider": "2.5"
        }
        line_spacing = line_spacing_map.get(settings.get('line_spacing', 'normal'), '1.5')
        
        # Kelime aralığı
        word_spacing = "0.2em" if settings.get('word_spacing') == 'wide' else "normal"
        
        # Renk kontrastı
        text_color = "#000000" if not settings.get('high_contrast') else "#000000"
        bg_color = "#FFFFFF" if not settings.get('dark_mode') else "#1a1a1a"
        
        if settings.get('high_contrast'):
            text_color = "#000000"
            bg_color = "#FFFFFF"
        
        if settings.get('dark_mode'):
            text_color = "#FFFFFF"
            bg_color = "#1a1a1a"
        
        return {
            "formatted_text": story_text,
            "css_styles": {
                "font_size": font_size,
                "font_family": font_family,
                "line_height": line_spacing,
                "word_spacing": word_spacing,
                "color": text_color,
                "background_color": bg_color
            },
            "accessibility_features": {
                "screen_reader_ready": settings.get('screen_reader', False),
                "keyboard_navigation": settings.get('keyboard_navigation', True),
                "reduced_motion": settings.get('reduce_motion', False),
                "color_blind_mode": settings.get('color_blind_mode')
            }
        }
    
    def generate_alt_text_for_image(self, image_url: str, story_context: str) -> str:
        """
        Görsel için alternatif metin oluşturur (AI ile).
        Not: Bu gerçek uygulamada görsel analizi yapılabilir.
        """
        # Basit bir implementasyon - gerçek uygulamada AI görsel analizi kullanılabilir
        return f"Hikâye görseli: {story_context[:50]}..."
    
    def validate_accessibility(self, story_text: str) -> Dict:
        """
        Hikâyenin erişilebilirlik standartlarına uygunluğunu kontrol eder.
        """
        issues = []
        suggestions = []
        
        # Uzun paragraflar kontrolü
        paragraphs = story_text.split('\n\n')
        for i, para in enumerate(paragraphs):
            if len(para) > 500:
                issues.append({
                    "type": "long_paragraph",
                    "paragraph_index": i,
                    "length": len(para),
                    "suggestion": "Paragrafı daha kısa paragraflara bölün"
                })
        
        # Karmaşık cümleler kontrolü
        sentences = story_text.split('.')
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            if len(words) > 25:
                suggestions.append({
                    "type": "complex_sentence",
                    "sentence_index": i,
                    "word_count": len(words),
                    "suggestion": "Cümleyi daha kısa cümlelere bölün"
                })
        
        # Başlık eksikliği kontrolü
        if not any(line.strip().startswith('#') for line in story_text.split('\n')):
            suggestions.append({
                "type": "missing_headings",
                "suggestion": "Hikâyeye başlıklar ekleyin"
            })
        
        return {
            "is_accessible": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "accessibility_score": max(0, 100 - (len(issues) * 10) - (len(suggestions) * 5))
        }

