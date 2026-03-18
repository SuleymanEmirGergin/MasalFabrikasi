from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.story_storage import StoryStorage
from app.services.story_analysis_service import StoryAnalysisService
import json
from datetime import datetime


class StoryInsightsService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.story_storage = StoryStorage()
        self.analysis_service = StoryAnalysisService()
    
    async def generate_story_insights(self, story_id: str) -> Dict:
        """Hikâye için derinlemesine içgörüler oluşturur."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        story_text = story.get('story_text', '')
        analysis = await self.analysis_service.analyze_story(story_text, story.get('language', 'tr'))
        
        prompt = f"""
Aşağıdaki hikâye analizini kullanarak derinlemesine içgörüler oluştur.

Hikâye Analizi:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

JSON formatında döndür:
{{
  "key_insights": [
    "İçgörü 1",
    "İçgörü 2",
    "İçgörü 3"
  ],
  "strengths": ["Güçlü yön 1", "Güçlü yön 2"],
  "weaknesses": ["Zayıf yön 1", "Zayıf yön 2"],
  "recommendations": ["Öneri 1", "Öneri 2"],
  "target_audience": "Hedef kitle",
  "unique_selling_points": ["Özellik 1", "Özellik 2"]
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir hikâye analiz uzmanısın. Derinlemesine içgörüler sunuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            insights_text = response.choices[0].message.content
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
            
            return {
                "story_id": story_id,
                "insights": insights,
                "analysis": analysis,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "story_id": story_id,
                "insights": {
                    "key_insights": [],
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": []
                },
                "error": str(e)
            }
    
    async def compare_story_insights(self, story_id_1: str, story_id_2: str) -> Dict:
        """İki hikâyenin içgörülerini karşılaştırır."""
        insights1 = await self.generate_story_insights(story_id_1)
        insights2 = await self.generate_story_insights(story_id_2)
        
        return {
            "story1_insights": insights1,
            "story2_insights": insights2,
            "comparison": {
                "similar_strengths": [],
                "different_weaknesses": [],
                "unique_features": []
            }
        }
    
    async def get_writing_trends(self, user_id: Optional[str] = None) -> Dict:
        """Yazım trendlerini analiz eder."""
        if user_id:
            all_stories = self.story_storage.get_all_stories()
            stories = [s for s in all_stories if s.get('user_id') == user_id]
        else:
            stories = self.story_storage.get_all_stories()
        
        # Tema trendleri
        themes = {}
        for story in stories:
            theme = story.get('theme', 'Bilinmeyen')
            themes[theme] = themes.get(theme, 0) + 1
        
        top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "top_themes": [{"theme": t[0], "count": t[1]} for t in top_themes],
            "total_stories": len(stories),
            "trend_period": "all_time"
        }

