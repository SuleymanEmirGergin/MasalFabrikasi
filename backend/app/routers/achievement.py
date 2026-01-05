from fastapi import APIRouter, HTTPException
from app.services.achievement_service import AchievementService

router = APIRouter()
achievement_service = AchievementService()


@router.get("/achievements")
async def get_all_achievements():
    """
    Tüm başarıları getirir.
    """
    try:
        achievements = achievement_service.get_all_achievements()
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Başarılar yüklenirken hata oluştu: {str(e)}")


@router.get("/user/{user_id}/achievements")
async def get_user_achievements(user_id: str):
    """
    Kullanıcı başarılarını getirir.
    """
    try:
        achievements = achievement_service.get_user_achievements(user_id)
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı başarıları yüklenirken hata oluştu: {str(e)}")


@router.post("/achievements/{achievement_id}/unlock")
async def unlock_achievement(achievement_id: str, user_id: str):
    """
    Başarıyı açar.
    """
    try:
        achievement = achievement_service.unlock_achievement(user_id, achievement_id)
        if not achievement:
            raise HTTPException(status_code=404, detail="Başarı bulunamadı")
        return achievement
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Başarı açılırken hata oluştu: {str(e)}")

