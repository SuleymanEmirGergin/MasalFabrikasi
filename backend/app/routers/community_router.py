from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.core.database import get_db
from app.models import Story, UserProfile, Comment
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class AuthorSchema(BaseModel):
    username: str
    id: str

class PublicStorySchema(BaseModel):
    id: str
    title: str
    theme: str
    image_url: Optional[str]
    like_count: int
    view_count: int
    created_at: datetime
    author: AuthorSchema

    class Config:
        from_attributes = True

@router.get("/feed", response_model=List[PublicStorySchema])
async def get_community_feed(
    page: int = 1, 
    limit: int = 20, 
    sort_by: str = "latest", # latest, popular
    db: Session = Depends(get_db)
):
    """
    Get public stories for the community feed.
    """
    query = db.query(Story).filter(Story.is_public == True)
    
    if sort_by == "popular":
        query = query.order_by(desc(Story.like_count))
    else:
        query = query.order_by(desc(Story.created_at))
        
    stories = query.offset((page - 1) * limit).limit(limit).all()
    
    # Transform to schema manually to handle author relation gracefully
    result = []
    for s in stories:
        result.append({
            "id": s.id,
            "title": s.title,
            "theme": s.theme,
            "image_url": s.image_url,
            "like_count": s.like_count,
            "view_count": s.view_count,
            "created_at": s.created_at,
            "author": {
                "username": s.user.username if s.user else "Unknown",
                "id": s.user_id
            }
        })
        
    return result

@router.post("/{story_id}/like")
async def like_story(story_id: str, db: Session = Depends(get_db)):
    """
    Increment like count for a story.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
        
    story.like_count += 1
    db.commit()
    return {"status": "success", "likes": story.like_count}

@router.get("/{story_id}/comments")
async def get_comments(story_id: str, db: Session = Depends(get_db)):
    """
    Get comments for a story.
    """
    comments = db.query(Comment).filter(Comment.story_id == story_id).order_by(desc(Comment.created_at)).all()
    return [{
        "id": c.id,
        "content": c.content,
        "username": c.user.username if c.user else "Anonymous", # Assuming user relationship exists on Comment
        "created_at": c.created_at
    } for c in comments]

# NOTE: Comment posting would require Auth user context, skipped for brevity in this public read-only phase
