from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models import Story, StoryAnalysis, UserProfile

router = APIRouter()

@router.get("/{user_id}/stats")
async def get_parental_stats(user_id: str, db: Session = Depends(get_db)):
    """
    Get aggregated educational stats for a user's child.
    """
    # Get all analysis for user's stories
    analyses = db.query(StoryAnalysis).join(Story).filter(Story.user_id == user_id).all()
    
    if not analyses:
        return {
            "total_stories_read": 0,
            "total_words_learned": 0,
            "top_themes": [],
            "complexity_progress": []
        }
        
    total_words = sum(a.vocabulary_count for a in analyses)
    unique_words_learned = sum(a.unique_words for a in analyses) # Simplified aggregation
    
    # Group themes
    theme_counts = {}
    for a in analyses:
        if a.educational_themes:
            for theme in a.educational_themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
                
    top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_stories_read": len(analyses),
        "total_words_encountered": total_words,
        "unique_vocab_exposure": unique_words_learned,
        "top_themes": [{"name": k, "count": v} for k, v in top_themes],
        "recent_analyses": [
            {
                "story_title": a.story.title,
                "score": a.complexity_score,
                "themes": a.educational_themes,
                "date": a.analyzed_at
            } for a in analyses[-5:]
        ]
    }
