from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import UserProfile
from app.repositories.user_repository import get_user_repository
from pydantic import BaseModel
import shortuuid

router = APIRouter()

class RedeemRequest(BaseModel):
    user_id: str
    referral_code: str

@router.post("/redeem")
async def redeem_referral_code(
    request: RedeemRequest,
    db: Session = Depends(get_db)
):
    """
    Kullanıcının bir referans kodunu kullanmasını ve ödül kazanmasını sağlar.
    Hem davet eden hem de davet edilen kazanır.
    """
    user_repo = get_user_repository(db)
    
    # 1. Mevcut kullanıcıyı bul
    user = user_repo.get_user(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    if user.get("referred_by"):
        raise HTTPException(status_code=400, detail="Zaten bir referans kodu kullandınız.")
        
    # 2. Referans kodunun sahibini bul
    referrer = db.query(UserProfile).filter(UserProfile.referral_code == request.referral_code).first()
    
    if not referrer:
        raise HTTPException(status_code=404, detail="Geçersiz referans kodu")
        
    if str(referrer.id) == request.user_id:
        raise HTTPException(status_code=400, detail="Kendi kodunuzu kullanamazsınız.")
    
    # 3. Ödül Dağıtımı (Her iki tarafa da 50 kredi)
    REWARD_AMOUNT = 50
    
    # Davet edilen
    user_repo.update_user(request.user_id, {
        "credits": user["credits"] + REWARD_AMOUNT,
        "referred_by": request.referral_code
    })
    
    # Davet eden
    referrer.credits += REWARD_AMOUNT
    db.commit()
    
    return {
        "status": "success",
        "message": f"Tebrikler! {REWARD_AMOUNT} Kredi kazandınız.",
        "new_balance": user["credits"] + REWARD_AMOUNT
    }

@router.post("/{user_id}/generate")
async def generate_code(user_id: str, db: Session = Depends(get_db)):
    """
    Kullanıcı için benzersiz referans kodu oluşturur (Eğer yoksa).
    """
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
    if not user.referral_code:
        # Create a short unique code e.g., 'MSL-X7Z2'
        code = "MSL-" + shortuuid.ShortUUID().random(length=5).upper()
        user.referral_code = code
        db.commit()
        db.refresh(user)
        
    return {"referral_code": user.referral_code}
