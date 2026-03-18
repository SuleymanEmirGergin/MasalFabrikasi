from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_improvement_service import StoryImprovementService
import json


class AIImprovementAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.improvement_service = StoryImprovementService()
    
    async def get_realtime_suggestions(
        self,
        text: str,
        cursor_position: int,
        context: Optional[str] = None
    ) -> List[Dict]:
        """Gerçek zamanlı iyileştirme önerileri getirir."""
        # Cursor pozisyonuna göre cümleyi al
        sentences = text.split('.')
        current_sentence = ""
        for sentence in sentences:
            if len(current_sentence) + len(sentence) < cursor_position:
                current_sentence += sentence + "."
            else:
                current_sentence = sentence
                break
        
        prompt = f"""
Aşağıdaki cümleyi iyileştir. 3 öneri sun.

Cümle: {current_sentence}
Bağlam: {context or 'Genel hikâye'}

JSON formatında döndür:
{{
  "suggestions": [
    {{
      "original": "Orijinal cümle",
      "improved": "İyileştirilmiş cümle",
      "reason": "Neden iyileştirildi",
      "type": "vocabulary/structure/clarity"
    }}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat editörüsün. Gerçek zamanlı öneriler sunuyorsun."},
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
    
    async def auto_improve_section(
        self,
        text: str,
        improvement_type: str = "general"
    ) -> str:
        """Bölümü otomatik iyileştirir."""
        improved = await self.improvement_service.get_improved_version(text, improvement_type, "tr")
        return improved
    
    async def batch_improve(
        self,
        sections: List[str],
        improvement_types: List[str]
    ) -> List[Dict]:
        """Birden fazla bölümü toplu iyileştirir."""
        results = []
        for section, imp_type in zip(sections, improvement_types):
            improved = await self.auto_improve_section(section, imp_type)
            results.append({
                "original": section,
                "improved": improved,
                "type": imp_type
            })
        return results

