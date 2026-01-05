from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json


class ContentModerationService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    
    async def moderate_content(
        self,
        text: str,
        content_type: str = "story"
    ) -> Dict:
        """
        İçeriği moderasyon kontrolünden geçirir.
        
        Args:
            text: Kontrol edilecek metin
            content_type: İçerik tipi (story, comment, etc.)
        
        Returns:
            Moderasyon sonuçları
        """
        prompt = f"""
Aşağıdaki {content_type} içeriğini analiz et ve uygunsuz içerik kontrolü yap.

İçerik:
{text}

Kontrol etmen gerekenler:
1. Küfür ve hakaret
2. Şiddet içeriği
3. Cinsel içerik
4. Nefret söylemi
5. Spam
6. Yaş uygunluğu

JSON formatında döndür:
{{
  "is_appropriate": true/false,
  "issues": ["sorun1", "sorun2"],
  "severity": "low/medium/high",
  "age_appropriate": "5-7/8-10/11-13/14+",
  "recommendations": ["öneri1", "öneri2"]
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir içerik moderasyon uzmanısın. İçerikleri güvenlik ve uygunluk açısından kontrol ediyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            moderation_text = response.choices[0].message.content
            
            if "```json" in moderation_text:
                moderation_text = moderation_text.split("```json")[1].split("```")[0].strip()
            elif "```" in moderation_text:
                moderation_text = moderation_text.split("```")[1].split("```")[0].strip()
            
            moderation = json.loads(moderation_text)
            
            return {
                "is_appropriate": moderation.get('is_appropriate', True),
                "issues": moderation.get('issues', []),
                "severity": moderation.get('severity', 'low'),
                "age_appropriate": moderation.get('age_appropriate', '8-10'),
                "recommendations": moderation.get('recommendations', []),
                "content_type": content_type
            }
        
        except Exception as e:
            print(f"Moderasyon hatası: {e}")
            # Güvenli tarafta kal
            return {
                "is_appropriate": False,
                "issues": ["Moderasyon kontrolü yapılamadı"],
                "severity": "medium",
                "age_appropriate": "14+",
                "recommendations": ["İçerik manuel kontrol edilmeli"],
                "content_type": content_type,
                "error": str(e)
            }
    
    async def check_age_appropriateness(
        self,
        text: str,
        target_age: int
    ) -> Dict:
        """
        Yaş uygunluğunu kontrol eder.
        
        Args:
            text: Kontrol edilecek metin
            target_age: Hedef yaş
        
        Returns:
            Yaş uygunluk sonuçları
        """
        moderation = await self.moderate_content(text, "story")
        
        age_appropriate = moderation.get('age_appropriate', '8-10')
        age_range = self._parse_age_range(age_appropriate)
        
        is_appropriate = target_age >= age_range[0]
        
        return {
            "target_age": target_age,
            "recommended_age_range": age_appropriate,
            "is_appropriate": is_appropriate,
            "issues": moderation.get('issues', []),
            "recommendations": moderation.get('recommendations', [])
        }
    
    def _parse_age_range(self, age_str: str) -> tuple:
        """Yaş aralığını parse eder."""
        try:
            if '-' in age_str:
                parts = age_str.split('-')
                return (int(parts[0]), int(parts[1]))
            elif '+' in age_str:
                return (int(age_str.replace('+', '')), 18)
            else:
                return (8, 10)
        except:
            return (8, 10)
    
    async def detect_inappropriate_keywords(
        self,
        text: str
    ) -> Dict:
        """
        Uygunsuz anahtar kelimeleri tespit eder.
        """
        # Basit keyword listesi (gerçek uygulamada daha kapsamlı olabilir)
        inappropriate_keywords = [
            # Bu liste gerçek uygulamada daha kapsamlı olmalı
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in inappropriate_keywords if kw in text_lower]
        
        return {
            "found_keywords": found_keywords,
            "keyword_count": len(found_keywords),
            "is_clean": len(found_keywords) == 0
        }
    
    async def suggest_content_improvements(
        self,
        text: str,
        issues: List[str]
    ) -> Dict:
        """
        İçerik iyileştirme önerileri sunar.
        """
        if not issues:
            return {
                "suggestions": [],
                "improved_text": text
            }
        
        prompt = f"""
Aşağıdaki metinde şu sorunlar var: {', '.join(issues)}

Metni bu sorunları gidererek iyileştir. Sadece iyileştirilmiş metni döndür.

Orijinal Metin:
{text}

İyileştirilmiş Metin:
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir içerik editörüsün. Metinleri uygun hale getiriyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            improved_text = response.choices[0].message.content.strip()
            
            return {
                "suggestions": issues,
                "improved_text": improved_text,
                "original_text": text
            }
        
        except Exception as e:
            return {
                "suggestions": issues,
                "improved_text": text,
                "error": str(e)
            }

