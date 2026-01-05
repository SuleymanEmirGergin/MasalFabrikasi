from typing import List, Dict, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.recommendation_service import RecommendationService
from app.services.story_storage import StoryStorage
import json
import os
from datetime import datetime
from app.core.config import settings


class AIRecommendationsAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.recommendation_service = RecommendationService()
        self.story_storage = StoryStorage()
        self.learning_file = os.path.join(settings.STORAGE_PATH, "recommendation_learning.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.learning_file):
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def get_realtime_recommendations(
        self,
        user_id: str,
        current_story_id: Optional[str] = None,
        user_action: Optional[str] = None
    ) -> List[Dict]:
        """Gerçek zamanlı öneriler getirir."""
        # Kullanıcı eylemlerini analiz et
        user_preferences = self._get_user_learning_data(user_id)
        
        # AI ile öneri oluştur
        prompt = f"""
Kullanıcı ID: {user_id}
Mevcut Hikâye: {current_story_id or 'Yok'}
Kullanıcı Eylemi: {user_action or 'Yok'}
Kullanıcı Tercihleri: {json.dumps(user_preferences, ensure_ascii=False)}

Bu kullanıcı için 5 hikâye önerisi oluştur. JSON formatında döndür:
{{
  "recommendations": [
    {{
      "story_id": "önerilen_hikâye_id",
      "reason": "Neden önerildi",
      "confidence": 0.9
    }}
  ]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir öneri sistemi uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result.get('recommendations', [])
        except:
            # Fallback: Normal öneri servisi
            return await self.recommendation_service.get_recommendations(user_id, 5)
    
    def _get_user_learning_data(self, user_id: str) -> Dict:
        """Kullanıcı öğrenme verilerini getirir."""
        try:
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                learning = json.load(f)
            return learning.get(user_id, {})
        except:
            return {}
    
    def record_user_interaction(
        self,
        user_id: str,
        story_id: str,
        interaction_type: str,
        rating: Optional[float] = None
    ):
        """Kullanıcı etkileşimini kaydeder (öğrenme için)."""
        try:
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                learning = json.load(f)
        except:
            learning = {}
        
        if user_id not in learning:
            learning[user_id] = {
                "interactions": [],
                "preferences": {}
            }
        
        interaction = {
            "story_id": story_id,
            "interaction_type": interaction_type,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }
        
        learning[user_id]["interactions"].append(interaction)
        
        # Tercihleri güncelle
        if rating and rating > 3:
            story = self.story_storage.get_story(story_id)
            if story:
                theme = story.get('theme', '')
                if theme not in learning[user_id]["preferences"]:
                    learning[user_id]["preferences"][theme] = 0
                learning[user_id]["preferences"][theme] += 1
        
        with open(self.learning_file, 'w', encoding='utf-8') as f:
            json.dump(learning, f, ensure_ascii=False, indent=2)
    
    async def get_contextual_recommendations(
        self,
        user_id: str,
        context: Dict
    ) -> List[Dict]:
        """Bağlamsal öneriler getirir."""
        time_of_day = context.get('time_of_day', '')
        mood = context.get('mood', '')
        weather = context.get('weather', '')
        
        # Bağlama göre öneriler
        all_stories = self.story_storage.get_all_stories()
        scored = []
        
        for story in all_stories:
            score = 0
            
            # Zaman bazlı
            if time_of_day == "morning":
                if "energetic" in story.get('theme', '').lower():
                    score += 10
            elif time_of_day == "bedtime":
                if "calm" in story.get('theme', '').lower():
                    score += 10
            
            # Ruh hali bazlı
            if mood:
                story_text = story.get('story_text', '').lower()
                if mood.lower() in story_text:
                    score += 15
            
            if score > 0:
                scored.append({"story": story, "score": score})
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        return [s['story'] for s in scored[:10]]

