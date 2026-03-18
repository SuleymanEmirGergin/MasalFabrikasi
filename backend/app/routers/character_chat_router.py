from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.character_chat_service import character_chat_service
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class ChatRequest(BaseModel):
    character_id: str
    message: str
    history: List[Dict[str, str]] = []  # [{"role": "user", "content": "..."}]
    use_wiro: bool = False  # Use Wiro gpt-5-nano for reply when WIRO_API_KEY is set

@router.post("/chat")
async def chat_with_character_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to a character and get a response.
    Set use_wiro=true to use Wiro gpt-5-nano instead of the default LLM.
    """
    response = await character_chat_service.chat_with_character(
        db, request.character_id, request.message, request.history, use_wiro=request.use_wiro
    )
    return {"response": response}
