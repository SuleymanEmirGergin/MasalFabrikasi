from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date
from app.core.database import get_db
from app.models import UserProfile, DailyQuest
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

class LeaderboardEntry(BaseModel):
    username: str
    xp: int
    level: int
    rank: int

class QuestItem(BaseModel):
    id: str
    type: str # 'create_story', 'read_story'
    description: str
    target: int
    progress: int
    completed: bool
    reward: int

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get top users by XP.
    """
    top_users = db.query(UserProfile).order_by(desc(UserProfile.xp)).limit(limit).all()
    
    leaderboard = []
    for index, user in enumerate(top_users):
        # Resolve username. 
        # UserProfile might not have username directly if auth is separate.
        # Fallback to preferences or 'User'
        username = user.preferences.get('username') if user.preferences else f"User {str(user.id)[:4]}"
        
        leaderboard.append({
            "username": username,
            "xp": user.xp,
            "level": user.level,
            "rank": index + 1
        })
        
    return leaderboard

@router.get("/quests/{user_id}", response_model=List[QuestItem])
async def get_daily_quests(user_id: str, db: Session = Depends(get_db)):
    """
    Get or create daily quests for the user.
    """
    # 1. Check if user has quests for today
    today = datetime.now().date()
    
    # Check User exists
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        # If user doesn't exist in DB yet (sync issue), returning empty is safer than error loop
         raise HTTPException(status_code=404, detail="User not found")

    quests = db.query(DailyQuest).filter(
        DailyQuest.user_id == user_id,
        func.date(DailyQuest.date) == today
    ).all()
    
    if not quests:
        # Create default quests
        new_quests = [
            DailyQuest(
                id=uuid.uuid4(), # DB expects UUID
                user_id=user_id,
                quest_type="create_story",
                target_count=1,
                xp_reward=100
            ),
            DailyQuest(
                id=uuid.uuid4(),
                user_id=user_id,
                quest_type="share_story",
                target_count=1,
                xp_reward=50
            ),
             DailyQuest(
                id=uuid.uuid4(),
                user_id=user_id,
                quest_type="read_story",
                target_count=1,
                xp_reward=20
            )
        ]
        db.add_all(new_quests)
        db.commit()
        quests = new_quests
        # Refresh to get updated state if needed, but not strictly required for just returning list
        
    result = []
    for q in quests:
        desc_map = {
            "create_story": "Yeni Bir Masal Oluştur",
            "share_story": "Bir Masalını Paylaş",
            "read_story": "Bir Masal Oku"
        }
        result.append({
            "id": str(q.id),
            "type": q.quest_type,
            "description": desc_map.get(q.quest_type, "Görev"),
            "target": q.target_count,
            "progress": q.current_progress,
            "completed": q.is_completed,
            "reward": q.xp_reward
        })
        
    return result

@router.post("/quests/{quest_id}/check")
async def check_quest_progress(quest_id: str, db: Session = Depends(get_db)):
    """
    Manually trigger a check/update for a quest (usually triggered by events).
    This is a simplified endpoint to verify completion.
    """
    # Ensure UUID
    try:
        q_uuid = uuid.UUID(quest_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    quest = db.query(DailyQuest).filter(DailyQuest.id == q_uuid).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
        
    # Logic to check progress would go here.
    # For now, we assume this endpoint might be used to force-complete debugging or verify.
    # Real logic happens in service when events occur.
    
    return {"status": "checked", "completed": quest.is_completed, "progress": quest.current_progress}

@router.get("/achievements", response_model=dict)
async def get_all_achievements():
    """
    Get all achievement definitions.
    """
    from app.services.achievement_service import achievement_service
    return {"achievements": achievement_service._achievements}

@router.get("/achievements/{user_id}", response_model=dict)
async def get_user_achievements(user_id: str, db: Session = Depends(get_db)):
    """
    Get user achievements.
    """
    from app.services.achievement_service import achievement_service
    # Service get_user_achievements method now takes db
    achievements = achievement_service.get_user_achievements(db, user_id)
    return {"achievements": achievements}
