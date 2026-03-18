from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import UserProfile, Story, Purchase, Subscription, SubscriptionTier
from app.repositories.user_repository import UserRepository
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Admin Statistics Schema
class DashboardStats(BaseModel):
    total_users: int
    total_stories: int
    total_revenue: float
    premium_users: int
    daily_active_users: int
    recent_signups: int

# User Management Schema
class AdminUserList(BaseModel):
    users: List[dict]
    total: int
    page: int
    limit: int

@router.get("/stats", response_model=DashboardStats)
async def get_admin_stats(db: Session = Depends(get_db)):
    """
    Get high-level statistics for the admin dashboard.
    """
    try:
        # Total Users
        total_users = db.query(func.count(UserProfile.id)).scalar()
        
        # Total Stories
        total_stories = db.query(func.count(Story.id)).scalar()
        
        # Total Revenue (Sum of 'completed' purchases)
        revenue = db.query(func.sum(Purchase.amount)).filter(
            Purchase.status == 'completed'
        ).scalar() or 0.0
        
        # Premium Users
        premium_count = db.query(func.count(UserProfile.id)).filter(
            (UserProfile.subscription_tier == SubscriptionTier.PREMIUM) | 
            (UserProfile.subscription_tier == SubscriptionTier.PRO)
        ).scalar()
        
        # Recent Signups (Last 24h)
        yesterday = datetime.now() - timedelta(days=1)
        recent_signups = db.query(func.count(UserProfile.id)).filter(
            UserProfile.created_at >= yesterday
        ).scalar()
        
        # Mock DAU logic (Updated with last_login if available, currently mock)
        dau = int(total_users * 0.15) if total_users else 0
        
        return {
            "total_users": total_users or 0,
            "total_stories": total_stories or 0,
            "total_revenue": float(revenue),
            "premium_users": premium_count or 0,
            "daily_active_users": dau,
            "recent_signups": recent_signups or 0
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/users", response_model=AdminUserList)
async def list_users(
    page: int = 1, 
    limit: int = 20, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List users with pagination and search.
    """
    query = db.query(UserProfile)
    
    # Not: UserProfile'da username yoksa auth metadata'dan veya başka yerden alınması gerekebilir.
    # Şimdilik id üzerinden arama yapalım veya preferences->username varsa oradan (JSONB search).
    # Basitlik için sadece listeleme yapıyoruz.
    if search:
        # Postgres JSONB search example: filter(UserProfile.preferences['username'].astext.ilike(f"%{search}%"))
        pass
        
    total = query.count()
    
    users = query.order_by(desc(UserProfile.created_at)).offset((page - 1) * limit).limit(limit).all()
    
    user_list = []
    for u in users:
        # Resolve username from preferences is fallback
        username = u.preferences.get('username') if u.preferences else "Unknown"
        
        # Tier check for is_premium
        is_premium = u.subscription_tier in [SubscriptionTier.PREMIUM, SubscriptionTier.PRO]

        user_list.append({
            "id": str(u.id),
            "auth_id": str(u.auth_user_id),
            "username": username,
            "start_date": str(u.created_at),
            "credits": u.credits_remaining,
            "tier": u.subscription_tier,
            "is_premium": is_premium,
            "is_banned": u.is_banned,
            "xp": u.xp
        })
        
    return {
        "users": user_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.post("/users/{user_id}/ban")
async def ban_user(user_id: str, db: Session = Depends(get_db)):
    """
    Ban a user.
    """
    user_repo = UserRepository(db)
    # Check if UUID
    try:
        user = user_repo.get_profile(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_banned = True
        user.is_active = False # Deactivate
        db.commit()
        
        return {"status": "success", "message": f"User {user_id} has been banned."}
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/{user_id}/unban")
async def unban_user(user_id: str, db: Session = Depends(get_db)):
    """
    Unban a user.
    """
    user_repo = UserRepository(db)
    try:
        user = user_repo.get_profile(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_banned = False
        user.is_active = True
        db.commit()
        
        return {"status": "success", "message": f"User {user_id} has been unbanned."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/{user_id}/grant-premium")
async def grant_premium(user_id: str, db: Session = Depends(get_db)):
    """
    Manually grant premium status to a user.
    """
    user_repo = UserRepository(db)
    try:
        # user_id should be UUID of UserProfile
        updated_user = user_repo.update_subscription(user_id, SubscriptionTier.PREMIUM)
        if not updated_user:
             raise HTTPException(status_code=404, detail="User not found")
             
        return {"status": "success", "message": "Premium granted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/{user_id}/add-credits")
async def add_credits(
    user_id: str, 
    amount: int = Body(..., embed=True), 
    db: Session = Depends(get_db)
):
    """
    Manually add credits to a user.
    """
    user_repo = UserRepository(db)
    try:
        # consume_credits with negative amount adds credits
        user_repo.consume_credits(user_id, -amount)
        return {"status": "success", "message": f"{amount} credits added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
