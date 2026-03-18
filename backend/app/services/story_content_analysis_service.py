from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentAnalysisService:
    """Hikaye içerik analizi servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.analyses_file = os.path.join(settings.STORAGE_PATH, "content_analyses.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.analyses_file):
            with open(self.analyses_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def analyze_story(
        self,
        story_id: str,
        story_text: str,
        analysis_type: str = "comprehensive"
    ) -> Dict:
        """Hikayeyi analiz eder."""
        analysis_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi kapsamlı bir şekilde analiz et:
1. Yapı ve kurgu
2. Karakterler
3. Temalar
4. Dil ve anlatım
5. Güçlü ve zayıf yönler

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        analysis_text = response.choices[0].message.content
        
        # İstatistiksel analiz
        stats = self._calculate_statistics(story_text)
        
        analysis = {
            "analysis_id": analysis_id,
            "story_id": story_id,
            "analysis_type": analysis_type,
            "analysis_text": analysis_text,
            "statistics": stats,
            "created_at": datetime.now().isoformat()
        }
        
        analyses = self._load_analyses()
        analyses.append(analysis)
        self._save_analyses(analyses)
        
        return {
            "analysis_id": analysis_id,
            "analysis": analysis_text,
            "statistics": stats
        }
    
    async def analyze_readability(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Okunabilirlik analizi."""
        words = story_text.split()
        sentences = story_text.split('.')
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Basit okunabilirlik skoru
        readability_score = 100 - (avg_sentence_length * 1.5) - (avg_word_length * 2)
        readability_score = max(0, min(100, readability_score))
        
        readability_level = "kolay" if readability_score > 70 else "orta" if readability_score > 40 else "zor"
        
        return {
            "story_id": story_id,
            "readability_score": round(readability_score, 2),
            "readability_level": readability_level,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2)
        }
    
    def _calculate_statistics(self, text: str) -> Dict:
        """İstatistikleri hesaplar."""
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        return {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "character_count": len(text),
            "character_count_no_spaces": len(text.replace(" ", "")),
            "avg_words_per_sentence": round(len(words) / len(sentences), 2) if sentences else 0
        }
    
    def _load_analyses(self) -> List[Dict]:
        """Analizleri yükler."""
        try:
            with open(self.analyses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_analyses(self, analyses: List[Dict]):
        """Analizleri kaydeder."""
        with open(self.analyses_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)

