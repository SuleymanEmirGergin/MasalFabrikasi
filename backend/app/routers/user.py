from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.services.user_service import UserService
from app.services.follow_service import FollowService
from app.core.auth_dependencies import get_current_user

router = APIRouter()
user_service = UserService()
follow_service = FollowService()

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Supabase üzerinden mevcut kullanıcı bilgisini döndürür.
    """
    return current_user


class UserRegisterRequest(BaseModel):
    device_id: str
    name: Optional[str] = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


@router.post("/users/register")
async def register_user(request: UserRegisterRequest):
    """
    Kullanıcı kaydı oluşturur veya mevcut kullanıcıyı getirir.
    """
    try:
        user = user_service.register_user(request.device_id, request.name)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı kaydı oluşturulurken hata oluştu: {str(e)}")


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """
    Kullanıcı profilini getirir.
    """
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı yüklenirken hata oluştu: {str(e)}")


@router.get("/users/device/{device_id}")
async def get_user_by_device(device_id: str):
    """
    Device ID'ye göre kullanıcıyı getirir.
    """
    try:
        user = user_service.get_user_by_device_id(device_id)
        if not user:
            # Kullanıcı yoksa otomatik kaydet
            user = user_service.register_user(device_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı yüklenirken hata oluştu: {str(e)}")


@router.put("/users/{user_id}")
async def update_user(user_id: str, request: UserUpdateRequest):
    """
    Kullanıcı profilini günceller.
    """
    try:
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.avatar is not None:
            updates['avatar'] = request.avatar
        if request.bio is not None:
            updates['bio'] = request.bio
        
        user = user_service.update_user(user_id, updates)
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı güncellenirken hata oluştu: {str(e)}")


@router.get("/users/{user_id}/statistics")
async def get_user_statistics(user_id: str):
    """
    Kullanıcı istatistiklerini getirir.
    """
    try:
        stats = user_service.get_user_statistics(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistikler yüklenirken hata oluştu: {str(e)}")


@router.post("/users/{user_id}/follow")
async def follow_user(user_id: str, follower_id: str = Query(...)):
    """
    Kullanıcıyı takip eder veya takipten çıkarır.
    """
    try:
        result = follow_service.follow_user(follower_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Takip işlemi sırasında hata oluştu: {str(e)}")


@router.delete("/users/{user_id}/follow")
async def unfollow_user(user_id: str, follower_id: str = Query(...)):
    """
    Kullanıcıyı takipten çıkarır.
    """
    try:
        result = follow_service.follow_user(follower_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Takipten çıkma işlemi sırasında hata oluştu: {str(e)}")


@router.get("/users/{user_id}/followers")
async def get_followers(user_id: str):
    """
    Kullanıcının takipçilerini getirir.
    """
    try:
        followers = follow_service.get_followers(user_id)
        return {"followers": followers, "count": len(followers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Takipçiler yüklenirken hata oluştu: {str(e)}")


@router.get("/users/{user_id}/following")
async def get_following(user_id: str):
    """
    Kullanıcının takip ettiklerini getirir.
    """
    try:
        following = follow_service.get_following(user_id)
        return {"following": following, "count": len(following)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Takip edilenler yüklenirken hata oluştu: {str(e)}")


@router.get("/user/{user_id}/level")
async def get_user_level(user_id: str):
    """
    Kullanıcı seviyesini getirir.
    """
    try:
        xp_info = user_service.get_user_xp(user_id)
        return xp_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seviye bilgisi yüklenirken hata oluştu: {str(e)}")


@router.get("/user/{user_id}/xp")
async def get_user_xp(user_id: str):
    """
    Kullanıcı XP bilgisini getirir.
    """
    try:
        xp_info = user_service.get_user_xp(user_id)
        return xp_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XP bilgisi yüklenirken hata oluştu: {str(e)}")


@router.post("/user/{user_id}/add-xp")
async def add_xp(user_id: str, xp_amount: int):
    """
    Kullanıcıya XP ekler.
    """
    try:
        result = user_service.add_xp(user_id, xp_amount)
        if not result:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XP eklenirken hata oluştu: {str(e)}")


@router.get("/user/{user_id}/streak")
async def get_streak(user_id: str):
    """
    Kullanıcının streak bilgisini getirir.
    """
    try:
        streak_info = user_service.get_streak(user_id)
        return streak_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streak bilgisi yüklenirken hata oluştu: {str(e)}")


@router.post("/user/{user_id}/activity")
async def record_activity(user_id: str):
    """
    Günlük aktiviteyi kaydeder.
    """
    try:
        result = user_service.record_activity(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aktivite kaydedilirken hata oluştu: {str(e)}")

