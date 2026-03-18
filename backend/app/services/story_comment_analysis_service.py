from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryCommentAnalysisService:
    """Hikaye yorum ve analiz araçları servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.analyses_file = os.path.join(settings.STORAGE_PATH, "comment_analyses.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.analyses_file):
            with open(self.analyses_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def analyze_comments(
        self,
        story_id: str,
        comments: List[str]
    ) -> Dict:
        """Yorumları analiz eder."""
        analysis_id = str(uuid.uuid4())
        
        comments_text = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(comments)])
        
        prompt = f"""Aşağıdaki yorumları analiz et:
{comments_text}

Şunları belirle:
1. Genel duygu durumu (pozitif/negatif/nötr)
2. Ana temalar ve konular
3. Öneriler ve geri bildirimler
4. En çok bahsedilen özellikler"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir yorum analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Duygu analizi
        sentiment = self._analyze_sentiment(comments)
        
        analysis = {
            "analysis_id": analysis_id,
            "story_id": story_id,
            "comments_count": len(comments),
            "analysis": analysis_text,
            "sentiment": sentiment,
            "themes": self._extract_themes(comments),
            "created_at": datetime.now().isoformat()
        }
        
        analyses = self._load_analyses()
        analyses.append(analysis)
        self._save_analyses(analyses)
        
        return {
            "analysis_id": analysis_id,
            "sentiment": sentiment,
            "themes": analysis["themes"],
            "analysis": analysis_text
        }
    
    async def generate_response_suggestions(
        self,
        comment: str,
        story_context: Optional[str] = None
    ) -> Dict:
        """Yorum için yanıt önerileri oluşturur."""
        prompt = f"""Aşağıdaki yoruma profesyonel ve nazik bir yanıt öner:
Yorum: {comment}

{f"Hikaye bağlamı: {story_context}" if story_context else ""}

3 farklı yanıt seçeneği sun."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir müşteri hizmetleri uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        suggestions = response.choices[0].message.content
        
        return {
            "suggestions": suggestions,
            "suggestions_count": len(suggestions.split('\n'))
        }
    
    def _analyze_sentiment(self, comments: List[str]) -> Dict:
        """Duygu analizi yapar."""
        positive_words = ["güzel", "harika", "mükemmel", "beğendim", "sevdi"]
        negative_words = ["kötü", "beğenmedim", "yetersiz", "hata", "problem"]
        
        positive_count = sum(1 for comment in comments if any(word in comment.lower() for word in positive_words))
        negative_count = sum(1 for comment in comments if any(word in comment.lower() for word in negative_words))
        
        total = len(comments)
        if total == 0:
            return {"positive": 0, "negative": 0, "neutral": 0}
        
        return {
            "positive": round((positive_count / total) * 100, 2),
            "negative": round((negative_count / total) * 100, 2),
            "neutral": round(((total - positive_count - negative_count) / total) * 100, 2)
        }
    
    def _extract_themes(self, comments: List[str]) -> List[str]:
        """Temaları çıkarır."""
        themes = []
        theme_keywords = {
            "karakter": ["karakter", "kahraman", "kişi"],
            "olay": ["olay", "hikaye", "kurgu"],
            "dil": ["dil", "anlatım", "yazım"],
            "görsel": ["görsel", "resim", "illüstrasyon"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in " ".join(comments).lower() for keyword in keywords):
                themes.append(theme)
        
        return themes
    
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

