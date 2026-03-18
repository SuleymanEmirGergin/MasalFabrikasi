from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import re


class AIEditorService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    
    async def realtime_spell_check(self, text: str, language: str = "tr") -> Dict:
        """Gerçek zamanlı yazım kontrolü."""
        prompt = f"""
Aşağıdaki metindeki yazım hatalarını bul ve düzelt. JSON formatında döndür.

Metin:
{text}

Dil: {language}

JSON formatında döndür:
{{
  "errors": [
    {{
      "word": "yanlış_kelime",
      "position": 10,
      "suggestion": "doğru_kelime",
      "type": "spelling/grammar"
    }}
  ],
  "corrected_text": "Düzeltilmiş metin"
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir yazım kontrol uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
        except:
            return {"errors": [], "corrected_text": text}
    
    async def get_style_suggestions(self, text: str) -> List[Dict]:
        """Stil önerileri getirir."""
        prompt = f"""
Aşağıdaki metne stil önerileri sun. JSON formatında döndür.

Metin:
{text}

JSON formatında döndür:
{{
  "suggestions": [
    {{
      "type": "vocabulary/sentence_structure/clarity",
      "original": "Orijinal cümle",
      "suggestion": "Önerilen cümle",
      "reason": "Neden önerildi"
    }}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat editörüsün."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result.get('suggestions', [])
        except:
            return []
    
    async def auto_correct(self, text: str, corrections: List[Dict]) -> str:
        """Otomatik düzeltmeleri uygular."""
        corrected = text
        for correction in sorted(corrections, key=lambda x: x.get('position', 0), reverse=True):
            original = correction.get('original', '')
            suggestion = correction.get('suggestion', '')
            if original and suggestion:
                corrected = corrected.replace(original, suggestion, 1)
        return corrected
    
    def calculate_readability_score(self, text: str) -> Dict:
        """Okunabilirlik skoru hesaplar."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        # Basit okunabilirlik skoru (0-100)
        readability = 100 - (avg_sentence_length * 2) - (avg_word_length * 5)
        readability = max(0, min(100, readability))
        
        return {
            "score": round(readability, 2),
            "level": "kolay" if readability > 70 else "orta" if readability > 40 else "zor",
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_word_length": round(avg_word_length, 1)
        }

