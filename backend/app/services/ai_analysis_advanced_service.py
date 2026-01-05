from typing import Dict, List
from openai import OpenAI
from app.core.config import settings
from app.services.story_analysis_service import StoryAnalysisService
import json


class AIAnalysisAdvancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.analysis_service = StoryAnalysisService()
    
    async def generate_emotion_chart_data(self, story_id: str) -> Dict:
        """Duygu analizi grafik verisi oluşturur."""
        from app.services.story_storage import StoryStorage
        story_storage = StoryStorage()
        
        story = story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        analysis = await self.analysis_service.analyze_story(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        
        emotions = analysis.get('emotions', {})
        emotion_scores = emotions.get('emotion_score', {})
        
        # Grafik verisi
        chart_data = {
            "labels": list(emotion_scores.keys()),
            "values": list(emotion_scores.values()),
            "primary_emotion": emotions.get('primary', 'neutral'),
            "secondary_emotions": emotions.get('secondary', [])
        }
        
        return chart_data
    
    async def generate_character_chart_data(self, story_id: str) -> Dict:
        """Karakter analizi grafik verisi oluşturur."""
        from app.services.story_storage import StoryStorage
        story_storage = StoryStorage()
        
        story = story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        analysis = await self.analysis_service.analyze_story(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        
        characters = analysis.get('characters', [])
        
        # Karakter önem grafiği
        character_data = {
            "characters": [
                {
                    "name": c.get('name', ''),
                    "importance": c.get('importance', 'medium'),
                    "role": c.get('role', '')
                }
                for c in characters
            ],
            "total_characters": len(characters),
            "main_characters": len([c for c in characters if c.get('importance') == 'high'])
        }
        
        return character_data
    
    async def generate_theme_chart_data(self, story_id: str) -> Dict:
        """Tema analizi grafik verisi oluşturur."""
        from app.services.story_storage import StoryStorage
        story_storage = StoryStorage()
        
        story = story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        analysis = await self.analysis_service.analyze_story(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        
        themes = analysis.get('themes', [])
        
        return {
            "themes": themes,
            "theme_count": len(themes),
            "primary_theme": story.get('theme', '')
        }
    
    async def generate_readability_chart_data(self, story_id: str) -> Dict:
        """Okunabilirlik analizi grafik verisi oluşturur."""
        from app.services.story_storage import StoryStorage
        story_storage = StoryStorage()
        
        story = story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        analysis = await self.analysis_service.analyze_story(
            story.get('story_text', ''),
            story.get('language', 'tr')
        )
        
        reading_level = analysis.get('reading_level', {})
        stats = analysis.get('statistics', {})
        
        return {
            "readability_score": reading_level.get('difficulty', 'medium'),
            "age_group": reading_level.get('age_group', '8-10'),
            "word_count": stats.get('word_count', 0),
            "sentence_count": stats.get('sentence_count', 0),
            "average_words_per_sentence": stats.get('average_words_per_sentence', 0)
        }

