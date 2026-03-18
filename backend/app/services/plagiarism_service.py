from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json
from difflib import SequenceMatcher


class PlagiarismService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
    
    async def check_plagiarism(
        self,
        story_text: str,
        story_id: Optional[str] = None
    ) -> Dict:
        """
        İntihal kontrolü yapar.
        
        Args:
            story_text: Kontrol edilecek hikâye metni
            story_id: Hikâye ID'si (kendisi hariç tutulur)
        
        Returns:
            İntihal kontrolü sonuçları
        """
        all_stories = self.story_storage.get_all_stories()
        
        similarities = []
        
        for story in all_stories:
            if story.get('story_id') == story_id:
                continue
            
            other_text = story.get('story_text', '')
            similarity = self._calculate_similarity(story_text, other_text)
            
            if similarity > 0.3:  # %30'dan fazla benzerlik
                similarities.append({
                    "story_id": story.get('story_id'),
                    "theme": story.get('theme'),
                    "similarity": round(similarity * 100, 2),
                    "similarity_score": similarity
                })
        
        # Benzerliğe göre sırala
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Orijinallik skoru
        originality_score = 100 - (similarities[0]['similarity'] if similarities else 0)
        
        return {
            "originality_score": round(originality_score, 2),
            "similar_stories": similarities[:5],  # En benzer 5 hikâye
            "total_comparisons": len(all_stories) - (1 if story_id else 0),
            "is_original": originality_score >= 70
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """İki metin arasındaki benzerliği hesaplar."""
        if not text1 or not text2:
            return 0.0
        
        # Basit benzerlik (SequenceMatcher)
        similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # Kelime bazlı benzerlik
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        word_similarity = len(words1 & words2) / len(words1 | words2)
        
        # Kombine benzerlik
        combined_similarity = (similarity * 0.6) + (word_similarity * 0.4)
        
        return combined_similarity
    
    async def check_with_ai(
        self,
        story_text: str
    ) -> Dict:
        """
        AI ile daha gelişmiş intihal kontrolü.
        """
        prompt = f"""
Aşağıdaki metni analiz et ve orijinallik değerlendirmesi yap. Bu metin başka bir kaynaktan kopyalanmış olabilir mi?

Metin:
{story_text[:1000]}  # İlk 1000 karakter

JSON formatında döndür:
{{
  "originality_assessment": "high/medium/low",
  "potential_sources": ["kaynak1", "kaynak2"],
  "similarity_indicators": ["gösterge1", "gösterge2"],
  "recommendations": ["öneri1", "öneri2"]
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir intihal tespit uzmanısın. Metinlerin orijinalliğini değerlendiriyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            assessment_text = response.choices[0].message.content
            
            if "```json" in assessment_text:
                assessment_text = assessment_text.split("```json")[1].split("```")[0].strip()
            elif "```" in assessment_text:
                assessment_text = assessment_text.split("```")[1].split("```")[0].strip()
            
            assessment = json.loads(assessment_text)
            
            return {
                "originality_assessment": assessment.get('originality_assessment', 'medium'),
                "potential_sources": assessment.get('potential_sources', []),
                "similarity_indicators": assessment.get('similarity_indicators', []),
                "recommendations": assessment.get('recommendations', []),
                "ai_checked": True
            }
        
        except Exception as e:
            print(f"AI intihal kontrolü hatası: {e}")
            return {
                "originality_assessment": "unknown",
                "potential_sources": [],
                "similarity_indicators": [],
                "recommendations": ["AI kontrolü yapılamadı, manuel kontrol önerilir"],
                "ai_checked": False,
                "error": str(e)
            }
    
    def get_originality_report(
        self,
        story_id: str
    ) -> Dict:
        """
        Orijinallik raporu oluşturur.
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        
        # Basit intihal kontrolü
        plagiarism_check = self.check_plagiarism(story_text, story_id)
        
        return {
            "story_id": story_id,
            "originality_score": plagiarism_check.get('originality_score', 100),
            "is_original": plagiarism_check.get('is_original', True),
            "similar_stories_count": len(plagiarism_check.get('similar_stories', [])),
            "top_similar_story": plagiarism_check.get('similar_stories', [])[0] if plagiarism_check.get('similar_stories') else None,
            "recommendations": [
                "Orijinallik skorunuz yüksek" if plagiarism_check.get('originality_score', 0) >= 80 else "Metni daha özgün hale getirmeyi düşünün"
            ]
        }

