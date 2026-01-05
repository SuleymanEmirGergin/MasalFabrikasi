from fastapi import APIRouter, Body
from app.services.atmosphere_service import atmosphere_service

router = APIRouter()

@router.post("/analyze")
async def analyze_atmosphere(text: str = Body(..., embed=True)):
    """
    Get lighting configuration for a text segment.
    """
    return await atmosphere_service.analyze_mood(text)
