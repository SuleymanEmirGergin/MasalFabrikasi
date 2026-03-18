from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentVerificationService:
    """Hikaye içerik doğrulama servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.verifications_file = os.path.join(settings.STORAGE_PATH, "content_verifications.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.verifications_file):
            with open(self.verifications_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def verify_content(
        self,
        story_id: str,
        story_text: str,
        verification_type: str = "comprehensive"
    ) -> Dict:
        """İçeriği doğrular."""
        verification_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi doğrula:
1. Dilbilgisi hataları
2. Tutarlılık kontrolü
3. Mantık hataları
4. Çocuklar için uygunluk

Hikaye:
{story_text}

Her kontrol için sonuç ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir içerik doğrulama uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        verification_result = response.choices[0].message.content
        
        # Basit doğrulama skorları
        checks = {
            "grammar": self._check_grammar(story_text),
            "consistency": self._check_consistency(story_text),
            "logic": self._check_logic(story_text),
            "age_appropriateness": self._check_age_appropriateness(story_text)
        }
        
        overall_score = sum(checks.values()) / len(checks)
        
        verification = {
            "verification_id": verification_id,
            "story_id": story_id,
            "verification_type": verification_type,
            "verification_result": verification_result,
            "checks": checks,
            "overall_score": overall_score,
            "is_verified": overall_score >= 0.7,
            "created_at": datetime.now().isoformat()
        }
        
        verifications = self._load_verifications()
        verifications.append(verification)
        self._save_verifications(verifications)
        
        return verification
    
    def _check_grammar(self, text: str) -> float:
        """Dilbilgisi kontrolü."""
        # Basit kontrol
        common_errors = ["ki", "de", "da"]
        error_count = sum(1 for error in common_errors if error in text.lower())
        return max(0.0, 1.0 - (error_count * 0.1))
    
    def _check_consistency(self, text: str) -> float:
        """Tutarlılık kontrolü."""
        # Basit kontrol - karakter isimlerinin tutarlılığı
        words = text.split()
        capitalized_words = [w for w in words if w and w[0].isupper()]
        unique_caps = len(set(capitalized_words))
        
        if unique_caps > 0:
            return min(1.0, 0.8 + (1.0 / unique_caps))
        return 0.7
    
    def _check_logic(self, text: str) -> float:
        """Mantık kontrolü."""
        # Basit kontrol
        logical_indicators = ["çünkü", "böylece", "sonra", "önce"]
        indicator_count = sum(1 for indicator in logical_indicators if indicator in text.lower())
        return min(1.0, 0.6 + (indicator_count * 0.1))
    
    def _check_age_appropriateness(self, text: str) -> float:
        """Yaş uygunluğu kontrolü."""
        inappropriate_words = ["şiddet", "korku", "ölüm"]
        inappropriate_count = sum(1 for word in inappropriate_words if word in text.lower())
        return max(0.0, 1.0 - (inappropriate_count * 0.3))
    
    def _load_verifications(self) -> List[Dict]:
        """Doğrulamaları yükler."""
        try:
            with open(self.verifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_verifications(self, verifications: List[Dict]):
        """Doğrulamaları kaydeder."""
        with open(self.verifications_file, 'w', encoding='utf-8') as f:
            json.dump(verifications, f, ensure_ascii=False, indent=2)

