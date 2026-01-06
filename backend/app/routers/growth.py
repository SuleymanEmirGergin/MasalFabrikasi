from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Waitlist, UserProfile
from pydantic import EmailStr, BaseModel
from typing import Optional
import uuid
import random
import string

router = APIRouter(prefix="/api/growth", tags=["Growth & Referrals"])

class WaitlistCreate(BaseModel):
    email: EmailStr
    source: Optional[str] = "landing_page"

@router.post("/waitlist", status_code=status.HTTP_201_CREATED)
async def join_waitlist(data: WaitlistCreate, db: Session = Depends(get_db)):
    """Landing page'den gelen abonelikleri kaydeder."""
    existing = db.query(Waitlist).filter(Waitlist.email == data.email).first()
    if existing:
        return {"message": "Zaten listedesin!", "email": data.email}
    
    new_entry = Waitlist(
        email=data.email,
        source=data.source
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {"message": "Başarıyla eklendi!", "id": str(new_entry.id)}

@router.post("/referral/generate")
async def generate_referral_code(user_auth_id: str, db: Session = Depends(get_db)):
    """Kullanıcı için benzersiz bir referans kodu oluşturur."""
    profile = db.query(UserProfile).filter(UserProfile.auth_user_id == user_auth_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı profili bulunamadı")
    
    if profile.referral_code:
        return {"referral_code": profile.referral_code}
    
    # Basit ama benzersiz kod üretimi
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Çakışma kontrolü
    while db.query(UserProfile).filter(UserProfile.referral_code == code).first():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
    profile.referral_code = code
    db.commit()
    return {"referral_code": code}

@router.get("/referral/stats")
async def get_referral_stats(user_auth_id: str, db: Session = Depends(get_db)):
    """Kullanıcının referans istatistiklerini getirir."""
    profile = db.query(UserProfile).filter(UserProfile.auth_user_id == user_auth_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı profili bulunamadı")
    
    if not profile.referral_code:
        return {"referrals_count": 0, "referral_code": None}
    
    count = db.query(UserProfile).filter(UserProfile.referred_by == profile.referral_code).count()
    return {
        "referral_code": profile.referral_code,
        "referrals_count": count,
        "reward_credits": count * 5  # Her referans için 5 kredi (örnek)
    }
