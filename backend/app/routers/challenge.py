from fastapi import APIRouter, HTTPException, Query
from app.services.challenge_service import ChallengeService

router = APIRouter()
challenge_service = ChallengeService()


@router.get("/challenges/daily")
async def get_daily_challenges():
    """
    Günlük görevleri getirir.
    """
    try:
        challenges = challenge_service.get_daily_challenges()
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Günlük görevler yüklenirken hata oluştu: {str(e)}")


@router.get("/challenges/weekly")
async def get_weekly_challenges():
    """
    Haftalık mücadeleleri getirir.
    """
    try:
        challenges = challenge_service.get_weekly_challenges()
        return {"challenges": challenges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Haftalık mücadeleler yüklenirken hata oluştu: {str(e)}")


@router.post("/challenges/{challenge_id}/complete")
async def complete_challenge(challenge_id: str, user_id: str = Query(...)):
    """
    Görevi tamamlar.
    """
    try:
        result = challenge_service.complete_challenge(user_id, challenge_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev tamamlanırken hata oluştu: {str(e)}")


@router.get("/challenges/{challenge_id}/progress")
async def get_challenge_progress(challenge_id: str, user_id: str = Query(...)):
    """
    Görev ilerlemesini getirir.
    """
    try:
        progress = challenge_service.get_user_challenge_progress(user_id, challenge_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev ilerlemesi yüklenirken hata oluştu: {str(e)}")

