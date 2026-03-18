from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import re


class AIEditorEnhancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    
    async def realtime_spell_check(
        self,
        text: str,
        language: str = "tr"
    ) -> List[Dict]:
        """Gerçek zamanlı yazım kontrolü."""
        # Basit yazım kontrolü (gerçek uygulamada daha gelişmiş olabilir)
        words = text.split()
        suggestions = []
        
        # Yaygın hatalar için kontrol
        common_errors = {
            "ki": "ki",
            "de": "de",
            "da": "da"
        }
        
        for i, word in enumerate(words):
            word_clean = word.strip('.,!?;:"()[]{}')
            if word_clean.lower() in common_errors:
                suggestions.append({
                    "word": word,
                    "position": i,
                    "suggestion": common_errors[word_clean.lower()],
                    "type": "spelling"
                })
        
        return suggestions
    
    async def auto_correct(
        self,
        text: str,
        corrections: List[Dict]
    ) -> str:
        """Otomatik düzeltme yapar."""
        corrected_text = text
        for correction in sorted(corrections, key=lambda x: x.get('position', 0), reverse=True):
            pos = correction.get('position', 0)
            words = corrected_text.split()
            if 0 <= pos < len(words):
                words[pos] = correction.get('suggestion', words[pos])
                corrected_text = ' '.join(words)
        return corrected_text
    
    async def get_style_suggestions(
        self,
        text: str,
        language: str = "tr"
    ) -> List[Dict]:
        """Stil önerileri getirir."""
        prompt = f"""
Aşağıdaki metni analiz et ve stil önerileri sun.

Metin:
{text}

JSON formatında döndür:
{{
  "suggestions": [
    {{
      "type": "vocabulary/sentence_structure/clarity",
      "original": "Orijinal metin",
      "suggested": "Önerilen metin",
      "reason": "Neden önerildi"
    }}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat editörüsün. Stil önerileri sunuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result.get('suggestions', [])
        except:
            return []
    
    async def calculate_readability_score(
        self,
        text: str,
        language: str = "tr"
    ) -> Dict:
        """Okunabilirlik skoru hesaplar."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        avg_words_per_sentence = len(words) / max(len([s for s in sentences if s.strip()]), 1)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Basit okunabilirlik skoru (0-100)
        readability = 100 - (avg_words_per_sentence * 2) - (avg_word_length * 5)
        readability = max(0, min(100, readability))
        
        return {
            "score": round(readability, 1),
            "level": self._get_readability_level(readability),
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "avg_word_length": round(avg_word_length, 1)
        }
    
    def _get_readability_level(self, score: float) -> str:
        """Okunabilirlik seviyesi belirler."""
        if score >= 80:
            return "Çok Kolay"
        elif score >= 60:
            return "Kolay"
        elif score >= 40:
            return "Orta"
        elif score >= 20:
            return "Zor"
        else:
            return "Çok Zor"

