from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.interactive_story_service import interactive_story_service
from pydantic import BaseModel

router = APIRouter()

class StartStoryRequest(BaseModel):
    user_id: str # Temporary, usually from auth
    theme: str
    character_name: str

class MakeChoiceRequest(BaseModel):
    segment_id: str
    choice_id: str

@router.post("/start")
async def start_interactive(request: StartStoryRequest, db: Session = Depends(get_db)):
    """
    Start a new interactive adventure.
    """
    story, first_segment = await interactive_story_service.start_interactive_story(
        db, request.user_id, request.theme, request.character_name
    )
    
    return {
        "story_id": story.id,
        "segment_id": first_segment.id,
        "content": first_segment.content,
        "choices": [{"id": c.id, "text": c.choice_text} for c in first_segment.choices]
    }

@router.post("/choose")
async def choose_path(request: MakeChoiceRequest, db: Session = Depends(get_db)):
    """
    Make a choice and get the next segment.
    """
    next_segment = await interactive_story_service.make_choice(
        db, request.segment_id, request.choice_id
    )
    
    choices = [{"id": c.id, "text": c.choice_text} for c in next_segment.choices]
    
    return {
        "segment_id": next_segment.id,
        "content": next_segment.content,
        "choices": choices,
        "is_finished": len(choices) == 0
    }
