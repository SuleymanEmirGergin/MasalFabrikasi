from sqlalchemy.orm import Session
from app.models import Story, StoryAnalysis
from langchain_openai import ChatOpenAI
import json

class EducationalAnalysisService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    async def analyze_story(self, db: Session, story_id: str):
        """
        Analyzes a story to extract educational metrics.
        """
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            return None
        
        # 1. Basic Stats
        words = story.story_text.split()
        word_count = len(words)
        unique_words = len(set(words))
        
        # 2. AI Analysis for Themes
        prompt = f"""
        Analyze this children's story for educational content.
        Story: {story.story_text[:2000]}...
        
        Return a JSON object with:
        - themes: list of educational themes (e.g., Friendship, Honesty, Courage) - Max 3
        - keywords: list of 5 important vocabulary words
        - complexity_score: 1-10 (1=Simple, 10=Complex)
        
        JSON format only.
        """
        
        try:
            response = self.llm.invoke(prompt).content
            # Basic cleanup if markdown ticks are present
            response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response)
        except:
            # Fallback
            data = {
                "themes": ["Imagination"],
                "keywords": [],
                "complexity_score": 3.0
            }
            
        # 3. Save Analysis
        analysis = StoryAnalysis(
            story_id=story.id,
            vocabulary_count=word_count,
            unique_words=unique_words,
            complexity_score=data.get("complexity_score", 5.0),
            educational_themes=data.get("themes", []),
            keywords=data.get("keywords", [])
        )
        
        db.add(analysis)
        db.commit()
        return analysis

educational_analysis_service = EducationalAnalysisService()
