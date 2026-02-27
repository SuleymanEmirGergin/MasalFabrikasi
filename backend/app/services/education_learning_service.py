from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json
import re
from datetime import datetime


class EducationLearningService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
        self.learning_progress_file = f"{settings.STORAGE_PATH}/learning_progress.json"
        self._ensure_file()
    
    def _ensure_file(self):
        import os
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.learning_progress_file):
            with open(self.learning_progress_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def analyze_reading_level(
        self,
        story_text: str,
        language: str = "tr"
    ) -> Dict:
        """Okuma seviyesi analizi yapar."""
        words = story_text.split()
        sentences = re.split(r'[.!?]+', story_text)
        
        # Basit hesaplamalar
        avg_words_per_sentence = len(words) / max(len([s for s in sentences if s.strip()]), 1)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Seviye belirleme
        if avg_words_per_sentence < 8 and avg_word_length < 4:
            level = "Başlangıç (5-7 yaş)"
        elif avg_words_per_sentence < 12 and avg_word_length < 5:
            level = "Orta (8-10 yaş)"
        elif avg_words_per_sentence < 16 and avg_word_length < 6:
            level = "İleri (11-13 yaş)"
        else:
            level = "Uzman (14+ yaş)"
        
        return {
            "reading_level": level,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "avg_word_length": round(avg_word_length, 1),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()])
        }
    
    async def extract_vocabulary(
        self,
        story_text: str,
        difficulty_level: str = "medium"
    ) -> Dict:
        """Hikâyeden kelime çıkarır."""
        words = story_text.split()
        unique_words = list(set(word.lower().strip('.,!?;:"()[]{}') for word in words))
        
        # Zorluk seviyesine göre filtreleme (basit örnek)
        if difficulty_level == "easy":
            vocabulary = [w for w in unique_words if len(w) <= 5]
        elif difficulty_level == "hard":
            vocabulary = [w for w in unique_words if len(w) >= 8]
        else:
            vocabulary = unique_words
        
        return {
            "vocabulary": vocabulary[:50],  # En fazla 50 kelime
            "total_words": len(unique_words),
            "difficulty_level": difficulty_level
        }
    
    async def create_learning_mode(
        self,
        story_id: str,
        learning_type: str = "vocabulary"
    ) -> Dict:
        """Öğrenme modu oluşturur."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        if learning_type == "vocabulary":
            vocab = await self.extract_vocabulary(story.get('story_text', ''))
            return {
                "story_id": story_id,
                "learning_type": learning_type,
                "vocabulary": vocab,
                "exercises": []
            }
        elif learning_type == "comprehension":
            # Anlama soruları oluştur
            return {
                "story_id": story_id,
                "learning_type": learning_type,
                "questions": []
            }
        
        return {"story_id": story_id, "learning_type": learning_type}
    
    async def generate_educational_story(
        self,
        topic: str,
        age_group: str,
        educational_goal: str,
        language: str = "tr"
    ) -> Dict:
        """Eğitici hikâye oluşturur."""
        prompt = f"""
{age_group} yaş grubuna uygun, {topic} konusunda eğitici bir hikâye yaz.

Eğitim Hedefi: {educational_goal}

Hikâye eğlenceli, öğretici ve yaş grubuna uygun olmalı. JSON formatında döndür:
{{
  "story_text": "Hikâye metni",
  "learning_points": ["Öğrenme noktası 1", "Öğrenme noktası 2"],
  "vocabulary": ["Kelime 1", "Kelime 2"],
  "questions": [
    {{"question": "Soru", "answer": "Cevap"}}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir eğitim uzmanısın. Eğitici hikâyeler yazıyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def track_learning_progress(
        self,
        user_id: str,
        story_id: str,
        progress_data: Dict
    ):
        """Öğrenme ilerlemesini takip eder."""
        import os
        with open(self.learning_progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        if user_id not in progress:
            progress[user_id] = {}
        
        if story_id not in progress[user_id]:
            progress[user_id][story_id] = {
                "started_at": datetime.now().isoformat(),
                "completed": False
            }
        
        progress[user_id][story_id].update(progress_data)
        progress[user_id][story_id]["last_updated"] = datetime.now().isoformat()
        
        with open(self.learning_progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

