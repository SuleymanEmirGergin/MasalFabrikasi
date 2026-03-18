from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryEmotionAnalysisService:
    """Hikaye duygu analizi servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.emotion_analyses_file = os.path.join(settings.STORAGE_PATH, "emotion_analyses.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.emotion_analyses_file):
            with open(self.emotion_analyses_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def analyze_emotions(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikayedeki duyguları analiz eder."""
        prompt = f"""Aşağıdaki hikayedeki duyguları analiz et. Her bölüm için:
1. Baskın duygu (mutluluk, üzüntü, korku, heyecan, vb.)
2. Duygu yoğunluğu (1-10 arası)
3. Duygu geçişleri

Hikaye:
{story_text}

JSON formatında döndür."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir duygu analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        # Basit duygu analizi
        emotions = self._extract_emotions_from_text(story_text)
        
        analysis = {
            "story_id": story_id,
            "emotions": emotions,
            "overall_sentiment": self._calculate_overall_sentiment(emotions),
            "analyzed_at": datetime.now().isoformat()
        }
        
        analyses = self._load_analyses()
        analyses[story_id] = analysis
        self._save_analyses(analyses)
        
        return analysis
    
    def _extract_emotions_from_text(self, text: str) -> List[Dict]:
        """Metinden duyguları çıkarır."""
        emotions = []
        emotion_keywords = {
            "mutluluk": ["mutlu", "neşeli", "sevinç", "gülümseme", "eğlence"],
            "üzüntü": ["üzgün", "hüzün", "ağlamak", "keder", "acı"],
            "korku": ["korku", "endişe", "kaygı", "tedirgin", "ürkütücü"],
            "heyecan": ["heyecan", "coşku", "enerji", "canlı", "dinamik"],
            "sakinlik": ["sakin", "huzur", "rahat", "sessiz", "dingin"]
        }
        
        sentences = text.split('.')
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                detected_emotions = []
                for emotion, keywords in emotion_keywords.items():
                    if any(keyword in sentence.lower() for keyword in keywords):
                        detected_emotions.append(emotion)
                
                if detected_emotions:
                    emotions.append({
                        "segment_id": str(uuid.uuid4()),
                        "sentence_index": i,
                        "emotions": detected_emotions,
                        "intensity": len(detected_emotions) * 2,
                        "text": sentence.strip()
                    })
        
        return emotions
    
    def _calculate_overall_sentiment(self, emotions: List[Dict]) -> str:
        """Genel duygu durumunu hesaplar."""
        if not emotions:
            return "nötr"
        
        emotion_counts = {}
        for emotion_data in emotions:
            for emotion in emotion_data.get("emotions", []):
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if emotion_counts:
            dominant = max(emotion_counts, key=emotion_counts.get)
            return dominant
        return "nötr"
    
    async def get_emotion_analysis(self, story_id: str) -> Optional[Dict]:
        """Duygu analizini getirir."""
        analyses = self._load_analyses()
        return analyses.get(story_id)
    
    def _load_analyses(self) -> Dict:
        """Analizleri yükler."""
        try:
            with open(self.emotion_analyses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_analyses(self, analyses: Dict):
        """Analizleri kaydeder."""
        with open(self.emotion_analyses_file, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)

