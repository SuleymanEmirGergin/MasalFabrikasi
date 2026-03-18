from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import re


class StoryImprovementService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    
    async def analyze_story_quality(
        self,
        story_text: str,
        language: str = "tr"
    ) -> Dict:
        """
        Hikâye kalitesini analiz eder ve iyileştirme önerileri sunar.
        
        Args:
            story_text: Hikâye metni
            language: Dil
        
        Returns:
            Analiz sonuçları ve öneriler
        """
        prompt = f"""
Aşağıdaki hikâyeyi analiz et ve iyileştirme önerileri sun. JSON formatında döndür.

Hikâye:
{story_text}

Analiz etmen gerekenler:
1. Yazım ve dil bilgisi hataları
2. Cümle yapısı ve akıcılık
3. Kelime seçimi ve çeşitlilik
4. Hikâye yapısı (giriş, gelişme, sonuç)
5. Karakter gelişimi
6. Diyalog kalitesi
7. Betimleme kalitesi
8. Genel okunabilirlik

Her kategori için:
- Skor (0-100)
- Güçlü yönler
- İyileştirme önerileri
- Örnek cümleler (iyileştirilmiş versiyonlar)

JSON formatında döndür:
{{
  "overall_score": 75,
  "categories": {{
    "spelling_grammar": {{
      "score": 80,
      "strengths": ["Güçlü yönler"],
      "suggestions": ["İyileştirme önerileri"],
      "examples": [{{"original": "Cümle", "improved": "İyileştirilmiş cümle"}}]
    }},
    "sentence_structure": {{...}},
    "word_choice": {{...}},
    "story_structure": {{...}},
    "character_development": {{...}},
    "dialogue": {{...}},
    "description": {{...}},
    "readability": {{...}}
  }},
  "top_suggestions": [
    "En önemli 3-5 öneri"
  ],
  "readability_score": 65
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat editörüsün. Hikâyeleri analiz edip iyileştirme önerileri sunuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # JSON'u çıkar
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(analysis_text)
            
            # Ek hesaplamalar
            analysis['statistics'] = self._calculate_text_statistics(story_text)
            
            return analysis
        
        except Exception as e:
            print(f"Hikâye iyileştirme analizi hatası: {e}")
            return self._fallback_analysis(story_text)
    
    def _calculate_text_statistics(self, text: str) -> Dict:
        """Metin istatistiklerini hesaplar."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        # Kelime çeşitliliği
        unique_words = len(set(word.lower() for word in words))
        word_diversity = unique_words / len(words) if words else 0
        
        # Ortalama cümle uzunluğu
        avg_sentence_length = len(words) / max(len([s for s in sentences if s.strip()]), 1)
        
        # Ortalama kelime uzunluğu
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len(paragraphs),
            "unique_words": unique_words,
            "word_diversity": round(word_diversity * 100, 2),
            "average_sentence_length": round(avg_sentence_length, 1),
            "average_word_length": round(avg_word_length, 1)
        }
    
    def _fallback_analysis(self, story_text: str) -> Dict:
        """Basit fallback analiz."""
        stats = self._calculate_text_statistics(story_text)
        
        return {
            "overall_score": 70,
            "categories": {
                "spelling_grammar": {
                    "score": 75,
                    "strengths": ["Genel olarak doğru yazım"],
                    "suggestions": ["Yazım kontrolü yapın"],
                    "examples": []
                }
            },
            "top_suggestions": [
                "Hikâyeyi bir kez daha gözden geçirin",
                "Cümle yapılarını çeşitlendirin"
            ],
            "readability_score": 65,
            "statistics": stats
        }
    
    async def get_improved_version(
        self,
        story_text: str,
        improvement_type: str,
        language: str = "tr"
    ) -> str:
        """
        Hikâyenin iyileştirilmiş versiyonunu üretir.
        
        Args:
            story_text: Orijinal hikâye metni
            improvement_type: İyileştirme tipi (flow, vocabulary, structure, etc.)
            language: Dil
        
        Returns:
            İyileştirilmiş hikâye metni
        """
        improvement_prompts = {
            "flow": "Hikâyeyi daha akıcı hale getir. Cümle geçişlerini iyileştir.",
            "vocabulary": "Kelime çeşitliliğini artır. Daha zengin kelimeler kullan.",
            "structure": "Hikâye yapısını iyileştir. Giriş, gelişme, sonuç bölümlerini güçlendir.",
            "description": "Betimlemeleri zenginleştir. Daha canlı ve detaylı betimlemeler ekle.",
            "dialogue": "Diyalogları iyileştir. Daha doğal ve karakteristik diyaloglar yaz."
        }
        
        prompt_text = improvement_prompts.get(improvement_type, "Hikâyeyi genel olarak iyileştir.")
        
        prompt = f"""
{prompt_text}

Orijinal Hikâye:
{story_text}

İyileştirilmiş versiyonu döndür. Sadece iyileştirilmiş metni döndür, ek açıklama yapma.
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir edebiyat editörüsün. Hikâyeleri iyileştiriyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Hikâye iyileştirme hatası: {e}")
            return story_text

