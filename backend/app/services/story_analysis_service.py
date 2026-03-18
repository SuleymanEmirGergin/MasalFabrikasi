from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import re


class StoryAnalysisService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    
    async def analyze_story(
        self,
        story_text: str,
        language: str = "tr"
    ) -> Dict:
        """
        Hikâyeyi analiz eder: duygu, karakter, okuma seviyesi, tema vb.
        
        Args:
            story_text: Hikâye metni
            language: Dil
        
        Returns:
            Analiz sonuçları
        """
        prompt = f"""
Aşağıdaki hikâyeyi detaylı analiz et ve JSON formatında sonuçları döndür.

Hikâye:
{story_text}

Analiz etmen gerekenler:
1. Duygu analizi: Hikâyedeki ana duygular (mutlu, üzgün, korkulu, heyecanlı, vb.)
2. Karakter analizi: Ana karakterler, rolleri, özellikleri
3. Okuma seviyesi: Yaş grubu, zorluk seviyesi (kolay, orta, zor)
4. Tema analizi: Ana temalar, mesajlar
5. Kelime sayısı, cümle sayısı
6. Okuma süresi tahmini (dakika)
7. Önerilen yaş grubu

JSON formatında döndür:
{{
  "emotions": {{
    "primary": "ana_duygu",
    "secondary": ["ikincil_duygu1", "ikincil_duygu2"],
    "emotion_score": {{
      "happy": 0.7,
      "sad": 0.2,
      "excited": 0.8,
      "scared": 0.1
    }}
  }},
  "characters": [
    {{
      "name": "Karakter adı",
      "role": "Ana karakter / Yan karakter",
      "personality": "Kişilik özellikleri",
      "importance": "yüksek / orta / düşük"
    }}
  ],
  "reading_level": {{
    "difficulty": "kolay / orta / zor",
    "age_group": "5-7 / 8-10 / 11-13 / 14+",
    "grade_level": "1-2 / 3-4 / 5-6 / 7+"
  }},
  "themes": ["tema1", "tema2", "tema3"],
  "statistics": {{
    "word_count": 500,
    "sentence_count": 30,
    "paragraph_count": 5,
    "average_words_per_sentence": 16.7,
    "reading_time_minutes": 3
  }},
  "recommended_age": "5-8",
  "keywords": ["anahtar_kelime1", "anahtar_kelime2"]
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat analiz uzmanısın. Hikâyeleri detaylı analiz ediyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # JSON'u çıkar (eğer markdown code block içindeyse)
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(analysis_text)
            
            # Ek istatistikler ekle
            analysis['statistics']['word_count'] = len(story_text.split())
            analysis['statistics']['sentence_count'] = len(re.split(r'[.!?]+', story_text))
            analysis['statistics']['paragraph_count'] = len([p for p in story_text.split('\n\n') if p.strip()])
            
            return analysis
        
        except Exception as e:
            print(f"Hikâye analizi hatası: {e}")
            # Fallback analiz
            return self._fallback_analysis(story_text)
    
    def _fallback_analysis(self, story_text: str) -> Dict:
        """Basit fallback analiz."""
        words = story_text.split()
        sentences = re.split(r'[.!?]+', story_text)
        
        return {
            "emotions": {
                "primary": "neutral",
                "secondary": [],
                "emotion_score": {
                    "happy": 0.5,
                    "sad": 0.3,
                    "excited": 0.4,
                    "scared": 0.2
                }
            },
            "characters": [],
            "reading_level": {
                "difficulty": "medium",
                "age_group": "8-10",
                "grade_level": "3-4"
            },
            "themes": [],
            "statistics": {
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "paragraph_count": len([p for p in story_text.split('\n\n') if p.strip()]),
                "average_words_per_sentence": len(words) / max(len([s for s in sentences if s.strip()]), 1),
                "reading_time_minutes": round(len(words) / 200, 1)  # Ortalama 200 kelime/dakika
            },
            "recommended_age": "8-10",
            "keywords": []
        }
    
    async def get_reading_suggestions(
        self,
        analysis: Dict,
        user_age: Optional[int] = None
    ) -> List[str]:
        """
        Okuma önerileri getirir.
        
        Args:
            analysis: Hikâye analizi
            user_age: Kullanıcı yaşı (opsiyonel)
        
        Returns:
            Öneriler listesi
        """
        suggestions = []
        
        reading_level = analysis.get('reading_level', {})
        difficulty = reading_level.get('difficulty', 'medium')
        age_group = reading_level.get('age_group', '8-10')
        
        if difficulty == "easy":
            suggestions.append("Bu hikâye başlangıç seviyesi okuyucular için uygundur.")
        elif difficulty == "hard":
            suggestions.append("Bu hikâye ileri seviye okuyucular için uygundur.")
        
        emotions = analysis.get('emotions', {})
        primary_emotion = emotions.get('primary', '')
        
        if primary_emotion == "happy":
            suggestions.append("Neşeli bir hikâye! Mutlu sonla bitiyor.")
        elif primary_emotion == "sad":
            suggestions.append("Duygusal bir hikâye. Duyarlı okuyucular için uygun.")
        
        word_count = analysis.get('statistics', {}).get('word_count', 0)
        if word_count < 200:
            suggestions.append("Kısa bir hikâye - hızlı okunabilir.")
        elif word_count > 1000:
            suggestions.append("Uzun bir hikâye - sabırla okunmalı.")
        
        return suggestions

