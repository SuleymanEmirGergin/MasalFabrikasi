from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from app.services.market_service import MarketService

router = APIRouter()
market_service = MarketService()

class BalanceResponse(BaseModel):
    credits: int
    is_premium: bool

class PurchaseRequest(BaseModel):
    user_id: str
    amount: int
    item_name: str

class PurchaseResponse(BaseModel):
    success: bool
    new_balance: int
    message: str

class CreditPackage(BaseModel):
    id: str
    name: str
    credits: int
    price_try: float

@router.get("/balance/{user_id}", response_model=BalanceResponse)
async def get_balance(user_id: str):
    """
    Kullanıcının kredi bakiyesini ve premium durumunu getirir.
    """
    credits = await market_service.get_user_balance(user_id)
    is_premium = await market_service.get_user_premium_status(user_id)
    return {"credits": credits, "is_premium": is_premium}

@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_item(request: PurchaseRequest):
    """
    Kredi harcayarak bir ürün/hizmet satın alma işlemi.
    """
    success = await market_service.spend_credits(request.user_id, request.amount, request.item_name)
    new_balance = await market_service.get_user_balance(request.user_id)
    
    if success:
        return {"success": True, "new_balance": new_balance, "message": "Satın alma başarılı."}
    else:
        return {"success": False, "new_balance": new_balance, "message": "Yetersiz bakiye."}

@router.post("/add-credits", response_model=BalanceResponse)
async def add_credits_mock(user_id: str, amount: int):
    """
    (Demo için) Kullanıcıya kredi yükler. Gerçekte Ödeme Yöntemi entegrasyonu olur.
    """
    new_credits = await market_service.add_credits(user_id, amount)
    is_premium = await market_service.get_user_premium_status(user_id)
    return {"credits": new_credits, "is_premium": is_premium}

@router.get("/packages", response_model=List[CreditPackage])
async def get_credit_packages():
    """
    Satın alınabilir kredi paketlerini listeler.
    """
    return [
        {"id": "starter", "name": "Başlangıç Paketi", "credits": 50, "price_try": 29.99},
        {"id": "storyteller", "name": "Masalcı Paketi", "credits": 150, "price_try": 69.99},
        {"id": "legend", "name": "Efsane Paketi", "credits": 500, "price_try": 199.99}
    ]

@router.post("/premium/upgrade", response_model=PurchaseResponse)
async def upgrade_premium(user_id: str):
    """
    Premium üyeliğe yükselt. 100 Kredi düşer.
    """
    success = await market_service.upgrade_to_premium(user_id)
    new_balance = await market_service.get_user_balance(user_id)
    
    if success:
         return {"success": True, "new_balance": new_balance, "message": "Premium üyeliğe geçildi!"}
    else:
         return {"success": False, "new_balance": new_balance, "message": "Yetersiz bakiye (100 Kredi gerekli)."}
