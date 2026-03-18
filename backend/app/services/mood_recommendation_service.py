from typing import List, Dict, Optional
from app.services.story_storage import StoryStorage
from app.services.story_analysis_service import StoryAnalysisService
from app.services.recommendation_service import RecommendationService
import json
import os
from datetime import datetime
from app.core.config import settings


class MoodRecommendationService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.analysis_service = StoryAnalysisService()
        self.recommendation_service = RecommendationService()
        self.user_moods_file = os.path.join(settings.STORAGE_PATH, "user_moods.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.user_moods_file):
            with open(self.user_moods_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def get_mood_based_recommendations(self, user_id: str, mood: str, limit: int = 10) -> List[Dict]:
        all_stories = self.story_storage.get_all_stories()
        scored = []
        
        for story in all_stories:
            analysis = await self.analysis_service.analyze_story(story.get('story_text', ''), story.get('language', 'tr'))
            story_emotion = analysis.get('emotions', {}).get('primary', 'neutral')
            
            mood_match = self._calculate_mood_match(mood, story_emotion)
            if mood_match > 0.5:
                scored.append({"story": story, "score": mood_match})
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        return [s['story'] for s in scored[:limit]]
    
    def _calculate_mood_match(self, user_mood: str, story_emotion: str) -> float:
        mood_map = {
            "happy": ["happy", "excited", "joyful"],
            "sad": ["sad", "melancholic"],
            "excited": ["excited", "adventurous"],
            "calm": ["calm", "peaceful", "neutral"]
        }
        matching_emotions = mood_map.get(user_mood.lower(), [])
        return 1.0 if story_emotion.lower() in matching_emotions else 0.3
    
    async def get_weather_based_recommendations(self, user_id: str, weather: str, limit: int = 5) -> List[Dict]:
        weather_themes = {
            "sunny": ["beach", "summer", "adventure"],
            "rainy": ["indoor", "cozy", "mystery"],
            "snowy": ["winter", "magic", "fantasy"],
            "cloudy": ["neutral", "calm"]
        }
        themes = weather_themes.get(weather.lower(), [])
        all_stories = self.story_storage.get_all_stories()
        matching = [s for s in all_stories if any(t in s.get('theme', '').lower() for t in themes)]
        return matching[:limit]
    
    async def get_time_based_recommendations(self, user_id: str, time_of_day: str, limit: int = 5) -> List[Dict]:
        time_preferences = {
            "morning": ["energetic", "adventure", "happy"],
            "afternoon": ["educational", "learning"],
            "evening": ["calm", "peaceful"],
            "bedtime": ["calm", "peaceful", "sleepy", "dreamy"]
        }
        preferred_emotions = time_preferences.get(time_of_day.lower(), [])
        all_stories = self.story_storage.get_all_stories()
        scored = []
        
        for story in all_stories:
            analysis = await self.analysis_service.analyze_story(story.get('story_text', ''), story.get('language', 'tr'))
            story_emotion = analysis.get('emotions', {}).get('primary', 'neutral')
            if story_emotion.lower() in preferred_emotions:
                scored.append({"story": story, "score": 1.0})
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        return [s['story'] for s in scored[:limit]]

