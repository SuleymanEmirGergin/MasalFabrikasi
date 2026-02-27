from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.shop_service import ShopService

router = APIRouter()
shop_service = ShopService()

class PurchaseRequest(BaseModel):
    user_id: str
    item_id: str
    current_credits: int

class EquipRequest(BaseModel):
    user_id: str
    item_id: str

class UnequipRequest(BaseModel):
    user_id: str
    category: str

@router.get("/items", response_model=List[Dict])
async def get_shop_items():
    """
    Mağazadaki tüm eşyaları listeler.
    """
    return shop_service.get_shop_items()

@router.get("/inventory/{user_id}", response_model=Dict)
async def get_user_inventory(user_id: str):
    """
    Kullanıcının envanterini getirir.
    """
    return shop_service.get_user_inventory(user_id)

@router.post("/purchase")
async def purchase_item(request: PurchaseRequest):
    """
    Eşya satın alır.
    """
    try:
        result = shop_service.purchase_item(request.user_id, request.item_id, request.current_credits)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/equip")
async def equip_item(request: EquipRequest):
    """
    Eşyayı donatır (Avatar'a giyer).
    """
    try:
        result = shop_service.equip_item(request.user_id, request.item_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/unequip")
async def unequip_item(request: UnequipRequest):
    """
    Kategori eşyasını çıkarır.
    """
    try:
        result = shop_service.unequip_item(request.user_id, request.category)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
