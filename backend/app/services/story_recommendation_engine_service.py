from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
import json
import os
import uuid
from datetime import datetime


class StoryRecommendationEngineService:
    """Gelişmiş hikaye öneri motoru servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
        self.recommendations_file = os.path.join(settings.STORAGE_PATH, "story_recommendations.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        based_on: str = "reading_history"  # "reading_history", "preferences", "similar_stories"
    ) -> List[Dict]:
        """Kişiselleştirilmiş öneriler getirir."""
        if based_on == "reading_history":
            return await self._recommend_based_on_history(user_id, limit)
        elif based_on == "preferences":
            return await self._recommend_based_on_preferences(user_id, limit)
        elif based_on == "similar_stories":
            return await self._recommend_similar_stories(user_id, limit)
        else:
            return []
    
    async def _recommend_based_on_history(
        self,
        user_id: str,
        limit: int
    ) -> List[Dict]:
        """Okuma geçmişine göre önerir."""
        # Kullanıcının okuduğu hikayeleri al
        all_stories = self.story_storage.get_all_stories()
        user_stories = [s for s in all_stories if s.get("user_id") == user_id]
        
        if not user_stories:
            # İlk kullanıcı için popüler hikayeler
            return all_stories[:limit]
        
        # Okunan hikayelerin temalarını analiz et
        themes = {}
        for story in user_stories:
            theme = story.get("theme", "genel")
            themes[theme] = themes.get(theme, 0) + 1
        
        # En çok okunan temaya göre öner
        favorite_theme = max(themes, key=themes.get) if themes else "genel"
        
        recommendations = [
            s for s in all_stories
            if s.get("theme") == favorite_theme
            and s.get("story_id") not in [us.get("story_id") for us in user_stories]
        ]
        
        return recommendations[:limit]
    
    async def _recommend_based_on_preferences(
        self,
        user_id: str,
        limit: int
    ) -> List[Dict]:
        """Tercihlere göre önerir."""
        # Kullanıcı tercihlerini al (varsa)
        all_stories = self.story_storage.get_all_stories()
        
        # AI ile öneri oluştur
        user_stories = [s for s in all_stories if s.get("user_id") == user_id]
        
        if not user_stories:
            return all_stories[:limit]
        
        # Kullanıcının hikayelerini analiz et
        themes_text = ", ".join([s.get("theme", "") for s in user_stories[:5]])
        
        prompt = f"""Kullanıcı şu temalarda hikayeler okumuş: {themes_text}
Bu kullanıcıya benzer temalarda yeni hikaye önerileri yap."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye öneri uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Basit eşleştirme
        recommendations = [
            s for s in all_stories
            if s.get("story_id") not in [us.get("story_id") for us in user_stories]
        ]
        
        return recommendations[:limit]
    
    async def _recommend_similar_stories(
        self,
        user_id: str,
        limit: int
    ) -> List[Dict]:
        """Benzer hikayeler önerir."""
        all_stories = self.story_storage.get_all_stories()
        user_stories = [s for s in all_stories if s.get("user_id") == user_id]
        
        if not user_stories:
            return all_stories[:limit]
        
        # En son okunan hikayeyi al
        latest_story = user_stories[-1]
        theme = latest_story.get("theme", "")
        story_type = latest_story.get("story_type", "")
        
        # Benzer temalı hikayeleri bul
        similar = [
            s for s in all_stories
            if (s.get("theme") == theme or s.get("story_type") == story_type)
            and s.get("story_id") != latest_story.get("story_id")
        ]
        
        return similar[:limit]
    
    async def get_trending_stories(
        self,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict]:
        """Trend hikayeleri getirir."""
        all_stories = self.story_storage.get_all_stories()
        
        # Basit trending (son oluşturulanlar)
        recent_stories = sorted(
            all_stories,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        return recent_stories[:limit]
    
    def _load_recommendations(self) -> Dict:
        """Önerileri yükler."""
        try:
            with open(self.recommendations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_recommendations(self, recommendations: Dict):
        """Önerileri kaydeder."""
        with open(self.recommendations_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, ensure_ascii=False, indent=2)

