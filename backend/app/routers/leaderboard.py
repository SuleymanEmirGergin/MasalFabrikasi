from fastapi import APIRouter, HTTPException, Query
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()
leaderboard_service = LeaderboardService()


@router.get("/leaderboard/stories")
async def get_stories_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """
    Hikâye sayısına göre liderlik tablosu.
    """
    try:
        leaderboard = leaderboard_service.get_stories_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liderlik tablosu yüklenirken hata oluştu: {str(e)}")


@router.get("/leaderboard/likes")
async def get_likes_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """
    Beğeni sayısına göre liderlik tablosu.
    """
    try:
        leaderboard = leaderboard_service.get_likes_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liderlik tablosu yüklenirken hata oluştu: {str(e)}")


@router.get("/leaderboard/xp")
async def get_xp_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """
    XP'ye göre liderlik tablosu.
    """
    try:
        leaderboard = leaderboard_service.get_xp_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liderlik tablosu yüklenirken hata oluştu: {str(e)}")

