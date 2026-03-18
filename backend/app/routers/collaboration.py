from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.collaboration_service import CollaborationService

router = APIRouter()
collab_service = CollaborationService()

class CreateSessionRequest(BaseModel):
    host_user_id: str
    theme: str

class JoinSessionRequest(BaseModel):
    session_id: str
    user_id: str

class StartSessionRequest(BaseModel):
    session_id: str
    user_id: str

class SubmitSegmentRequest(BaseModel):
    session_id: str
    user_id: str
    text: str

class SessionResponse(BaseModel):
    id: str
    host_id: str
    theme: str
    participants: List[str]
    turn_index: int
    segments: List[Dict]
    status: str
    created_at: str

@router.post("/sessions/create", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Yeni bir ortak yazım oturumu oluşturur.
    """
    return collab_service.create_session(request.host_user_id, request.theme)

@router.post("/sessions/join", response_model=SessionResponse)
async def join_session(request: JoinSessionRequest):
    """
    Mevcut bir oturuma katılır.
    """
    try:
        return collab_service.join_session(request.session_id, request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/start", response_model=SessionResponse)
async def start_session(request: StartSessionRequest):
    """
    Oturumu başlatır (Sadece host).
    """
    try:
        return collab_service.start_session(request.session_id, request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/submit", response_model=SessionResponse)
async def submit_segment(request: SubmitSegmentRequest):
    """
    Hikayeye bir parça ekler (Sıra kullanıcıdaysa).
    """
    try:
        return collab_service.submit_segment(request.session_id, request.user_id, request.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Oturumun güncel durumunu getirir (Polling için).
    """
    try:
        return collab_service.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/sessions", response_model=List[SessionResponse])
async def get_active_sessions():
    """
    Bekleyen (waiting) oturumları listeler.
    """
    return collab_service.get_active_sessions()
